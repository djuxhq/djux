import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from djux.core.downloader import download_and_extract
from djux.core.manifest import InvalidManifestError, parse_manifest
from djux.core.patcher import (
    patch_installed_apps,
    patch_settings_block,
    patch_urls,
)
from djux.core.registry import REGISTRY_URL, fetch_registry, get_app

console = Console()


def _find_project_root() -> Path | None:
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "djux.project.json").exists():
            return parent
    return None


def _read_project_json(root: Path) -> dict:
    return json.loads((root / "djux.project.json").read_text(encoding="utf-8"))


def _write_project_json(root: Path, data: dict) -> None:
    (root / "djux.project.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def _project_python(root: Path) -> str:
    """Resolve the Python interpreter belonging to the target project.

    djux is commonly installed before the project's own virtualenv exists
    (see README quick start), so `sys.executable` here is djux's own
    interpreter, not the project's. Prefer a .venv/ in the project root
    (the project's own environment, regardless of what's active in the
    current shell), then the active virtualenv via $VIRTUAL_ENV as a
    fallback for projects using a differently-located venv, and only then
    sys.executable.
    """
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    exe_name = "python.exe" if os.name == "nt" else "python"

    candidates = [root / ".venv"]
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        candidates.append(Path(virtual_env))

    for venv_path in candidates:
        python_path = venv_path / bin_dir / exe_name
        if python_path.exists():
            return str(python_path)

    return sys.executable


@click.command()
@click.argument("app_name")
@click.option("--registry", "registry_url", default=REGISTRY_URL, help="Custom registry URL.")
def add(app_name: str, registry_url: str):
    """Download and install a djux app into the current project."""

    # 1. Find project root
    root = _find_project_root()
    if root is None:
        console.print("✗ No djux project found. Run this inside a djx project.")
        raise SystemExit(1)

    # 2. Check if already installed
    project_data = _read_project_json(root)
    if app_name in project_data.get("installed_apps", []):
        console.print(f"⚠  App '[bold]{app_name}[/bold]' is already installed.")
        raise SystemExit(0)

    # 3. Fetch registry
    with console.status("Fetching registry..."):
        try:
            registry = fetch_registry(registry_url)
        except RuntimeError as e:
            console.print(f"✗ {e}")
            raise SystemExit(1)

    app_entry = get_app(registry, app_name)
    if app_entry is None:
        console.print(
            f"✗ App '[bold]{app_name}[/bold]' not found in registry.\n"
            "  Run [cyan]djux list[/cyan] to see available apps."
        )
        raise SystemExit(1)

    console.print(f"✓ Found [bold]{app_name}[/bold] v{app_entry.get('version', '?')}")

    # 4-5. Download and extract
    with console.status("Downloading..."):
        try:
            extracted = download_and_extract(app_entry["download"], app_name)
        except Exception as e:
            console.print(f"✗ Download failed: {e}")
            raise SystemExit(1)

    console.print("✓ Downloaded")

    # 6. Validate manifest
    try:
        manifest = parse_manifest(extracted)
    except InvalidManifestError as e:
        console.print(f"✗ {e}")
        raise SystemExit(1)

    # 7. Check required apps
    requires = manifest.get("requires_apps", [])
    installed = project_data.get("installed_apps", [])
    for dep in requires:
        if dep not in installed:
            console.print(
                f"✗ App '[bold]{app_name}[/bold]' requires "
                f"'[bold]{dep}[/bold]' to be installed first.\n"
                f"  Run: [cyan]djux add {dep}[/cyan]"
            )
            raise SystemExit(1)

    # 8. Copy app code
    app_src = extracted / "app"
    if not app_src.exists():
        console.print("✗ App package is missing the 'app/' directory.")
        raise SystemExit(1)

    install_name = app_name
    app_dest = root / "apps" / install_name

    if app_dest.exists():
        console.print(
            f"\n[yellow]Warning:[/yellow] Directory 'apps/{install_name}' already exists."
        )
        while True:
            new_name = click.prompt(
                "  Enter a new name to install as (or leave empty to cancel)",
                default="",
                show_default=False,
            ).strip()

            if not new_name:
                console.print("Cancelled.")
                raise SystemExit(0)

            import re as _re
            if not _re.match(r"^[a-z][a-z0-9_]*$", new_name):
                console.print(
                    "  [red]Invalid name.[/red] Use lowercase letters, digits, and underscores only."
                )
                continue

            app_dest = root / "apps" / new_name
            if app_dest.exists():
                console.print(f"  [red]Directory 'apps/{new_name}' also exists.[/red] Try another name.")
                continue

            install_name = new_name
            console.print(f"  Installing as '[bold]{install_name}[/bold]'")
            break

    shutil.copytree(app_src, app_dest)
    console.print(f"✓ App files copied to apps/{install_name}/")

    # 9. Patch settings.py
    settings_path = root / "config" / "settings.py"
    patch_installed_apps(settings_path, manifest["installed_apps"])

    settings_patch = manifest.get("settings_patch")
    if settings_patch:
        patch_settings_block(settings_path, settings_patch)

    console.print("✓ settings.py updated")

    # 10. Patch urls.py — use install_name so the URL include matches the folder
    urls_path = root / "config" / "urls.py"
    patch_urls(urls_path, install_name, manifest["url_prefix"])
    console.print("✓ urls.py updated")

    # 11. Install pip dependencies
    python_exe = _project_python(root)
    deps = manifest.get("dependencies", [])
    if deps:
        with console.status("Installing dependencies..."):
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", *deps],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(f"✗ pip install failed:\n{result.stderr}")
                raise SystemExit(1)
        console.print("✓ Dependencies installed")

    # 12. Run migrations
    if manifest.get("migrations", False):
        with console.status("Running migrations..."):
            result = subprocess.run(
                [python_exe, "manage.py", "migrate"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(f"✗ migrate failed:\n{result.stderr}")
                raise SystemExit(1)
        console.print("✓ Migrations applied")

    # 13. Update djux.project.json
    project_data.setdefault("installed_apps", []).append(install_name)
    _write_project_json(root, project_data)

    # 14. Print success
    label = f"{app_name}" if install_name == app_name else f"{app_name} (as '{install_name}')"
    console.print(f"\n[green]✓ {label} added successfully![/green]")

    env_vars = manifest.get("env_vars", [])
    if env_vars:
        console.print("\nRequired environment variables:")
        for var in env_vars:
            console.print(f"  • [yellow]{var}[/yellow]")

    notes = manifest.get("notes")
    if notes:
        console.print(f"\nNotes: {notes}")

import json
import shutil
from pathlib import Path

import click
from rich.console import Console

from djux.core.patcher import unpatch_installed_apps, unpatch_settings_block, unpatch_urls
from djux.core.manifest import parse_manifest, InvalidManifestError

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


@click.command()
@click.argument("app_name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def remove(app_name: str, yes: bool):
    """Remove an installed djux app from the current project."""

    # 1. Find project root
    root = _find_project_root()
    if root is None:
        console.print("✗ No djux project found. Run this inside a djx project.")
        raise SystemExit(1)

    # 2. Check app directory exists
    app_dir = root / "apps" / app_name
    if not app_dir.exists():
        console.print(
            f"✗ App '[bold]{app_name}[/bold]' is not installed "
            f"(no directory at apps/{app_name}/)."
        )
        raise SystemExit(1)

    # 3. Confirm
    if not yes:
        click.confirm(
            f"Remove '{app_name}' and all its files?", abort=True
        )

    # Read manifest before deleting so we know what to unpatch
    manifest = None
    try:
        manifest = parse_manifest(app_dir.parent / app_name)
    except (InvalidManifestError, FileNotFoundError):
        pass

    # 4. Delete app directory
    shutil.rmtree(app_dir)

    # 5. Unpatch settings.py
    settings_path = root / "config" / "settings.py"
    if manifest:
        unpatch_installed_apps(settings_path, manifest["installed_apps"])
        settings_patch = manifest.get("settings_patch")
        if settings_patch:
            unpatch_settings_block(settings_path, settings_patch)
    console.print("✓ settings.py updated")

    # 6. Unpatch urls.py
    urls_path = root / "config" / "urls.py"
    unpatch_urls(urls_path, app_name)
    console.print("✓ urls.py updated")

    # 7. Update djux.project.json
    project_data = _read_project_json(root)
    project_data["installed_apps"] = [
        a for a in project_data.get("installed_apps", []) if a != app_name
    ]
    _write_project_json(root, project_data)

    console.print(f"\n[green]✓ {app_name} removed.[/green]")
    console.print(
        "\n[yellow]Note:[/yellow] If this app had database models, run "
        "[cyan]python manage.py migrate[/cyan] to clean up the database."
    )

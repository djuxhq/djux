from pathlib import Path

import click
from rich.console import Console

from djux.core.manifest import InvalidManifestError, parse_manifest

console = Console()

REGISTRY_PR_URL = "https://github.com/browndevv/djx-registry/compare"


@click.command()
def publish():
    """Validate your app and generate a registry PR template."""
    cwd = Path.cwd()

    # Validate manifest
    try:
        manifest = parse_manifest(cwd)
    except InvalidManifestError as e:
        console.print(f"✗ {e}")
        raise SystemExit(1)

    # Validate app/ directory
    app_dir = cwd / "app"
    if not app_dir.exists():
        console.print("✗ Missing 'app/' directory.")
        raise SystemExit(1)

    required_files = ["__init__.py", "apps.py", "models.py", "views.py", "urls.py"]
    missing = [f for f in required_files if not (app_dir / f).exists()]
    if missing:
        console.print(f"✗ Missing required files in app/: {', '.join(missing)}")
        raise SystemExit(1)

    # README check
    if not (cwd / "README.md").exists():
        console.print("✗ Missing README.md — required for registry submission.")
        raise SystemExit(1)

    console.print(f"[green]✓ Manifest valid[/green] — {manifest['name']} v{manifest['version']}")
    console.print("[green]✓ app/ directory looks good[/green]")
    console.print("[green]✓ README.md found[/green]")

    console.print(
        f"\n[bold]Your app is ready to submit![/bold]\n\n"
        f"1. Push your app to a public GitHub repo\n"
        f"2. Open a PR to the djx registry:\n"
        f"   [cyan]{REGISTRY_PR_URL}[/cyan]\n\n"
        f"PR body template:\n"
        f"---\n"
        f"## New app: {manifest['name']}\n\n"
        f"- **Repo:** <your-repo-url>\n"
        f"- **Version:** {manifest['version']}\n"
        f"- **Description:** {manifest['description']}\n"
        f"- **Author:** {manifest.get('author', '<your-name>')}\n\n"
        f"Checklist:\n"
        f"- [ ] App repo is public\n"
        f"- [ ] djx.json is valid (verified by djux publish)\n"
        f"- [ ] README.md exists\n"
        f"- [ ] At least one passing test\n"
        f"---"
    )

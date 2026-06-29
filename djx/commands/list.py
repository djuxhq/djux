import click
from rich.console import Console
from rich.table import Table

from djx.core.registry import REGISTRY_URL, fetch_registry

console = Console()


@click.command()
@click.option("--registry", "registry_url", default=REGISTRY_URL, help="Custom registry URL.")
@click.option("--refresh", is_flag=True, help="Bypass cache and fetch fresh registry.")
def list_apps(registry_url: str, refresh: bool):
    """Show all apps available in the djx registry."""
    with console.status("Fetching registry..."):
        try:
            registry = fetch_registry(registry_url, force_refresh=refresh)
        except RuntimeError as e:
            console.print(f"✗ {e}")
            raise SystemExit(1)

    apps = registry.get("apps", {})
    if not apps:
        console.print("No apps found in registry.")
        return

    table = Table(title="Available djx Apps", border_style="blue")
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Description")
    table.add_column("Tags", style="dim")

    for name, info in apps.items():
        tags = ", ".join(info.get("tags", []))
        official = " [yellow]★[/yellow]" if info.get("official") else ""
        table.add_row(
            f"{name}{official}",
            info.get("version", "?"),
            info.get("description", ""),
            tags,
        )

    console.print(table)
    console.print("\n  Install any app:  [bold cyan]djx add <name>[/bold cyan]")
    console.print("  [yellow]★[/yellow] = official djx app")

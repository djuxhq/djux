import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "project_template"


def _replace_in_file(path: Path, project_name: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("{{project_name}}", project_name), encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        pass  # skip binary files


@click.command()
@click.argument("project_name")
def new(project_name: str):
    """Scaffold a new djux Django project."""
    target = Path.cwd() / project_name

    if target.exists():
        console.print(f"✗ Directory '[bold]{project_name}[/bold]' already exists.")
        raise SystemExit(1)

    console.print(f"Creating project: [bold]{project_name}[/bold]\n")

    shutil.copytree(TEMPLATE_DIR, target)

    for file_path in target.rglob("*"):
        if file_path.is_file():
            _replace_in_file(file_path, project_name)

    panel_content = (
        f"[green]✓[/green] Project created: [bold]{project_name}/[/bold]\n\n"
        f"  [cyan]cd {project_name}[/cyan]\n"
        f"  [cyan]python -m venv .venv[/cyan]\n"
        f"  [cyan]source .venv/bin/activate[/cyan]  [dim]# Windows: .venv\\Scripts\\activate[/dim]\n"
        f"  [cyan]pip install -r requirements.txt[/cyan]\n"
        f"  [cyan]cp .env.example .env[/cyan]\n"
        f"  [cyan]python manage.py migrate[/cyan]\n"
        f"  [cyan]python manage.py runserver[/cyan]\n\n"
        f"  Then add apps:  [bold cyan]djux add auth[/bold cyan]"
    )

    console.print(Panel(panel_content, title="Ready", border_style="green"))

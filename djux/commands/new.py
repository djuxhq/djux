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
@click.argument(
    "directory",
    required=False,
    type=click.Path(file_okay=False, path_type=Path),
)
def new(project_name: str, directory: Path | None):
    """Scaffold a new djux Django project.

    DIRECTORY is optional, like `django-admin startproject name
    [directory]`: when given, the project is created inside DIRECTORY
    instead of a new PROJECT_NAME folder in the current directory.
    """
    if directory is not None:
        target = directory if directory.is_absolute() else Path.cwd() / directory
        if target.exists() and any(target.iterdir()):
            console.print(f"✗ Directory '[bold]{directory}[/bold]' already exists and is not empty.")
            raise SystemExit(1)
    else:
        target = Path.cwd() / project_name
        if target.exists():
            console.print(f"✗ Directory '[bold]{project_name}[/bold]' already exists.")
            raise SystemExit(1)

    console.print(f"Creating project: [bold]{project_name}[/bold]\n")

    shutil.copytree(TEMPLATE_DIR, target, dirs_exist_ok=True)

    for file_path in target.rglob("*"):
        if file_path.is_file():
            _replace_in_file(file_path, project_name)

    cd_target = directory if directory is not None else project_name
    panel_content = (
        f"[green]✓[/green] Project created: [bold]{target}/[/bold]\n\n"
        f"  [cyan]cd {cd_target}[/cyan]\n"
        f"  [cyan]pip install -r requirements.txt[/cyan]\n"
        f"  [cyan]cp .env.example .env[/cyan]\n"
        f"  [cyan]python manage.py migrate[/cyan]\n"
        f"  [cyan]python manage.py runserver[/cyan]\n\n"
        f"  Then add apps:  [bold cyan]djux add auth[/bold cyan]"
    )

    console.print(Panel(panel_content, title="Ready", border_style="green"))

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from djux.commands.add import _project_python, add

FIXTURES_DIR = Path(__file__).parent / "fixtures"


MOCK_REGISTRY = {
    "version": "1",
    "apps": {
        "testapp": {
            "version": "0.1.0",
            "description": "A test app",
            "tags": ["test"],
            "author": "tester",
            "official": False,
            "repo": "https://github.com/example/testapp",
            "download": "https://github.com/example/testapp/archive/main.zip",
        }
    },
}

MOCK_MANIFEST = {
    "name": "testapp",
    "version": "0.1.0",
    "description": "A test app",
    "installed_apps": ["testapp"],
    "url_prefix": "api/testapp/",
    "dependencies": [],
    "migrations": False,
}


def _make_djx_project(root: Path) -> None:
    """Create a minimal djx project structure for testing."""
    config = root / "config"
    config.mkdir()

    settings = config / "settings.py"
    settings.write_text(
        "INSTALLED_APPS = [\n"
        '    "django.contrib.auth",\n'
        "    # djux:installed_apps\n"
        "]\n\n"
        "# djux:settings\n"
    )

    urls = config / "urls.py"
    urls.write_text(
        "from django.contrib import admin\n"
        "from django.urls import path, include\n\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "    # djux:urls\n"
        "]\n"
    )

    (root / "apps").mkdir()

    (root / "djux.project.json").write_text(
        json.dumps({"djux_version": "0.1.0", "project": "myproject", "installed_apps": []})
    )


def _make_app_zip(tmp_path: Path) -> Path:
    """Create a zip file mimicking a GitHub archive of a djx app."""
    app_src = tmp_path / "build" / "testapp-main"
    app_src.mkdir(parents=True)

    (app_src / "djux.json").write_text(json.dumps(MOCK_MANIFEST))

    app_code = app_src / "app"
    app_code.mkdir()
    (app_code / "__init__.py").write_text("")
    (app_code / "apps.py").write_text("")
    (app_code / "models.py").write_text("")
    (app_code / "views.py").write_text("")
    (app_code / "urls.py").write_text("")

    zip_path = tmp_path / "testapp.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in app_src.rglob("*"):
            zf.write(file, file.relative_to(tmp_path / "build"))

    return zip_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def djx_project(tmp_path, monkeypatch):
    _make_djx_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_add_full_flow(runner, djx_project, tmp_path):
    zip_path = _make_app_zip(tmp_path)

    with (
        patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY),
        patch("djux.commands.add.download_and_extract") as mock_dl,
    ):
        mock_dl.return_value = tmp_path / "build" / "testapp-main"
        result = runner.invoke(add, ["testapp"])

    assert result.exit_code == 0, result.output
    assert (djx_project / "apps" / "testapp").exists()


def test_add_updates_project_json(runner, djx_project, tmp_path):
    with (
        patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY),
        patch("djux.commands.add.download_and_extract") as mock_dl,
    ):
        mock_dl.return_value = tmp_path / "build" / "testapp-main"
        _make_app_zip(tmp_path)  # creates the build dir
        runner.invoke(add, ["testapp"])

    data = json.loads((djx_project / "djux.project.json").read_text())
    assert "testapp" in data["installed_apps"]


def test_add_fails_outside_djx_project(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(add, ["testapp"])
    assert result.exit_code != 0
    assert "No djux project found" in result.output


def test_add_fails_when_app_not_in_registry(runner, djx_project):
    with patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY):
        result = runner.invoke(add, ["nonexistent"])
    assert result.exit_code != 0
    assert "not found in registry" in result.output


def test_add_fails_when_manifest_missing_fields(runner, djx_project, tmp_path):
    bad_manifest = {"name": "testapp"}  # missing required fields
    app_dir = tmp_path / "build" / "testapp-main"
    app_dir.mkdir(parents=True)
    (app_dir / "djux.json").write_text(json.dumps(bad_manifest))
    (app_dir / "app").mkdir()

    with (
        patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY),
        patch("djux.commands.add.download_and_extract", return_value=app_dir),
    ):
        result = runner.invoke(add, ["testapp"])

    assert result.exit_code != 0
    assert "missing required field" in result.output


def test_add_warns_if_already_installed(runner, djx_project):
    (djx_project / "djux.project.json").write_text(
        json.dumps(
            {"djux_version": "0.1.0", "project": "myproject", "installed_apps": ["testapp"]}
        )
    )
    with patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY):
        result = runner.invoke(add, ["testapp"])
    assert result.exit_code == 0
    assert "already installed" in result.output


def test_add_collision_prompts_for_new_name(runner, djx_project, tmp_path):
    _make_app_zip(tmp_path)
    # Pre-create the conflicting directory
    (djx_project / "apps" / "testapp").mkdir(parents=True)

    with (
        patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY),
        patch("djux.commands.add.download_and_extract") as mock_dl,
    ):
        mock_dl.return_value = tmp_path / "build" / "testapp-main"
        # User types "testapp2" when prompted
        result = runner.invoke(add, ["testapp"], input="testapp2\n")

    assert result.exit_code == 0, result.output
    assert (djx_project / "apps" / "testapp2").exists()
    data = json.loads((djx_project / "djux.project.json").read_text())
    assert "testapp2" in data["installed_apps"]


def test_project_python_falls_back_to_sys_executable(tmp_path, monkeypatch):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    assert _project_python(tmp_path) == sys.executable


def test_project_python_prefers_project_dot_venv(tmp_path, monkeypatch):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    exe_name = "python.exe" if os.name == "nt" else "python"
    venv_python = tmp_path / ".venv" / bin_dir / exe_name
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()

    assert _project_python(tmp_path) == str(venv_python)


def test_project_python_prefers_active_virtual_env(tmp_path, monkeypatch):
    active_venv = tmp_path / "active-venv"
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    exe_name = "python.exe" if os.name == "nt" else "python"
    venv_python = active_venv / bin_dir / exe_name
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()

    monkeypatch.setenv("VIRTUAL_ENV", str(active_venv))

    # Even though djux itself isn't running from this venv (sys.executable
    # differs), $VIRTUAL_ENV is inherited from the activating shell and
    # should be preferred over the project's own .venv/ or sys.executable.
    assert _project_python(tmp_path) == str(venv_python)


def test_add_collision_cancel_on_empty_input(runner, djx_project, tmp_path):
    _make_app_zip(tmp_path)
    (djx_project / "apps" / "testapp").mkdir(parents=True)

    with (
        patch("djux.commands.add.fetch_registry", return_value=MOCK_REGISTRY),
        patch("djux.commands.add.download_and_extract") as mock_dl,
    ):
        mock_dl.return_value = tmp_path / "build" / "testapp-main"
        # User presses Enter (empty) to cancel
        result = runner.invoke(add, ["testapp"], input="\n")

    assert result.exit_code == 0
    assert "Cancelled" in result.output

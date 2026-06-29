import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from djx.commands.new import new


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


def test_new_creates_directory_structure(runner):
    result = runner.invoke(new, ["myproject"])
    assert result.exit_code == 0

    root = Path.cwd() / "myproject"
    assert root.is_dir()
    assert (root / "config" / "settings.py").exists()
    assert (root / "config" / "urls.py").exists()
    assert (root / "config" / "wsgi.py").exists()
    assert (root / "config" / "asgi.py").exists()
    assert (root / "manage.py").exists()
    assert (root / "djx.project.json").exists()
    assert (root / "requirements.txt").exists()
    assert (root / ".env.example").exists()
    assert (root / ".gitignore").exists()
    assert (root / "apps").is_dir()
    assert (root / "templates").is_dir()
    assert (root / "static").is_dir()


def test_new_replaces_project_name_placeholder(runner):
    result = runner.invoke(new, ["myproject"])
    assert result.exit_code == 0

    root = Path.cwd() / "myproject"

    project_json = (root / "djx.project.json").read_text()
    assert "myproject" in project_json
    assert "{{project_name}}" not in project_json

    settings = (root / "config" / "settings.py").read_text()
    assert "{{project_name}}" not in settings


def test_new_fails_if_directory_exists(runner):
    (Path.cwd() / "myproject").mkdir()
    result = runner.invoke(new, ["myproject"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_new_project_json_has_correct_structure(runner):
    import json

    runner.invoke(new, ["myproject"])
    data = json.loads((Path.cwd() / "myproject" / "djx.project.json").read_text())
    assert data["project"] == "myproject"
    assert data["installed_apps"] == []
    assert "djx_version" in data

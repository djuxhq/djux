import shutil
from pathlib import Path

import pytest

from djux.core.patcher import (
    patch_installed_apps,
    patch_urls,
    unpatch_installed_apps,
    unpatch_urls,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def settings_file(tmp_path):
    src = FIXTURES_DIR / "sample_settings.py"
    dest = tmp_path / "settings.py"
    shutil.copy(src, dest)
    return dest


@pytest.fixture
def urls_file(tmp_path):
    src = FIXTURES_DIR / "sample_urls.py"
    dest = tmp_path / "urls.py"
    shutil.copy(src, dest)
    return dest


# --- patch_installed_apps ---

def test_patch_installed_apps_injects_app(settings_file):
    patch_installed_apps(settings_file, ["myapp"])
    text = settings_file.read_text()
    assert '"myapp"' in text


def test_patch_installed_apps_is_idempotent(settings_file):
    patch_installed_apps(settings_file, ["myapp"])
    patch_installed_apps(settings_file, ["myapp"])
    text = settings_file.read_text()
    assert text.count('"myapp"') == 1


def test_patch_installed_apps_multiple(settings_file):
    patch_installed_apps(settings_file, ["app_one", "app_two"])
    text = settings_file.read_text()
    assert '"app_one"' in text
    assert '"app_two"' in text


# --- unpatch_installed_apps ---

def test_unpatch_installed_apps_removes_app(settings_file):
    patch_installed_apps(settings_file, ["myapp"])
    unpatch_installed_apps(settings_file, ["myapp"])
    text = settings_file.read_text()
    assert '"myapp"' not in text


def test_unpatch_installed_apps_leaves_other_apps(settings_file):
    patch_installed_apps(settings_file, ["myapp", "otherapp"])
    unpatch_installed_apps(settings_file, ["myapp"])
    text = settings_file.read_text()
    assert '"myapp"' not in text
    assert '"otherapp"' in text


# --- patch_urls ---

def test_patch_urls_injects_url(urls_file):
    patch_urls(urls_file, "myapp", "api/myapp/")
    text = urls_file.read_text()
    assert 'include("myapp.urls")' in text
    assert '"api/myapp/"' in text


def test_patch_urls_is_idempotent(urls_file):
    patch_urls(urls_file, "myapp", "api/myapp/")
    patch_urls(urls_file, "myapp", "api/myapp/")
    text = urls_file.read_text()
    assert text.count('include("myapp.urls")') == 1


def test_patch_urls_adds_include_import_when_missing(tmp_path):
    urls_no_include = tmp_path / "urls.py"
    urls_no_include.write_text(
        "from django.contrib import admin\n"
        "from django.urls import path\n\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "    # djux:urls\n"
        "]\n"
    )
    patch_urls(urls_no_include, "myapp", "api/myapp/")
    text = urls_no_include.read_text()
    assert "include" in text


# --- unpatch_urls ---

def test_unpatch_urls_removes_url_line(urls_file):
    patch_urls(urls_file, "myapp", "api/myapp/")
    unpatch_urls(urls_file, "myapp")
    text = urls_file.read_text()
    assert 'include("myapp.urls")' not in text


def test_unpatch_urls_leaves_other_urls(urls_file):
    patch_urls(urls_file, "myapp", "api/myapp/")
    patch_urls(urls_file, "otherapp", "api/other/")
    unpatch_urls(urls_file, "myapp")
    text = urls_file.read_text()
    assert 'include("myapp.urls")' not in text
    assert 'include("otherapp.urls")' in text

import json
import time
from pathlib import Path

import requests

REGISTRY_URL = "https://raw.githubusercontent.com/djuxhq/djux-registry/main/registry.json"
CACHE_DIR = Path.home() / ".djux"
CACHE_FILE = CACHE_DIR / "registry.json"
CACHE_META_FILE = CACHE_DIR / "registry.meta.json"
CACHE_TTL = 3600  # 1 hour


def _cache_is_fresh() -> bool:
    if not CACHE_FILE.exists() or not CACHE_META_FILE.exists():
        return False
    try:
        meta = json.loads(CACHE_META_FILE.read_text(encoding="utf-8"))
        return (time.time() - meta.get("fetched_at", 0)) < CACHE_TTL
    except (json.JSONDecodeError, KeyError):
        return False


def _read_cache() -> dict | None:
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _write_cache(data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    CACHE_META_FILE.write_text(
        json.dumps({"fetched_at": time.time()}), encoding="utf-8"
    )


def fetch_registry(url: str = REGISTRY_URL, force_refresh: bool = False) -> dict:
    if not force_refresh and _cache_is_fresh():
        return _read_cache()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        _write_cache(data)
        return data
    except requests.RequestException as e:
        cached = _read_cache()
        if cached is not None:
            import click
            click.echo(
                f"  ⚠  Network error: could not reach registry.\n"
                f"  Using cached registry (may be outdated).",
                err=True,
            )
            return cached
        raise RuntimeError(
            f"Network error: could not reach registry.\n  {e}"
        ) from e


def get_app(registry: dict, app_name: str) -> dict | None:
    return registry.get("apps", {}).get(app_name)

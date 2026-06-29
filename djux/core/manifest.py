import json
from pathlib import Path


class InvalidManifestError(Exception):
    pass


REQUIRED_FIELDS = {
    "name": str,
    "version": str,
    "description": str,
    "installed_apps": list,
    "url_prefix": str,
    "dependencies": list,
}


def parse_manifest(path: Path) -> dict:
    manifest_file = path / "djux.json"
    if not manifest_file.exists():
        raise InvalidManifestError("App is missing djux.json manifest.")

    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise InvalidManifestError(f"djux.json is not valid JSON: {e}") from e

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            raise InvalidManifestError(
                f"djux.json is missing required field: '{field}'"
            )
        if not isinstance(data[field], expected_type):
            raise InvalidManifestError(
                f"djux.json field '{field}' must be {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )

    return data

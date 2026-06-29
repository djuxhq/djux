import io
import tempfile
import zipfile
from pathlib import Path

import requests


def download_and_extract(download_url: str, app_name: str) -> Path:
    response = requests.get(download_url, timeout=60, stream=True)
    response.raise_for_status()

    tmp_dir = Path(tempfile.mkdtemp())
    zip_path = tmp_dir / f"{app_name}.zip"

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    extract_dir = tmp_dir / "extracted"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    # GitHub archives wrap contents in a top-level folder e.g. djx-app-auth-main/
    # Unwrap it if there's exactly one top-level directory
    children = list(extract_dir.iterdir())
    if len(children) == 1 and children[0].is_dir():
        return children[0]

    return extract_dir

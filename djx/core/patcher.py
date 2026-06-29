import re
from pathlib import Path


def patch_installed_apps(settings_path: Path, apps: list[str]) -> None:
    text = settings_path.read_text(encoding="utf-8")
    for app_name in apps:
        # Already present as a quoted string — skip
        if re.search(rf"""['"]{ re.escape(app_name) }['"]""", text):
            continue
        anchor = "# djx:installed_apps"
        if anchor not in text:
            raise ValueError(
                f"settings.py is missing the anchor comment '{anchor}'. "
                "This project may not have been created by djx."
            )
        text = text.replace(anchor, f'    "{app_name}",\n    {anchor}')
    settings_path.write_text(text, encoding="utf-8")


def unpatch_installed_apps(settings_path: Path, apps: list[str]) -> None:
    lines = settings_path.read_text(encoding="utf-8").splitlines(keepends=True)
    for app_name in apps:
        pattern = re.compile(rf"""^\s*['"]{ re.escape(app_name) }['"],?\s*\n?$""")
        lines = [line for line in lines if not pattern.match(line)]
    settings_path.write_text("".join(lines), encoding="utf-8")


def patch_settings_block(settings_path: Path, block: str) -> None:
    """Inject a raw Python settings block above # djx:settings anchor."""
    text = settings_path.read_text(encoding="utf-8")
    anchor = "# djx:settings"
    if anchor not in text:
        # Append anchor + block at end of file
        text = text.rstrip() + f"\n\n{anchor}\n"
        settings_path.write_text(text, encoding="utf-8")
        text = settings_path.read_text(encoding="utf-8")

    if block.strip() in text:
        return  # already patched

    text = text.replace(anchor, f"{block.strip()}\n\n{anchor}")
    settings_path.write_text(text, encoding="utf-8")


def unpatch_settings_block(settings_path: Path, block: str) -> None:
    text = settings_path.read_text(encoding="utf-8")
    cleaned = text.replace(block.strip() + "\n\n", "").replace(block.strip(), "")
    settings_path.write_text(cleaned, encoding="utf-8")


def patch_urls(urls_path: Path, app_name: str, prefix: str) -> None:
    text = urls_path.read_text(encoding="utf-8")

    # Idempotency — check if already present
    if f'include("{app_name}' in text or f"include('{app_name}" in text:
        return

    # Ensure 'include' is imported
    if "include" not in text:
        text = re.sub(
            r"(from django\.urls import\s+)(path)",
            r"\1path, include",
            text,
        )

    anchor = "# djx:urls"
    if anchor not in text:
        raise ValueError(
            f"urls.py is missing the anchor comment '{anchor}'. "
            "This project may not have been created by djx."
        )

    new_line = f'    path("{prefix}", include("{app_name}.urls")),\n    '
    text = text.replace(f"    {anchor}", f"{new_line}{anchor}")
    urls_path.write_text(text, encoding="utf-8")


def unpatch_urls(urls_path: Path, app_name: str) -> None:
    lines = urls_path.read_text(encoding="utf-8").splitlines(keepends=True)
    pattern = re.compile(rf"""include\(['"]{ re.escape(app_name) }\.""")
    lines = [line for line in lines if not pattern.search(line)]
    urls_path.write_text("".join(lines), encoding="utf-8")

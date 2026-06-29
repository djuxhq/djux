import os
import sys

# Ensure UTF-8 output on Windows (required for Rich/Unicode characters)
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click
from djx.commands.new import new
from djx.commands.add import add
from djx.commands.remove import remove
from djx.commands.list import list_apps
from djx.commands.publish import publish


@click.group()
@click.version_option(package_name="djx")
def main():
    """djx — add production-ready Django apps in one command."""


main.add_command(new)
main.add_command(add)
main.add_command(remove)
main.add_command(list_apps, name="list")
main.add_command(publish)

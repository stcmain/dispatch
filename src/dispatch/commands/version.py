"""``dispatch version`` — print name, version, and Python version."""

from __future__ import annotations

import platform

from rich.console import Console

from dispatch import __version__


def run_version() -> None:
    """Print package + Python version to stdout."""
    console = Console()
    console.print(f"dispatch-cli {__version__}")
    console.print(f"python {platform.python_version()}")

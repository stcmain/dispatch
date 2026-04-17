"""``dispatch status`` — tail INBOX_STATUS.md."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from dispatch.io.inbox import read_tail
from dispatch.io.paths import status_path


def run_status(tail: int, workspace: Path | None) -> None:
    """Print the last ``tail`` lines of INBOX_STATUS.md."""
    console = Console()
    path = status_path(workspace)
    console.print(f"[dim]{path}[/dim]")
    console.print(read_tail(path, n=max(0, tail)))

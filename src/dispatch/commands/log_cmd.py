"""``dispatch log`` — tail dispatch_log.jsonl, pretty-printed via rich."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from dispatch.io.log import tail_log
from dispatch.io.paths import log_path


def run_log(tail: int, workspace: Path | None) -> None:
    """Print the last ``tail`` entries of dispatch_log.jsonl."""
    console = Console()
    path = log_path(workspace)
    if not path.exists():
        console.print("[dim](no log)[/dim]")
        return
    entries = tail_log(path, n=max(0, tail))
    if not entries:
        console.print("[dim](empty)[/dim]")
        return
    for entry in entries:
        ts = str(entry.get("timestamp", "?"))[:19]
        raw = str(entry.get("raw_input", ""))[:60]
        cat = entry.get("category", "?")
        stats = entry.get("token_stats") or {}
        saved = stats.get("savings_pct", 0)
        console.print(
            f"[dim]{ts}[/dim] [cyan]{cat:<10}[/cyan] {saved}% saved  {raw!r}"
        )

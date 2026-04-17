"""``dispatch routes`` — list available route categories as a rich table."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from dispatch.core.classify import load_routes
from dispatch.io.paths import routes_path


def run_routes_list(workspace: Path | None) -> None:
    """Print a table of ``(category, agent, keyword count)``."""
    console = Console()
    path = routes_path(workspace)
    try:
        routes = load_routes(path)
    except (OSError, ValueError) as exc:
        console.print(f"[red]error:[/red] {exc}")
        return

    table = Table(title=f"Routes — {path}")
    table.add_column("Category", style="bold cyan")
    table.add_column("Agent", style="white")
    table.add_column("Keywords", style="dim", justify="right")

    for category, data in routes.items():
        agent = str(data.get("agent", "")) if isinstance(data, dict) else ""
        keyword_count = (
            len(data.get("keywords", [])) if isinstance(data, dict) else 0
        )
        table.add_row(category, agent, str(keyword_count))

    console.print(table)

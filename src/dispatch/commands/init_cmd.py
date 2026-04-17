"""``dispatch init`` — scaffold a ``.dispatch`` folder with a stock routes.json."""

from __future__ import annotations

import shutil
from importlib.resources import files
from pathlib import Path

from rich.console import Console


def _stock_routes_path() -> Path:
    """Locate the bundled stock routes.json inside the installed package."""
    resource = files("dispatch.routes").joinpath("routes.json")
    return Path(str(resource))


def run_init(target_dir: Path) -> None:
    """Create ``<target_dir>/.dispatch/routes.json`` from the stock template."""
    console = Console()
    target_dir = target_dir.expanduser().resolve()
    dispatch_dir = target_dir / ".dispatch"
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    dest = dispatch_dir / "routes.json"

    stock = _stock_routes_path()
    if not stock.exists():
        console.print(
            f"[red]error:[/red] stock routes not found at {stock}"
        )
        return

    shutil.copyfile(stock, dest)
    console.print(f"[green]wrote:[/green] {dest}")

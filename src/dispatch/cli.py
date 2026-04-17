"""Typer CLI entry point — wires subcommands together."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dispatch.commands.exec_cmd import run_exec
from dispatch.commands.init_cmd import run_init
from dispatch.commands.log_cmd import run_log
from dispatch.commands.repl import run_repl
from dispatch.commands.routes import run_routes_list
from dispatch.commands.status import run_status
from dispatch.commands.version import run_version


app = typer.Typer(
    name="dispatch",
    help="Hub-and-spoke AI dispatcher",
    no_args_is_help=False,
    add_completion=False,
)

routes_app = typer.Typer(help="Inspect route definitions")
app.add_typer(routes_app, name="routes")


_WORKSPACE_OPTION = typer.Option(
    None,
    "--workspace",
    "-w",
    help="Override workspace directory (defaults to $DISPATCH_WORKSPACE or ~/Desktop/JARVIS_EMPIRE/dispatcher).",
    envvar="DISPATCH_WORKSPACE",
)


def _resolve_workspace(workspace: Optional[Path]) -> Optional[Path]:
    return workspace.expanduser() if workspace is not None else None


@app.callback(invoke_without_command=True)
def _entry(
    ctx: typer.Context,
    workspace: Optional[Path] = _WORKSPACE_OPTION,
) -> None:
    """Launch the REPL when no subcommand is given."""
    ctx.obj = {"workspace": _resolve_workspace(workspace)}
    if ctx.invoked_subcommand is not None:
        return
    # No subcommand → run the REPL.
    code = run_repl(workspace=ctx.obj["workspace"])
    raise typer.Exit(code=code)


@app.command("exec", help="One-shot dispatch: classify, supercharge, fan out.")
def exec_cmd(
    ctx: typer.Context,
    message: str = typer.Argument(..., help="Short message (3-10 words)."),
    target: Optional[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Comma-separated session names (writes INBOX_<NAME>.md for each).",
    ),
    raw: bool = typer.Option(False, "--raw", help="Skip enrichment; write the message as-is."),
    json_out: bool = typer.Option(False, "--json", help="Emit result as a JSON object."),
) -> None:
    workspace = ctx.obj.get("workspace") if ctx.obj else None
    targets = (
        [name.strip() for name in target.split(",") if name.strip()] if target else None
    )
    try:
        result = run_exec(message, targets, raw=raw, workspace=workspace)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2)

    console = Console()
    if json_out:
        typer.echo(json.dumps(result, indent=2))
        return

    mode = ",".join(targets) if targets else "BROADCAST"
    stats = result.get("stats") or {}
    saved = stats.get("savings_pct", 0)
    console.print(f"[green]→[/green] [bold]{result['category']}[/bold] / {mode}")
    console.print(f"  saved: [green]{saved}%[/green]")
    for path in result.get("paths", []):
        console.print(f"  wrote: {path}")


@app.command("target", help="Target one or more sessions by name (shorthand for exec --target).")
def target_cmd(
    ctx: typer.Context,
    names: str = typer.Argument(..., help="Comma-separated session names."),
    message: list[str] = typer.Argument(..., help="Message to fan out."),
    raw: bool = typer.Option(False, "--raw", help="Skip enrichment."),
) -> None:
    workspace = ctx.obj.get("workspace") if ctx.obj else None
    text = " ".join(message).strip()
    targets = [name.strip() for name in names.split(",") if name.strip()]
    try:
        result = run_exec(text, targets, raw=raw, workspace=workspace)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2)
    console = Console()
    console.print(f"[green]→[/green] [bold]{result['category']}[/bold] / {','.join(targets)}")
    for path in result.get("paths", []):
        console.print(f"  wrote: {path}")


@app.command("status", help="Tail INBOX_STATUS.md.")
def status_cmd(
    ctx: typer.Context,
    tail: int = typer.Option(5, "--tail", "-n", min=1, help="Number of trailing lines."),
) -> None:
    workspace = ctx.obj.get("workspace") if ctx.obj else None
    run_status(tail=tail, workspace=workspace)


@app.command("log", help="Tail dispatch_log.jsonl (pretty-printed).")
def log_cmd(
    ctx: typer.Context,
    tail: int = typer.Option(10, "--tail", "-n", min=1, help="Number of trailing entries."),
) -> None:
    workspace = ctx.obj.get("workspace") if ctx.obj else None
    run_log(tail=tail, workspace=workspace)


@routes_app.callback(invoke_without_command=True)
def _routes_default(ctx: typer.Context) -> None:
    """Default ``dispatch routes`` action → list the table."""
    if ctx.invoked_subcommand is None:
        workspace = ctx.obj.get("workspace") if ctx.obj else None
        run_routes_list(workspace=workspace)


@routes_app.command("list", help="List all route categories as a table.")
def routes_list(ctx: typer.Context) -> None:
    workspace = ctx.obj.get("workspace") if ctx.obj else None
    run_routes_list(workspace=workspace)


@app.command("init", help="Scaffold a .dispatch directory with a stock routes.json.")
def init_cmd_command(
    directory: Path = typer.Argument(
        Path.cwd(),
        help="Target directory to scaffold under (default: current directory).",
    ),
) -> None:
    run_init(target_dir=directory)


@app.command("version", help="Print dispatch-cli and Python version.")
def version_cmd() -> None:
    run_version()


def main() -> int:
    """Programmatic entry point (mirrors ``python -m dispatch``)."""
    try:
        app()
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

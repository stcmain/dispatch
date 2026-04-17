"""Interactive REPL — port of ``hub.py`` using rich for colored output.

Grammar (unchanged):
    @code,content <msg>    one-shot targets
    /target code,ops       sticky targets
    /broadcast             revert to all-hands
    /raw <msg>             skip enrichment
    /last                  reprint last dispatch
    /status                tail INBOX_STATUS.md
    /inbox <name>          tail INBOX_<NAME>.md
    /log                   tail dispatch log
    /routes                print known route names
    /help                  show grammar
    /quit                  exit
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from dispatch.commands.exec_cmd import run_exec
from dispatch.core.classify import load_routes
from dispatch.io.inbox import read_tail
from dispatch.io.log import tail_log
from dispatch.io.paths import (
    default_workspace,
    inbox_path,
    log_path,
    routes_path,
    status_path,
)


_FALLBACK_ROUTES: tuple[str, ...] = (
    "CODE", "CONTENT", "MUSIC", "BETTING", "JOBS", "OPS",
    "RESEARCH", "DEPLOY", "AUDIT", "DELEGATE", "DISPATCH",
    "FAMILY", "VIDEO", "AUTOMATION", "MONETIZATION", "ANALYTICS",
)


def _load_route_names(workspace: Path | None) -> list[str]:
    try:
        return list(load_routes(routes_path(workspace)).keys())
    except (OSError, ValueError):
        return list(_FALLBACK_ROUTES)


def _banner(console: Console, workspace: Path, targets: list[str]) -> None:
    mode = (
        f"targets={','.join(targets)}" if targets else "mode=BROADCAST (all spokes)"
    )
    console.print()
    console.print("[bold cyan]  STC DISPATCHER HUB  [/bold cyan][dim]— speak or type 3-10 words[/dim]")
    console.print(f"[dim]  cwd: {workspace}[/dim]")
    console.print(f"[dim]  {mode}[/dim]")
    console.print(
        "[dim]  /help for commands  •  @<name> <msg> for targeted  •  /quit to exit[/dim]"
    )
    console.print("[dim]  macOS: press Fn-Fn to dictate into this terminal[/dim]")
    console.print()


def _print_result(
    console: Console,
    raw: str,
    result: dict[str, Any],
    targets: list[str],
) -> None:
    mode = ",".join(targets) if targets else "BROADCAST"
    stats = result.get("stats") or {}
    raw_tok = stats.get("raw_input_tokens", len(raw) // 4)
    enr_tok = stats.get("supercharged_tokens", len(result.get("enriched", "")) // 4)
    saved = stats.get("savings_pct", 0)
    category = result.get("category", "?")
    console.print(f"  [green]→[/green] [bold]{category}[/bold] / {mode}")
    console.print(f"  [dim]raw:[/dim]      {raw!r}  ({raw_tok} tok)")
    console.print(
        f"  [dim]enriched:[/dim] ~{enr_tok} tok  [green]{saved}% saved[/green] vs full context"
    )
    for p in result.get("paths", []):
        console.print(f"  [dim]wrote:[/dim]    {p}")
    console.print()


def _parse_at_prefix(line: str, valid_routes: list[str]) -> tuple[list[str], str]:
    """``@code,content do the thing`` → ``(['code','content'], 'do the thing')``."""
    if not line.startswith("@"):
        return [], line
    head, _sep, body = line[1:].partition(" ")
    if not body:
        return [], line
    candidates = [part.strip().upper() for part in head.split(",") if part.strip()]
    valid = [c for c in candidates if c in valid_routes]
    if not valid or len(valid) != len(candidates):
        return [], line
    return [c.lower() for c in valid], body.strip()


def _print_help(console: Console) -> None:
    doc = __doc__ or "Dispatcher REPL."
    console.print(doc)


def _print_log(console: Console, workspace: Path | None, n: int = 3) -> None:
    entries = tail_log(log_path(workspace), n=n)
    if not entries:
        console.print("[dim](no log)[/dim]")
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


def run_repl(workspace: Path | None = None) -> int:
    """Run the REPL until the user quits. Returns the exit code."""
    console = Console()
    resolved_workspace = (workspace or default_workspace()).expanduser()
    resolved_workspace.mkdir(parents=True, exist_ok=True)
    os.chdir(resolved_workspace)

    valid_routes = _load_route_names(workspace)
    sticky_targets: list[str] = []
    last_result: Optional[dict[str, Any]] = None
    last_raw: Optional[str] = None

    _banner(console, resolved_workspace, sticky_targets)

    while True:
        try:
            prompt_tag = (
                f"[magenta]{','.join(sticky_targets).upper()}[/magenta]"
                if sticky_targets
                else "[cyan]HUB[/cyan]"
            )
            console.print(prompt_tag + "[bold]❯ [/bold]", end="")
            line = input().strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return 0

        if not line:
            continue

        if line.startswith("/"):
            cmd, _sep, arg = line[1:].partition(" ")
            cmd = cmd.lower().strip()
            arg = arg.strip()

            if cmd in ("quit", "exit", "q"):
                return 0
            if cmd == "help":
                _print_help(console)
                continue
            if cmd == "target":
                if not arg:
                    console.print("  [yellow]usage:[/yellow] /target code,content")
                    continue
                names = [n.strip().upper() for n in arg.split(",") if n.strip()]
                bad = [n for n in names if n not in valid_routes]
                if bad:
                    console.print(f"  [red]unknown:[/red] {','.join(bad)}")
                    console.print(f"  [dim]known:[/dim] {','.join(valid_routes)}")
                    continue
                sticky_targets = [n.lower() for n in names]
                console.print(f"  [green]targeting:[/green] {','.join(sticky_targets)}")
                continue
            if cmd == "broadcast":
                sticky_targets = []
                console.print("  [green]mode:[/green] BROADCAST (all spokes)")
                continue
            if cmd == "raw":
                if not arg:
                    console.print("  [yellow]usage:[/yellow] /raw <message>")
                    continue
                result = run_exec(arg, sticky_targets, raw=True, workspace=workspace)
                last_result, last_raw = result, arg
                _print_result(console, arg, result, sticky_targets)
                continue
            if cmd == "last":
                if last_result and last_raw:
                    _print_result(console, last_raw, last_result, sticky_targets)
                else:
                    console.print("  [dim](no prior dispatch)[/dim]")
                continue
            if cmd == "status":
                console.print(read_tail(status_path(workspace), 5))
                console.print()
                continue
            if cmd == "inbox":
                if not arg:
                    console.print("  [yellow]usage:[/yellow] /inbox code")
                    continue
                target = inbox_path(arg, workspace)
                if not target.exists():
                    console.print(f"  [dim]no file:[/dim] {target}")
                    continue
                console.print(read_tail(target, 30))
                console.print()
                continue
            if cmd == "log":
                _print_log(console, workspace, n=3)
                console.print()
                continue
            if cmd == "routes":
                console.print(f"  [cyan]{','.join(valid_routes)}[/cyan]")
                continue
            console.print(f"  [red]unknown command:[/red] /{cmd}")
            console.print("  [dim]try /help[/dim]")
            continue

        # @prefix one-shot target (does not change sticky_targets)
        oneshot_targets, stripped = _parse_at_prefix(line, valid_routes)
        use_targets = oneshot_targets or sticky_targets
        try:
            result = run_exec(stripped, use_targets, raw=False, workspace=workspace)
        except (OSError, ValueError) as exc:
            console.print(f"  [red]error:[/red] {exc}")
            continue
        last_result, last_raw = result, stripped
        _print_result(console, stripped, result, use_targets)

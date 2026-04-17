"""Tests for the REPL command — focus on pure helpers + one E2E loop via monkeypatch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dispatch.commands import repl as repl_mod
from dispatch.commands.repl import (
    _FALLBACK_ROUTES,
    _load_route_names,
    _parse_at_prefix,
    _print_log,
    run_repl,
)
from dispatch.io.log import log_dispatch


pytestmark = pytest.mark.unit


class _Cap:
    """Minimal rich.Console stand-in that captures .print() args."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def print(self, *args: object, end: str = "\n") -> None:
        self.lines.append(" ".join(str(a) for a in args))


def test_parse_at_prefix_accepts_known_routes() -> None:
    targets, msg = _parse_at_prefix("@code,content do the thing", ["CODE", "CONTENT"])
    assert targets == ["code", "content"]
    assert msg == "do the thing"


def test_parse_at_prefix_rejects_unknown_route() -> None:
    targets, msg = _parse_at_prefix("@code,bogus hi", ["CODE", "CONTENT"])
    assert targets == []
    assert msg == "@code,bogus hi"


def test_parse_at_prefix_no_body_returns_original() -> None:
    targets, msg = _parse_at_prefix("@code", ["CODE"])
    assert targets == []
    assert msg == "@code"


def test_parse_at_prefix_no_prefix_returns_empty() -> None:
    targets, msg = _parse_at_prefix("hello world", ["CODE"])
    assert targets == []
    assert msg == "hello world"


def test_parse_at_prefix_empty_segment_treated_as_unknown() -> None:
    targets, msg = _parse_at_prefix("@code, hi", ["CODE"])
    assert targets == ["code"]
    assert msg == "hi"


def test_load_route_names_from_workspace(tmp_workspace: Path) -> None:
    names = _load_route_names(tmp_workspace)
    assert "CODE" in names and "CONTENT" in names


def test_load_route_names_falls_back_when_missing(tmp_path: Path) -> None:
    names = _load_route_names(tmp_path)
    assert names == list(_FALLBACK_ROUTES)


def test_print_log_empty(tmp_path: Path) -> None:
    cap = _Cap()
    _print_log(cap, tmp_path, n=3)
    assert any("no log" in line for line in cap.lines)


def test_print_log_with_entries(tmp_path: Path) -> None:
    log_dispatch(
        {
            "timestamp": "2026-04-17T08:00:00",
            "raw_input": "draft the caption",
            "category": "CONTENT",
            "token_stats": {"savings_pct": 31},
        },
        tmp_path / "dispatch_log.jsonl",
    )
    cap = _Cap()
    _print_log(cap, tmp_path, n=3)
    joined = "\n".join(cap.lines)
    assert "CONTENT" in joined
    assert "31%" in joined


def test_run_repl_quit_immediately(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda: "/quit")
    assert run_repl(tmp_workspace) == 0


def test_run_repl_help_then_quit(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["/help", "/quit"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    assert run_repl(tmp_workspace) == 0


def test_run_repl_eof_exits_cleanly(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise() -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise)
    assert run_repl(tmp_workspace) == 0


def test_run_repl_unknown_command(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["/nope", "/quit"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    assert run_repl(tmp_workspace) == 0


def test_run_repl_target_and_broadcast(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(
        [
            "/target",              # no arg → usage line
            "/target code,content", # ok
            "/target bogus",        # unknown
            "/broadcast",           # back to all-hands
            "/routes",              # prints route names
            "/log",                 # no log yet
            "/status",              # no status yet
            "/inbox",               # no arg
            "/inbox code",          # no file
            "/last",                # no prior dispatch
            "/raw",                 # usage
            "/quit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    assert run_repl(tmp_workspace) == 0


def test_run_repl_dispatch_and_last(tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(
        [
            "",                           # empty line skipped
            "fix the site",               # real dispatch
            "/last",                      # reprint
            "/raw say hi",                # raw dispatch
            "@code,content build stuff",  # @-prefix one-shot
            "/quit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    assert run_repl(tmp_workspace) == 0
    assert (tmp_workspace / "BROADCAST.md").exists() or (
        tmp_workspace / "INBOX_CODE.md"
    ).exists()


def test_run_repl_dispatch_error_path(
    tmp_workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(*_a: object, **_kw: object) -> dict:
        raise OSError("disk full")

    monkeypatch.setattr(repl_mod, "run_exec", _boom)
    inputs = iter(["hello world", "/quit"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    assert run_repl(tmp_workspace) == 0

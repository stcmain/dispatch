"""Tests for dispatch.io.log and dispatch log CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dispatch.cli import app
from dispatch.io.log import log_dispatch, tail_log


pytestmark = pytest.mark.unit


runner = CliRunner()


def test_tail_log_missing_file_returns_empty(tmp_path: Path) -> None:
    assert tail_log(tmp_path / "nope.jsonl") == []


def test_tail_log_returns_last_n_entries(tmp_path: Path) -> None:
    log = tmp_path / "d.jsonl"
    for i in range(5):
        log_dispatch({"i": i}, log)
    out = tail_log(log, n=3)
    assert [e["i"] for e in out] == [2, 3, 4]


def test_tail_log_skips_invalid_and_blank_lines(tmp_path: Path) -> None:
    log = tmp_path / "d.jsonl"
    log.write_text(
        '{"ok":1}\n\nnot-json\n["list-not-dict"]\n{"ok":2}\n',
        encoding="utf-8",
    )
    out = tail_log(log, n=10)
    assert out == [{"ok": 1}, {"ok": 2}]


def test_tail_log_zero_n_returns_empty(tmp_path: Path) -> None:
    log = tmp_path / "d.jsonl"
    log_dispatch({"a": 1}, log)
    assert tail_log(log, n=0) == []


def test_log_dispatch_creates_parent_dir(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "sub" / "d.jsonl"
    log_dispatch({"x": 1}, target)
    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8").strip()) == {"x": 1}


def test_log_cli_prints_entries(tmp_workspace: Path) -> None:
    log_dispatch(
        {
            "timestamp": "2026-04-17T09:00:00",
            "raw_input": "fix the site",
            "category": "CODE",
            "token_stats": {"savings_pct": 42},
        },
        tmp_workspace / "dispatch_log.jsonl",
    )
    result = runner.invoke(
        app, ["--workspace", str(tmp_workspace), "log", "--tail", "5"]
    )
    assert result.exit_code == 0, result.stdout
    assert "CODE" in result.stdout
    assert "42%" in result.stdout


def test_log_cli_no_file(tmp_workspace: Path) -> None:
    result = runner.invoke(app, ["--workspace", str(tmp_workspace), "log"])
    assert result.exit_code == 0
    assert "no log" in result.stdout


def test_log_cli_empty_file(tmp_workspace: Path) -> None:
    (tmp_workspace / "dispatch_log.jsonl").write_text("", encoding="utf-8")
    result = runner.invoke(app, ["--workspace", str(tmp_workspace), "log"])
    assert result.exit_code == 0
    assert "empty" in result.stdout

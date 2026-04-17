"""Integration tests for the Typer CLI wrapper."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from dispatch import __version__
from dispatch.cli import app


pytestmark = pytest.mark.integration


runner = CliRunner()


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_exec_creates_broadcast_file(tmp_workspace: Path) -> None:
    result = runner.invoke(
        app,
        ["--workspace", str(tmp_workspace), "exec", "fix the site"],
    )
    assert result.exit_code == 0, result.stdout
    broadcast = tmp_workspace / "BROADCAST.md"
    assert broadcast.exists()
    text = broadcast.read_text(encoding="utf-8")
    assert "BROADCAST" in text
    assert "fix the site" in text


def test_exec_with_targets_creates_per_session_inboxes(tmp_workspace: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--workspace",
            str(tmp_workspace),
            "exec",
            "draft caption for today",
            "--target",
            "code,content",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_workspace / "INBOX_CODE.md").exists()
    assert (tmp_workspace / "INBOX_CONTENT.md").exists()
    # Broadcast should NOT be written when a target is specified.
    assert not (tmp_workspace / "BROADCAST.md").exists()


def test_routes_list_command(tmp_workspace: Path) -> None:
    result = runner.invoke(
        app,
        ["--workspace", str(tmp_workspace), "routes", "list"],
    )
    assert result.exit_code == 0
    assert "CODE" in result.stdout
    assert "CONTENT" in result.stdout

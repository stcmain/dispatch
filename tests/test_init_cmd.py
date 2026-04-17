"""Tests for ``dispatch init`` — ships stock routes.json as package data."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dispatch.cli import app
from dispatch.commands.init_cmd import _stock_routes_path, run_init


pytestmark = pytest.mark.integration


runner = CliRunner()


def test_stock_routes_path_resolves_to_packaged_file() -> None:
    path = _stock_routes_path()
    assert path.exists(), f"bundled routes.json missing at {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and len(data) > 0


def test_run_init_writes_routes(tmp_path: Path) -> None:
    run_init(tmp_path)
    dest = tmp_path / ".dispatch" / "routes.json"
    assert dest.exists()
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and len(data) > 0


def test_init_cli_creates_dispatch_dir(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    dest = tmp_path / ".dispatch" / "routes.json"
    assert dest.exists()
    assert "wrote" in result.stdout.lower()

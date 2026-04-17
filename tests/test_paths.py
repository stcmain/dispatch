"""Tests for path resolution — ensures init-time layout is honored at runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dispatch.io.paths import routes_path


pytestmark = pytest.mark.unit


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_routes_path_prefers_workspace_root(tmp_path: Path) -> None:
    _write(tmp_path / "routes.json", {"root": {}})
    _write(tmp_path / ".dispatch" / "routes.json", {"nested": {}})
    assert routes_path(tmp_path) == tmp_path / "routes.json"


def test_routes_path_falls_back_to_dispatch_dir(tmp_path: Path) -> None:
    _write(tmp_path / ".dispatch" / "routes.json", {"nested": {}})
    assert routes_path(tmp_path) == tmp_path / ".dispatch" / "routes.json"


def test_routes_path_returns_root_when_neither_exists(tmp_path: Path) -> None:
    assert routes_path(tmp_path) == tmp_path / "routes.json"

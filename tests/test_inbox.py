"""Unit tests for dispatch.io.inbox writers."""

from __future__ import annotations

from pathlib import Path

import pytest

from dispatch.io.inbox import write_broadcast, write_targeted
from dispatch.io.paths import broadcast_path, inbox_path


pytestmark = pytest.mark.unit


def test_write_broadcast_contains_expected_headers(tmp_path: Path) -> None:
    path = write_broadcast("CODE", "enriched prompt body", "raw msg", workspace=tmp_path)
    assert path == broadcast_path(tmp_path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# BROADCAST — ")
    assert "**Category:** CODE" in text
    assert "enriched prompt body" in text
    assert "Acknowledge in `INBOX_STATUS.md`" in text


def test_write_targeted_contains_session_header(tmp_path: Path) -> None:
    path = write_targeted("code", "CODE", "enriched body", "raw", workspace=tmp_path)
    assert path == inbox_path("code", tmp_path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# INBOX — CODE — ")
    assert "**Category:** CODE" in text
    # Targeted inboxes must NOT include the acknowledge footer.
    assert "Acknowledge in `INBOX_STATUS.md`" not in text


def test_targeted_uppercases_session_name(tmp_path: Path) -> None:
    path = write_targeted("ops", "OPS", "body", "raw", workspace=tmp_path)
    assert path.name == "INBOX_OPS.md"

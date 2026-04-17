"""Shared pytest fixtures for dispatch-cli tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _REPO_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


@pytest.fixture
def sample_routes() -> dict[str, dict]:
    """Inline fixture mirroring the shape of routes.json."""
    return {
        "CODE": {
            "description": "Code fixes and builds.",
            "keywords": ["fix", "build", "code", "site", "page"],
            "agent": "Claude Code",
            "cwd": "~/Desktop/JARVIS_EMPIRE",
            "context_sections": ["operating_rules"],
            "priority_files": ["~/Desktop/JARVIS_EMPIRE/README.md"],
            "notes": "Keep it tight.",
        },
        "CONTENT": {
            "description": "Content drafts.",
            "keywords": ["post", "write", "draft", "caption"],
            "agent": "Content Agent",
            "cwd": "~/Desktop/JARVIS_EMPIRE",
            "context_sections": [],
            "priority_files": [],
            "notes": "",
        },
        "OPS": {
            "description": "Operations catch-all.",
            "keywords": ["status", "check", "report"],
            "agent": "Ops Agent",
            "cwd": "~/Desktop/JARVIS_EMPIRE",
            "context_sections": ["operating_rules"],
            "priority_files": [],
            "notes": "Default fallback.",
        },
    }


@pytest.fixture
def sample_cache() -> dict[str, Any]:
    """Minimal context cache fixture."""
    return {
        "operating_rules": [
            "Use GREEN/YELLOW/RED",
            "VS Code terminal only",
        ],
        "infrastructure": {
            "services": ["OpenClaw", "Ollama"],
        },
    }


@pytest.fixture
def tmp_workspace(
    tmp_path: Path,
    sample_routes: dict[str, dict],
    sample_cache: dict[str, Any],
) -> Path:
    """Create an isolated workspace with seeded routes + cache."""
    (tmp_path / "routes.json").write_text(json.dumps(sample_routes), encoding="utf-8")
    (tmp_path / "context_cache.json").write_text(json.dumps(sample_cache), encoding="utf-8")
    return tmp_path

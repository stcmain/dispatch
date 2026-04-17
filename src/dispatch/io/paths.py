"""Single source of truth for filesystem paths used by the dispatcher.

The default workspace stays aligned with the legacy ``~/Desktop/JARVIS_EMPIRE/dispatcher``
directory so pre-existing inbox / log files remain compatible.
"""

from __future__ import annotations

import os
from pathlib import Path


_DEFAULT_WORKSPACE_ENV = "DISPATCH_WORKSPACE"
_DEFAULT_WORKSPACE_FALLBACK = "~/Desktop/JARVIS_EMPIRE/dispatcher"


def default_workspace() -> Path:
    """Return the workspace directory, respecting ``DISPATCH_WORKSPACE``."""
    raw = os.environ.get(_DEFAULT_WORKSPACE_ENV, _DEFAULT_WORKSPACE_FALLBACK)
    return Path(raw).expanduser()


def _resolve(workspace: Path | None) -> Path:
    return workspace.expanduser() if workspace is not None else default_workspace()


def workspace_file(name: str, workspace: Path | None = None) -> Path:
    """Return ``<workspace>/<name>`` using the resolved workspace."""
    return _resolve(workspace) / name


def routes_path(workspace: Path | None = None) -> Path:
    """Resolve routes.json, preferring workspace root, falling back to .dispatch/."""
    base = _resolve(workspace)
    root = base / "routes.json"
    if root.exists():
        return root
    nested = base / ".dispatch" / "routes.json"
    if nested.exists():
        return nested
    return root


def context_cache_path(workspace: Path | None = None) -> Path:
    return _resolve(workspace) / "context_cache.json"


def broadcast_path(workspace: Path | None = None) -> Path:
    return _resolve(workspace) / "BROADCAST.md"


def inbox_path(session: str, workspace: Path | None = None) -> Path:
    return _resolve(workspace) / f"INBOX_{session.upper()}.md"


def log_path(workspace: Path | None = None) -> Path:
    return _resolve(workspace) / "dispatch_log.jsonl"


def status_path(workspace: Path | None = None) -> Path:
    return _resolve(workspace) / "INBOX_STATUS.md"

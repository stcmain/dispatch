"""Inbox + broadcast file writers.

The body formats match the legacy ``fanout.py`` byte-for-byte so existing spoke
agents keep reading and acknowledging without changes.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from dispatch.io.paths import broadcast_path, inbox_path


_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M %Z"


def _now_ts() -> str:
    """Legacy-compatible timestamp: naive ``%Y-%m-%d %H:%M %Z`` stripped."""
    return _dt.datetime.now().strftime(_TIMESTAMP_FORMAT).strip()


def write_broadcast(
    category: str,
    enriched: str,
    raw: str,
    workspace: Path | None = None,
) -> Path:
    """All-hands broadcast file. Every spoke agent reads this path."""
    target = broadcast_path(workspace)
    ts = _now_ts()
    body = (
        f"# BROADCAST — {ts}\n"
        f"**Category:** {category}  •  **Raw:** {raw!r}\n\n"
        f"---\n\n"
        f"{enriched}\n"
        f"\n---\n"
        f"*Acknowledge in `INBOX_STATUS.md` when done.*\n"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def write_targeted(
    session: str,
    category: str,
    enriched: str,
    raw: str,
    workspace: Path | None = None,
) -> Path:
    """Per-session inbox file (``INBOX_<NAME>.md``)."""
    target = inbox_path(session, workspace)
    ts = _now_ts()
    body = (
        f"# INBOX — {session.upper()} — {ts}\n"
        f"**Category:** {category}  •  **Raw:** {raw!r}\n\n"
        f"---\n\n"
        f"{enriched}\n"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def read_tail(path: Path, n: int = 5) -> str:
    """Return the last ``n`` lines of a file as a joined string."""
    if not path.exists():
        return "(no file)"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return f"[err] {exc}"
    tail_lines = lines[-n:] if n > 0 else []
    return "\n".join(tail_lines) if tail_lines else "(empty)"

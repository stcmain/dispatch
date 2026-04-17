"""Append-only JSONL dispatch log."""

from __future__ import annotations

import json
from pathlib import Path


def log_dispatch(entry: dict, log_path: Path) -> None:
    """Append a JSON-encoded entry to the log file (one line per record)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def tail_log(log_path: Path, n: int = 10) -> list[dict]:
    """Return the last ``n`` parsed JSONL entries. Invalid lines are skipped."""
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    tail_lines = lines[-n:] if n > 0 else []
    results: list[dict] = []
    for line in tail_lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            results.append(parsed)
    return results

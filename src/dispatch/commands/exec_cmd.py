"""Non-interactive one-shot dispatch — used by ``dispatch exec`` and the REPL."""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any

from dispatch.core.enrich import enrich
from dispatch.io.inbox import write_broadcast, write_targeted
from dispatch.io.log import log_dispatch
from dispatch.io.paths import log_path


_RAW_CATEGORY = "RAW"


def _raw_stats(message: str) -> dict[str, Any]:
    rough = max(0, len(message) // 4)
    return {
        "raw_input_tokens": rough,
        "supercharged_tokens": rough,
        "full_context_tokens": 0,
        "tokens_saved": 0,
        "savings_pct": 0,
    }


def _normalize_targets(targets: list[str] | None) -> list[str]:
    if not targets:
        return []
    cleaned: list[str] = []
    for name in targets:
        if name is None:
            continue
        stripped = name.strip()
        if stripped:
            cleaned.append(stripped.lower())
    return cleaned


def run_exec(
    message: str,
    targets: list[str] | None,
    raw: bool,
    workspace: Path | None,
) -> dict[str, Any]:
    """Classify + supercharge + write inbox/broadcast files + log.

    Returns ``{category, paths, stats, enriched}``.
    """
    message = (message or "").strip()
    if not message:
        raise ValueError("message must be non-empty")

    if raw:
        category = _RAW_CATEGORY
        enriched = message
        stats = _raw_stats(message)
    else:
        category, enriched, stats = enrich(message, workspace=workspace)

    normalized_targets = _normalize_targets(targets)
    written: list[Path] = []
    if normalized_targets:
        for name in normalized_targets:
            written.append(write_targeted(name, category, enriched, message, workspace=workspace))
    else:
        written.append(write_broadcast(category, enriched, message, workspace=workspace))

    log_entry = {
        "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "raw_input": message,
        "category": category,
        "targets": normalized_targets,
        "paths": [str(p) for p in written],
        "token_stats": stats,
    }
    log_dispatch(log_entry, log_path(workspace))

    return {
        "category": category,
        "paths": [str(p) for p in written],
        "stats": stats,
        "enriched": enriched,
    }

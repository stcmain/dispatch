"""Pure classifier — keyword scoring with fallback heuristics.

Ported from the legacy ``dispatcher.classify`` function. This module is I/O-free:
callers load ``routes.json`` once and pass the keyword map in.
"""

from __future__ import annotations

import json
from pathlib import Path


# Fallback heuristics applied only when no keyword matches at all.
_CODE_FALLBACK = ("site", "page", "build", "run", "error")
_CONTENT_FALLBACK = ("post", "write", "draft")
_DEFAULT_CATEGORY = "OPS"


def load_routes(routes_path: Path) -> dict[str, dict]:
    """Read and return the routes.json mapping."""
    with open(routes_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"routes.json must be a JSON object, got {type(data).__name__}")
    return data


def load_keywords(routes: dict[str, dict]) -> dict[str, list[str]]:
    """Extract ``{category: [keywords...]}`` from a routes mapping."""
    return {cat: list(data.get("keywords", [])) for cat, data in routes.items()}


def classify(message: str, keywords: dict[str, list[str]]) -> str:
    """Return the best-match category name (UPPERCASE).

    Scoring mirrors ``dispatcher.classify``: each keyword hit adds 1; ties resolve
    by Python's ``max`` (first category declaration wins when equal). Fallback
    heuristics apply only when no keyword matches.
    """
    message_lower = message.lower()
    scores: dict[str, int] = {}

    for category, kw_list in keywords.items():
        score = sum(1 for kw in kw_list if kw in message_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        if any(word in message_lower for word in _CODE_FALLBACK):
            return "CODE"
        if any(word in message_lower for word in _CONTENT_FALLBACK):
            return "CONTENT"
        return _DEFAULT_CATEGORY

    return max(scores, key=lambda c: scores[c]).upper()

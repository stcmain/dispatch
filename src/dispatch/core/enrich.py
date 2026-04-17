"""High-level orchestrator — loads routes/cache, classifies, superchages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dispatch.core.classify import classify, load_keywords, load_routes
from dispatch.core.supercharge import supercharge
from dispatch.io.paths import context_cache_path, routes_path


def _load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"context cache must be a JSON object, got {type(data).__name__}")
    return data


def enrich(
    message: str,
    workspace: Path | None = None,
) -> tuple[str, str, dict[str, Any]]:
    """Return ``(category, supercharged_prompt, token_stats)``."""
    routes = load_routes(routes_path(workspace))
    cache = _load_cache(context_cache_path(workspace))
    keywords = load_keywords(routes)

    category = classify(message, keywords)
    result = supercharge(message, category, routes, cache)

    prompt = result["supercharged_prompt"]
    stats = result.get("token_stats", {})
    # Keep the resolved category (supercharge may fall back to OPS on unknown).
    resolved_category = result.get("category", category)
    return resolved_category, prompt, stats

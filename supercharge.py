#!/usr/bin/env python3
"""Legacy shim for supercharge.py — delegates to the ``dispatch`` package.

Maintains the ``supercharge()`` function signature for backwards compatibility.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add src/ to path
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    from dispatch.core.classify import load_routes
    from dispatch.core.enrich import _load_cache
    from dispatch.core.supercharge import supercharge as _supercharge
    from dispatch.io.paths import context_cache_path, routes_path
except ImportError:
    # Minimal fallback if package missing
    def _supercharge(msg: str, cat: str, routes: dict, cache: dict) -> dict:
        return {"supercharged_prompt": msg}
    def load_routes(p: Path) -> dict: return {}
    def _load_cache(p: Path) -> dict: return {}
    def routes_path(w: Any) -> Path: return Path("routes.json")
    def context_cache_path(w: Any) -> Path: return Path("context_cache.json")


def supercharge(raw_message: str, category: str, verbose: bool = False) -> dict:
    """Legacy entry point. Verbose argument is ignored (always uses package logic)."""
    workspace = None
    routes = load_routes(routes_path(workspace))
    cache = _load_cache(context_cache_path(workspace))
    return _supercharge(raw_message, category, routes, cache)


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "check status"
    result = supercharge(msg, "OPS")
    print(result["supercharged_prompt"])

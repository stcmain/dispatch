#!/usr/bin/env python3
"""Legacy shim for dispatcher.py — delegates to the ``dispatch`` package.

Maintains the exact console output and logging format of the original
script while using the refactored logic in ``src/dispatch``.
"""

from __future__ import annotations

import datetime
import os
import sys
from pathlib import Path

# Add src/ to path so we can import the dispatch package
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    from dispatch.core.classify import classify, load_keywords, load_routes
    from dispatch.core.enrich import _load_cache
    from dispatch.core.supercharge import supercharge
    from dispatch.io.log import log_dispatch
    from dispatch.io.paths import context_cache_path, log_path, routes_path
except ImportError:
    print("[ERROR] Could not import 'dispatch' package. Ensure 'src/' is present and dependencies (typer, rich) are installed.")
    sys.exit(1)


def print_header(label: str) -> None:
    width = 60
    print("=" * width)
    print(f"  {label}")
    print("=" * width)


def main() -> None:
    if len(sys.argv) > 1:
        raw_message = " ".join(sys.argv[1:]).strip()
    elif not sys.stdin.isatty():
        raw_message = sys.stdin.read().strip()
    else:
        print("Usage: python3 dispatcher.py \"your message\"")
        print("       echo \"your message\" | python3 dispatcher.py")
        sys.exit(1)

    if not raw_message:
        print("[ERROR] Empty message. Provide a task.")
        sys.exit(1)

    # Resolve paths and load data
    # Support DISPATCH_WORKSPACE env var for the shim too
    workspace_path = os.environ.get("DISPATCH_WORKSPACE")
    workspace = Path(workspace_path) if workspace_path else None

    r_path = routes_path(workspace)
    c_path = context_cache_path(workspace)

    try:
        routes = load_routes(r_path)
        cache = _load_cache(c_path)
    except Exception as exc:
        print(f"[ERROR] Failed to load configuration: {exc}")
        print(f"  Checked routes at: {r_path}")
        sys.exit(1)

    keywords = load_keywords(routes)

    # Classify
    category = classify(raw_message, keywords)

    # Supercharge
    result = supercharge(raw_message, category, routes, cache)

    # Log
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "raw_input": raw_message,
        "category": result["category"],
        "agent": result["agent"],
        "supercharged_prompt": result["supercharged_prompt"],
        "token_stats": result["token_stats"]
    }
    l_path = log_path(workspace)
    log_dispatch(log_entry, l_path)

    # Output
    stats = result["token_stats"]

    print_header("STC DISPATCHER")
    print(f"  RAW INPUT    : {raw_message}")
    print(f"  CATEGORY     : {result['category']}")
    print(f"  AGENT        : {result['agent']}")
    print(f"  CWD          : {result['cwd']}")
    print()
    print(f"  TOKENS (IN)  : ~{stats['raw_input_tokens']}")
    print(f"  TOKENS (OUT) : ~{stats['supercharged_tokens']}")
    print(f"  FULL CONTEXT : ~{stats['full_context_tokens']}")
    print(f"  SAVED        : ~{stats['tokens_saved']} tokens ({stats['savings_pct']}% vs sending all context)")
    print("=" * 60)
    print()
    print_header("SUPERCHARGED PROMPT")
    print()
    print(result["supercharged_prompt"])
    print()
    print("=" * 60)
    print(f"  Logged to: {l_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

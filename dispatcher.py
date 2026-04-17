#!/usr/bin/env python3
"""
dispatcher.py — STC JARVIS Dispatcher
Reads a short raw message, classifies it, supercharges it with relevant context,
and outputs a ready-to-use prompt for any agent.

Usage:
    python3 dispatcher.py "fix the website"
    echo "place bets" | python3 dispatcher.py
"""

import json
import os
import sys
import datetime
from typing import Optional

from supercharge import supercharge, load_json


ROUTES_PATH = os.path.join(os.path.dirname(__file__), "routes.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "dispatch_log.jsonl")


# --- CLASSIFIER ---

CATEGORY_KEYWORDS = {}

def load_keywords() -> dict[str, list[str]]:
    routes = load_json(ROUTES_PATH)
    return {cat: data.get("keywords", []) for cat, data in routes.items()}


def classify(message: str) -> str:
    keywords = load_keywords()
    message_lower = message.lower()
    scores: dict[str, int] = {}

    for category, kw_list in keywords.items():
        score = sum(1 for kw in kw_list if kw in message_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        # Fallback heuristics
        if any(w in message_lower for w in ["site", "page", "build", "run", "error"]):
            return "CODE"
        if any(w in message_lower for w in ["post", "write", "draft"]):
            return "CONTENT"
        return "OPS"

    return max(scores, key=lambda c: scores[c])


# --- LOGGER ---

def log_dispatch(entry: dict) -> None:
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# --- MAIN ---

def read_input() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("Usage: python3 dispatcher.py \"your message\"")
    print("       echo \"your message\" | python3 dispatcher.py")
    sys.exit(1)


def print_header(label: str) -> None:
    width = 60
    print("=" * width)
    print(f"  {label}")
    print("=" * width)


def main() -> None:
    raw_message = read_input()

    if not raw_message:
        print("[ERROR] Empty message. Provide a task.")
        sys.exit(1)

    # Classify
    category = classify(raw_message)

    # Supercharge
    result = supercharge(raw_message, category)

    # Log
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "raw_input": raw_message,
        "category": category,
        "agent": result["agent"],
        "supercharged_prompt": result["supercharged_prompt"],
        "token_stats": result["token_stats"]
    }
    log_dispatch(log_entry)

    # Output
    stats = result["token_stats"]

    print_header("STC DISPATCHER")
    print(f"  RAW INPUT    : {raw_message}")
    print(f"  CATEGORY     : {category}")
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
    print(f"  Logged to: {LOG_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()

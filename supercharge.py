"""
supercharge.py — Prompt enhancement engine for STC Dispatcher
Takes a raw message + category and returns a structured, context-rich prompt.
"""

import json
import os
from typing import Optional


CACHE_PATH = os.path.join(os.path.dirname(__file__), "context_cache.json")
ROUTES_PATH = os.path.join(os.path.dirname(__file__), "routes.json")


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def estimate_tokens(text: str) -> int:
    """Rough estimate: 4 chars = 1 token."""
    return len(text) // 4


def extract_context_sections(cache: dict, sections: list[str]) -> dict:
    return {k: cache[k] for k in sections if k in cache}


def format_context_block(context: dict) -> str:
    lines = []
    for key, val in context.items():
        header = key.upper().replace("_", " ")
        if isinstance(val, dict):
            lines.append(f"[{header}]")
            for k, v in val.items():
                if isinstance(v, dict):
                    lines.append(f"  {k}:")
                    for kk, vv in v.items():
                        lines.append(f"    {kk}: {vv}")
                elif isinstance(v, list):
                    lines.append(f"  {k}: {', '.join(str(i) for i in v)}")
                else:
                    lines.append(f"  {k}: {v}")
        elif isinstance(val, list):
            lines.append(f"[{header}]")
            for item in val:
                lines.append(f"  - {item}")
        else:
            lines.append(f"[{header}] {val}")
        lines.append("")
    return "\n".join(lines)


def format_priority_files(files: list[str]) -> str:
    if not files:
        return ""
    return "Priority files to read first:\n" + "\n".join(f"  - {f}" for f in files)


def supercharge(raw_message: str, category: str, verbose: bool = False) -> dict:
    cache = load_json(CACHE_PATH)
    routes = load_json(ROUTES_PATH)

    if category not in routes:
        category = "OPS"

    route = routes[category]
    context_sections = route.get("context_sections", [])
    relevant_context = extract_context_sections(cache, context_sections)
    context_block = format_context_block(relevant_context)
    priority_files = format_priority_files(route.get("priority_files", []))
    route_notes = route.get("notes", "")

    # Operating rules always injected as constraints
    rules = cache.get("operating_rules", [])
    constraints_block = "\n".join(f"  - {r}" for r in rules)

    # Build the supercharged prompt
    prompt = f"""TASK
{raw_message}

CATEGORY: {category}
AGENT: {route['agent']}
CWD: {route['cwd']}

CONTEXT
{context_block.strip()}

{priority_files}

ROUTE NOTES
{route_notes}

CONSTRAINTS
{constraints_block}

OUTPUT FORMAT
- Execute immediately without asking clarifying questions
- If multiple steps are needed, complete them in order and report each completion
- Use GREEN/YELLOW/RED labels for status, never emojis
- Work inside VS Code terminal only
- Save any outputs to ~/Desktop/JARVIS_EMPIRE/3_OUTPUT/ unless a more specific path applies
- Log major completions to ~/Desktop/JARVIS_EMPIRE/COO_LOG.md"""

    raw_tokens = estimate_tokens(raw_message)
    full_context_tokens = estimate_tokens(json.dumps(cache))
    prompt_tokens = estimate_tokens(prompt)
    tokens_saved = full_context_tokens - prompt_tokens

    result = {
        "category": category,
        "raw_message": raw_message,
        "supercharged_prompt": prompt,
        "agent": route["agent"],
        "cwd": route["cwd"],
        "token_stats": {
            "raw_input_tokens": raw_tokens,
            "supercharged_tokens": prompt_tokens,
            "full_context_tokens": full_context_tokens,
            "tokens_saved": max(0, tokens_saved),
            "savings_pct": round(max(0, tokens_saved) / full_context_tokens * 100) if full_context_tokens > 0 else 0
        }
    }

    return result


if __name__ == "__main__":
    import sys
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "check status"
    result = supercharge(msg, "OPS", verbose=True)
    print(result["supercharged_prompt"])

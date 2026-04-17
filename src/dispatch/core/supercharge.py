"""Prompt enhancement engine — pure port of the legacy ``supercharge.py``.

The function signature takes loaded ``routes`` and ``cache`` dicts so it stays
I/O-free; callers are responsible for reading JSON.
"""

from __future__ import annotations

import json
from typing import Any


_DEFAULT_CATEGORY = "OPS"


def estimate_tokens(text: str) -> int:
    """Rough estimate: 4 chars = 1 token."""
    return len(text) // 4


def extract_context_sections(cache: dict, sections: list[str]) -> dict:
    """Return the subset of ``cache`` matching the requested section keys."""
    return {k: cache[k] for k in sections if k in cache}


def format_context_block(context: dict) -> str:
    """Render the context dict into the legacy ``[HEADER]`` block format."""
    lines: list[str] = []
    for key, val in context.items():
        header = key.upper().replace("_", " ")
        if isinstance(val, dict):
            lines.append(f"[{header}]")
            for sub_key, sub_val in val.items():
                if isinstance(sub_val, dict):
                    lines.append(f"  {sub_key}:")
                    for leaf_key, leaf_val in sub_val.items():
                        lines.append(f"    {leaf_key}: {leaf_val}")
                elif isinstance(sub_val, list):
                    rendered = ", ".join(str(item) for item in sub_val)
                    lines.append(f"  {sub_key}: {rendered}")
                else:
                    lines.append(f"  {sub_key}: {sub_val}")
        elif isinstance(val, list):
            lines.append(f"[{header}]")
            for item in val:
                lines.append(f"  - {item}")
        else:
            lines.append(f"[{header}] {val}")
        lines.append("")
    return "\n".join(lines)


def format_priority_files(files: list[str]) -> str:
    """Render the ``priority_files`` bullet list; empty string when none."""
    if not files:
        return ""
    return "Priority files to read first:\n" + "\n".join(f"  - {f}" for f in files)


def supercharge(
    raw_message: str,
    category: str,
    routes: dict[str, dict],
    cache: dict,
) -> dict[str, Any]:
    """Return a supercharged prompt dict with identical shape to the legacy port.

    Keys: ``category``, ``raw_message``, ``supercharged_prompt``, ``agent``,
    ``cwd``, and ``token_stats`` (with ``raw_input_tokens``, ``supercharged_tokens``,
    ``full_context_tokens``, ``tokens_saved``, ``savings_pct``).
    """
    resolved_category = category if category in routes else _DEFAULT_CATEGORY
    # Fall back once more if OPS itself is missing — pick any available category.
    if resolved_category not in routes:
        if not routes:
            raise ValueError("routes must contain at least one category")
        resolved_category = next(iter(routes))

    route = routes[resolved_category]
    context_sections = route.get("context_sections", [])
    relevant_context = extract_context_sections(cache, context_sections)
    context_block = format_context_block(relevant_context)
    priority_files = format_priority_files(route.get("priority_files", []))
    route_notes = route.get("notes", "")

    rules = cache.get("operating_rules", [])
    constraints_block = "\n".join(f"  - {r}" for r in rules)

    prompt = f"""TASK
{raw_message}

CATEGORY: {resolved_category}
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
    savings_pct = (
        round(max(0, tokens_saved) / full_context_tokens * 100)
        if full_context_tokens > 0
        else 0
    )

    return {
        "category": resolved_category,
        "raw_message": raw_message,
        "supercharged_prompt": prompt,
        "agent": route["agent"],
        "cwd": route["cwd"],
        "token_stats": {
            "raw_input_tokens": raw_tokens,
            "supercharged_tokens": prompt_tokens,
            "full_context_tokens": full_context_tokens,
            "tokens_saved": max(0, tokens_saved),
            "savings_pct": savings_pct,
        },
    }

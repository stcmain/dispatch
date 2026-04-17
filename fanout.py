#!/usr/bin/env python3
"""Legacy shim — re-exports ``enrich``, ``write_broadcast``, ``write_targeted``.

The real implementation now lives in ``src/dispatch``. This module keeps the
command-line interface (``python3 fanout.py ...``) working for backwards
compatibility with existing scripts (e.g. ``speak.sh``).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from dispatch.commands.exec_cmd import run_exec  # type: ignore  # noqa: E402
from dispatch.core.enrich import enrich  # type: ignore  # noqa: E402,F401
from dispatch.io.inbox import write_broadcast, write_targeted  # type: ignore  # noqa: E402,F401


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="STC dispatcher fan-out")
    parser.add_argument("message", nargs="*", help="Short message to enrich")
    parser.add_argument(
        "--target",
        help="Comma-separated session names; writes INBOX_<NAME>.md for each",
    )
    parser.add_argument(
        "--broadcast",
        action="store_true",
        help="All-hands broadcast to BROADCAST.md (default behavior)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Skip enrichment, write message as-is",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not args.message and sys.stdin.isatty():
        print("empty message", file=sys.stderr)
        return 1

    raw = " ".join(args.message).strip() if args.message else sys.stdin.read().strip()
    if not raw:
        print("empty message", file=sys.stderr)
        return 1

    targets = None
    if args.target:
        targets = [name.strip() for name in args.target.split(",") if name.strip()]

    try:
        result = run_exec(raw, targets, raw=args.raw, workspace=None)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for path in result.get("paths", []):
        label = "WROTE" if targets else "BROADCAST"
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

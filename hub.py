#!/usr/bin/env python3
"""Legacy shim — delegates to dispatch.commands.repl.

The package at ``src/dispatch`` is the source of truth. This file remains so
that ``python3 hub.py`` and existing ``speak.sh`` invocations keep working.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from dispatch.commands.repl import run_repl  # type: ignore  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_repl())

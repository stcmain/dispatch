#!/usr/bin/env bash
# speak.sh — launcher for the STC Dispatcher HUB REPL.
# Run in the VSCode integrated terminal; dictate with macOS Fn-Fn.
set -euo pipefail

cd "$(dirname "$0")"

PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

# Load SSL cert file from .env (switcher/enricher needs it)
if [[ -f "../.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source ../.env 2>/dev/null || true; set +a
fi

# Prefer the installed `dispatch` CLI if available on PATH; otherwise fall
# back to the local src tree via `python -m dispatch`.
if command -v dispatch >/dev/null 2>&1; then
  exec dispatch "$@"
else
  export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
  exec "$PY" -m dispatch "$@"
fi

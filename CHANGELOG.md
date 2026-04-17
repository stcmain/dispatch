# Changelog

All notable changes to `dispatch-cli` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Textual-based TUI (`dispatch tui`)
- Pro tier: cloud sync, team inboxes, license verifier
- Homebrew tap published
- PyPI release

## [0.1.0] — 2026-04-16

### Added
- Hub-and-spoke dispatcher: classify → supercharge → fan out
- `dispatch` CLI powered by Typer, entry point `dispatch`
- Subcommands: `exec`, `repl`, `status`, `log`, `routes`, `init`, `version`
- 16 stock routes in `routes.json` (CODE, CONTENT, OPS, MUSIC, BETTING, JOBS, etc.)
- Keyword-based classification with CODE / CONTENT / OPS fallbacks
- Supercharge engine: 3-10 raw words → 400-700 token agent-ready prompt
  (60-75% savings vs full context dump)
- Targeted fanout via `--target <session>,<session>` writes `INBOX_<NAME>.md`
- Broadcast fanout writes `BROADCAST.md` with "Acknowledge in INBOX_STATUS.md" footer
- JSONL dispatch log with per-call token stats
- REPL with grammar: `@prefix`, `/target`, `/broadcast`, `/raw`, `/last`, `/status`, `/inbox`, `/log`, `/routes`, `/help`, `/quit`
- Python package `src/dispatch/` with `hatchling` build backend
- Legacy shims preserve compatibility with prior `hub.py` / `fanout.py` call sites
- MIT license, PEP 621 metadata, Python ≥3.10 support

### Tests
- 17 pytest tests across classify, supercharge, inbox, CLI (all passing)

[Unreleased]: https://github.com/shifttheculture/dispatch/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shifttheculture/dispatch/releases/tag/v0.1.0

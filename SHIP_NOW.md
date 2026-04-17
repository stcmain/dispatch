# SHIP_NOW — dispatch-cli 0.1.0

**Status: SHIPPED to GitHub Releases.** v0.1.0 live as of 2026-04-17.

## Live right now

- Repo: https://github.com/stcmain/dispatch
- Release: https://github.com/stcmain/dispatch/releases/tag/v0.1.0
- Wheel: `dispatch_cli-0.1.0-py3-none-any.whl` attached
- Sdist: `dispatch_cli-0.1.0.tar.gz` attached
- CI: matrix py3.10–3.13 green

Install command anyone can run today:

```bash
pip install https://github.com/stcmain/dispatch/releases/download/v0.1.0/dispatch_cli-0.1.0-py3-none-any.whl
dispatch version
dispatch init ./myworkspace
```

## What's still pending — ZP's account-gated steps

### PyPI (optional upgrade path)

Right now install is via GitHub Releases URL. Cleaner install (`pip install dispatch-cli`) requires PyPI publish, which needs your PyPI account.

Whatever screen you're on, one of these three tabs handles it:

1. **Account exists, forgot password** → `pypi.org/account/password-reset/` (tab open)
2. **Have creds, just log in** → `pypi.org/account/login/` (tab open)
3. **No account** → `pypi.org/account/register/` (tab open, needs email verification)

Once logged in:

- Go to `pypi.org/manage/account/publishing/`
- **Add pending publisher** with:
  - Project name: `dispatch-cli`
  - Owner: `stcmain`
  - Repository: `dispatch`
  - Workflow filename: `release.yml`
  - Environment: `pypi`

Then tell me "pypi set" and I'll retag (v0.1.1) to re-trigger publish. The
workflow is already wired — the trusted publisher form is the last gate.

### Homebrew tap (later)

Tap repo already exists at `github.com/stcmain/homebrew-dispatch`. After PyPI
is live, I can auto-fill the formula's sha256 and push the formula. Users
then get `brew tap stcmain/dispatch && brew install dispatch`.

## What changed this session

| Pass | Change |
|---|---|
| Phase 1 | Fixed hardcoded path in init_cmd.py (was ship-blocker) |
| Phase 1 | Bundled routes.json via hatch force-include |
| Phase 1 | Coverage 49% → 85% (added test_init_cmd, test_log, test_repl) |
| Phase 1 | `dispatch init` verified in clean venv |
| Phase 2 | Initialized git in `dispatcher/`, pushed to stcmain/dispatch |
| Phase 2 | Created GitHub env `pypi` via API |
| Phase 2 | Decoupled github-release from publish-pypi (continue-on-error) |
| Phase 2 | Tagged + pushed v0.1.0 — full release workflow ran |
| Phase 2 | GitHub Release v0.1.0 published with wheel+sdist |

## 5 Chrome tabs open for you now

1. `github.com/stcmain/dispatch/releases/tag/v0.1.0` — see the live release
2. `pypi.org/account/login/`
3. `pypi.org/account/password-reset/`
4. `pypi.org/account/register/`
5. `github.com/stcmain/dispatch/actions` — watch workflows

Go back to the work you had queued. When you want PyPI finalized, say the word.

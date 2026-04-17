# SHIP_NOW — dispatch-cli 0.1.0

Status as of 2026-04-17:

- Packaging kit: done
- Wheel + sdist: built, bundles routes.json correctly
- Tests: 44 pass, coverage 85%
- Git repo: initialized, first commit `de22a9b` on `main`
- Chrome tabs: 5 opened in MAIN profile for the steps below

## What ZP needs to tap through (5 tabs already open)

### 1. `github.com/login/device` — authenticate `gh` CLI

In VSCode integrated terminal, run:

```bash
gh auth login --web --git-protocol https --hostname github.com
```

It prints a one-time code — paste into the browser tab.

### 2. Create `stcmain/dispatch` repo

Tab: `github.com/organizations/stcmain/repositories/new`

- Name: `dispatch`
- Description: `Hub-and-spoke AI dispatcher — classify → supercharge → fanout`
- Public
- Do NOT init with README/LICENSE (we already have them)

Then, from `~/Desktop/JARVIS_EMPIRE/dispatcher`:

```bash
git remote add origin https://github.com/stcmain/dispatch.git
git push -u origin main
git tag v0.1.0 && git push origin v0.1.0
```

The `v0.1.0` tag triggers `.github/workflows/release.yml` which builds
the wheel and publishes to PyPI (once step 3 is done).

### 3. Register the PyPI trusted publisher

Tab: `pypi.org/manage/account/publishing/`

Fill the **pending publisher** form:

| Field | Value |
|---|---|
| PyPI project name | `dispatch-cli` |
| Owner | `stcmain` |
| Repository | `dispatch` |
| Workflow filename | `release.yml` |
| Environment name | `pypi` |

(Optional) Repeat on `test.pypi.org/manage/account/publishing/` to dry-run.

### 4. (Optional) Create the Homebrew tap repo

Tab: `github.com/new?name=homebrew-dispatch` (third tab opened)

- Name: `homebrew-dispatch`
- Public
- README only

Then after v0.1.0 hits PyPI:

```bash
cd /tmp
git clone https://github.com/stcmain/homebrew-dispatch.git
cp ~/Desktop/JARVIS_EMPIRE/dispatcher/packaging/homebrew/dispatch.rb \
   homebrew-dispatch/Formula/dispatch.rb
cd homebrew-dispatch
brew update-python-resources Formula/dispatch.rb  # fills sha256 blocks
git add Formula/dispatch.rb && git commit -m "dispatch 0.1.0"
git push
```

Users then get it via:

```bash
brew tap stcmain/dispatch
brew install dispatch
```

## Smoke test the shipped wheel locally

```bash
cd /tmp && python3 -m venv verify && source verify/bin/activate
pip install ~/Desktop/JARVIS_EMPIRE/dispatcher/dist/dispatch_cli-0.1.0-py3-none-any.whl
dispatch version
dispatch init ./demo
ls demo/.dispatch/routes.json   # must exist
```

## What changed in this pass

- Fixed hardcoded absolute path in `init_cmd.py` (ship-blocker)
- Bundled `routes.json` as package data via hatch `force-include`
- Added `tests/test_init_cmd.py`, `tests/test_log.py`, `tests/test_repl.py`
- Coverage 49% → 85%
- Initialized dedicated git repo inside `dispatcher/`
- `.gitignore` excludes internal `CLAUDE.md`

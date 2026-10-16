# STC DISPATCHER — HUB & SPOKE OPERATING GUIDE

**One prompt window → 8 running agents execute in their own context.**

---

## THE MODEL

```
     ┌────────────────────────┐
     │  ZP types 3-10 words   │
     │  in the HUB window     │
     └───────────┬────────────┘
                 │
                 ▼
     ┌────────────────────────┐
     │  fanout.py             │
     │  ├─ classify (routes)  │
     │  ├─ supercharge (ctx)  │
     │  └─ write to inbox     │
     └───────────┬────────────┘
                 │
     ┌───────────┼───────────────────────┐
     ▼           ▼                       ▼
 BROADCAST.md   INBOX_CODE.md       INBOX_CONTENT.md
 (all agents)   (code session)      (content session)  ...
     │           │                       │
     ▼           ▼                       ▼
  Each session on its next turn reads its inbox,
  executes within its own context + tool allowances,
  acknowledges in INBOX_STATUS.md.
```

**Why this beats N-way chat:** each spoke executes with its own full context. The hub only stores 3-10 word prompts. Token cost stays flat.

---

## HUB WORKFLOW (this session)

```bash
cd ~/Desktop/JARVIS_EMPIRE/dispatcher

# Broadcast to all sessions
python3 fanout.py "refresh revenue dashboard"

# Target specific sessions
python3 fanout.py --target code,content "draft 3 captions for futuredigitalmusic"

# Raw mode (skip enrichment — use when you already wrote a full prompt)
python3 fanout.py --raw --broadcast "all clear: plan limits roll to paid usage. Stay on default model + settings. Do not switch models."
```

The enricher produces 400-700 token prompts from 3-10 word inputs → 60-75% token savings vs full context injection.

---

## SPOKE WORKFLOW (each of your 8 sessions)

Paste this **once** per session. Treat it like a `.zshrc` for the agent:

```
You are one of N running Claude sessions under a hub dispatcher.
Before each new turn, read ~/Desktop/JARVIS_EMPIRE/dispatcher/BROADCAST.md
and ~/Desktop/JARVIS_EMPIRE/dispatcher/INBOX_<MY_NAME>.md if it exists.
If either was updated since last turn, execute its instructions.
After completion, append one line to INBOX_STATUS.md:
  [SESSION_NAME] [ISO_TIMESTAMP] model=<X> task=<short>
Never re-fetch a dispatch you already executed (dedup by timestamp in the file).
```

Each session name by convention: `CODE`, `CONTENT`, `MUSIC`, `BETTING`, `JOBS`, `OPS`, `RESEARCH`, `DEPLOY`.

---

## COST CONTROL LAYER

The dispatcher enforces the `ai_provider_switcher.chat_tier()` rule for agent scripts:

| Tier alias | When to use | Avg cost |
|------------|-------------|----------|
| `cheap` / `fast` / `free` | classification, summaries, drafts, 90% of agent calls | $0 (LiteLLM free routes) |
| `code` | implementation, file-touching work | $0 (Cerebras qwen-coder primary) |
| `reason` / `heavy` | COO decisions, architecture | $0 (Cerebras 235B primary) |
| `opus-4-7` | high-stakes user-facing output | Anthropic credits |

**Default: everything goes through LiteLLM on localhost:4000 → free providers.** Only explicit `opus-4-7` model calls burn Anthropic credits.

---

## FILES

| File | Role |
|------|------|
| `dispatcher.py` | classify → route → log (pre-existing, untouched) |
| `supercharge.py` | inject context sections from `context_cache.json` |
| `routes.json` | category → agent mapping + keywords |
| `context_cache.json` | pre-built context sections (edit as ops evolve) |
| `fanout.py` | **NEW** — write enriched prompt to per-session or broadcast inbox |
| `BROADCAST.md` | **NEW** — all-hands dispatch target |
| `INBOX_<NAME>.md` | **NEW** — targeted per-session dispatch |
| `INBOX_STATUS.md` | **NEW** — acknowledgment backchannel |
| `dispatch_log.jsonl` | full audit trail, token stats per dispatch |

---

## ESCALATION PATH

1. Agent can't complete → writes reason to `INBOX_STATUS.md` with `blocked=<reason>`
2. Hub (this session) reads status, re-dispatches with more context OR escalates to ZP via iMessage +12313421454
3. Agent hits plan limit → **continues on paid usage automatically** (usage credits, see USAGE LIMIT POLICY below). If it stops instead: run `/status`, confirm usage credits are enabled and funded (`/usage-credits`), **do NOT switch model.**
4. LiteLLM proxy down → orchestrator auto-restarts within 15 min, direct fallback chain in `ai_provider_switcher.py` also works

---

## USAGE LIMIT POLICY (2026-10-16)

**Rule: when a session hits the plan limit, nothing changes.** Same model, same effort, same permission
mode. Overflow rolls to **usage credits** (the prepaid pay-as-you-go balance on the Claude Max subscription,
formerly "extra usage") automatically. No downgrade to Sonnet/Haiku. **Cap: $100/month.** The 2026-04-16
"switch to cheap tier" broadcast is retired.

### One-time setup (ZP, local machine)

1. Usage credits: claude.ai → **Settings → Usage → Usage credits → Enable** (`https://claude.ai/settings/usage`,
   or `/usage-credits` inside any Claude Code session). **Add funds** (prepaid, billed at standard API rates),
   **Adjust limit** → $100/month, and turn on **auto-reload** so the balance never reaches zero. A zero balance
   flips credits off on its own (`/status` reports extra usage disabled, reason `out_of_credits`) and every
   session falls back to waiting for the plan reset.
2. Pin settings in `~/.claude/settings.json` (user scope = hub + every spoke; `bypassPermissions` is ignored in
   project-level files, so it has to live here):

   ```json
   {
     "model": "claude-fable-5-1",
     "effortLevel": "high",
     "permissions": { "defaultMode": "bypassPermissions" }
   }
   ```

   `effortLevel` (`low`/`medium`/`high`/`xhigh`) in user settings is honored by Fable 5.1; `/effort` writes
   per-model overrides to `modelSettings`. Verify in a fresh session with `/status`.
3. Keep `ANTHROPIC_API_KEY` **unset** in every shell that launches Claude Code (the `claude()` wrapper in
   `~/.zshrc` already strips it). A set key silently moves the session to Console (API) billing. Check `/status`.

### What happens at the limit

- Credits on and funded: requests past the 5-hour / weekly window bill to usage credits and keep going on the
  same model. Nothing to do.
- The first Fable request that bills credits in an interactive session shows a one-time consent prompt → pick
  **continue on Fable**. Unattended sessions (Remote Control, background, agent-team teammates) hold it for
  `dialogExpiry` (5 min default) then end the turn, so answer it at the terminal. `-p` runs never ask.
- Credits off or balance $0: Claude Code blocks at the limit and **auto-continues at reset**
  (`autoContinueAtUsageLimit`, default on). That is the "it stopped" case → fund credits, do not switch model.
- Monthly cap reached: `You've hit your monthly spend limit` → raise it at claude.ai Settings → Usage, or
  answer the in-CLI raise/remove prompt.

### Where to check

| Command | Shows |
|---------|-------|
| `/usage` | session + weekly bars, usage-credits spend vs monthly limit (row hidden while credits are off) |
| `/status` | model, account, login method, setting sources |
| `/rate-limit-options` | wait / add usage credits / upgrade |
| `https://claude.ai/settings/usage` | credits on/off, balance, this month's spend, monthly limit |

### Gotchas

- Prompt-cache lifetime drops from 1 hour (subscription) to 5 minutes once a session is drawing on usage
  credits. Keep spokes busy or restart them lean.
- Cloud sessions (Claude Code on the web) share the same plan limits and use subscription credentials. The
  docs (2026-10-16) only state that usage credits cover "Claude conversations and Claude Code terminal usage";
  cloud coverage is unconfirmed. Confirm on the first cloud limit hit and update this line.
- Max's included monthly API credits cannot be used for usage credits or in Claude Code.
- `-p` (print mode) and background sessions never auto-wait; they stop at the limit (credits still apply).

### Rollout

After setup, broadcast to every spoke so the old downgrade rule is dropped:

```bash
python3 fanout.py --raw --broadcast "all clear: plan limits roll to paid usage. Stay on default model + settings. Do not switch models."
```

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
python3 fanout.py --raw --broadcast "switch to cheap tier until credits refresh"
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
  [SESSION_NAME] [ISO_TIMESTAMP] model=<X> task=<short> switched=<yes/no>
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
3. Agent hits the Claude plan usage limit → **do not switch model.** Claude Code either waits and auto-continues at reset, or continues immediately on usage credits (see USAGE LIMIT POLICY below). If it stalls, run `/rate-limit-options` → add usage credits. Acknowledge with `switched=no`.
4. LiteLLM proxy down → orchestrator auto-restarts within 15 min, direct fallback chain in `ai_provider_switcher.py` also works

---

## USAGE LIMIT POLICY (2026-10-16)

**Rule: when a session hits the plan limit, nothing changes.** Same model, same effort, same permission
mode. Overflow bills to **usage credits** (the pay-as-you-go balance on the Claude subscription, formerly
called "extra usage"). No downgrade to Sonnet/Haiku. The 2026-04-16 "switch to cheap tier" broadcast is
retired.

### One-time setup (ZP, local machine)

1. Turn on usage credits: claude.ai → **Settings → Usage → Usage credits → Enable**
   (`https://claude.ai/settings/usage`, or type `/usage-credits` inside any Claude Code session).
   Add a payment method, **Add funds** (prepaid), set a monthly spend limit. Billed at standard API rates,
   separate from the subscription. Pro and Max users enable this themselves; Team/Enterprise admins do it
   under Organization settings → Usage.
2. Pin settings in `~/.claude/settings.json` (user scope, applies to hub + every spoke; `bypassPermissions`
   is ignored in project-level files, so it has to live here):

   ```json
   {
     "model": "<the model /model shows as your current default>",
     "permissions": { "defaultMode": "bypassPermissions" },
     "env": { "CLAUDE_CODE_EFFORT_LEVEL": "xhigh" },
     "autoContinueAtUsageLimit": true
   }
   ```

   `CLAUDE_CODE_EFFORT_LEVEL` outranks `--effort`, `/effort` and the `effortLevel` key, so it holds across
   every model. Verify in a fresh session with `/status` (model, login method, setting sources).
3. Keep `ANTHROPIC_API_KEY` **unset** in every shell that launches Claude Code. A set key silently moves the
   session to Console (API) billing, with no automatic fallback back to the subscription. Check `/status`.

### What happens at the limit

- Claude Code blocks at the session (5-hour) or weekly limit, shows the reset time, and by default
  **auto-continues** when the window resets.
- With usage credits funded, the limit screen offers `/usage-credits to continue now`; Claude Code picks the
  credits up and continues on the same model. Fable is the one exception: it asks for consent before billing
  credits, so answer the prompt.
- Family limits (Opus-only, Sonnet-only, Max's weekly Fable limit) are separate from the shared session
  and weekly limits.

### Where to check

| Command | Shows |
|---------|-------|
| `/usage` | session + weekly bars, plan breakdown, usage-credits spend vs monthly limit |
| `/status` | model, account, login method, setting sources |
| `/rate-limit-options` | wait / add usage credits / upgrade |
| `https://claude.ai/settings/usage` | credits on/off, balance, this month's spend, monthly limit |

### Gotchas

- Prompt-cache lifetime drops from 1 hour (subscription) to 5 minutes once a session is drawing on usage
  credits. A big session resumed after a break re-reads more context. Keep spokes busy or restart them lean.
- Cloud sessions (Claude Code on the web) always use subscription credentials, count toward the same plan
  limits, and ignore `apiKeyHelper` / `ANTHROPIC_API_KEY`. Whether usage credits cover cloud sessions is not
  stated in the docs as of 2026-10-16. Confirm on the first cloud limit hit and update this line.
- Max's included monthly API credits cannot be used for usage credits or in Claude Code.
- `-p` (print mode) and background sessions never auto-continue; they stop at the limit.

### Rollout

After setup, broadcast to every spoke so the old downgrade rule is dropped:

```bash
python3 fanout.py --raw --broadcast "all clear: plan limits roll to usage credits. Stay on default model + settings. Do not switch models. Ack switched=no."
```

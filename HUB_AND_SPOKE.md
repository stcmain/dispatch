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
3. Agent rate-limited on Anthropic → switch model in-session via `/model`, acknowledge with `switched=yes`
4. LiteLLM proxy down → orchestrator auto-restarts within 15 min, direct fallback chain in `ai_provider_switcher.py` also works

---

## CURRENT CONSTRAINT (2026-04-16)

- Anthropic API credits: ~$10 shared across 8 agents
- Default settings: Opus 4.7 + bypass permissions + high effort
- **Action active in BROADCAST.md** — all sessions directed to switch to Sonnet 4.6/Haiku 4.5 or tier aliases

When credits refresh or increase: update `BROADCAST.md` with "all clear" message and fan out.

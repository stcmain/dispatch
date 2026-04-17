# dispatch

> Short message in. Context-rich agent prompt out.

`dispatch` is a hub-and-spoke CLI that turns 3-10 word human messages into
400-700 token agent-ready prompts, then fans them out to one or more agent
inboxes as markdown. It is the last thing you type before the agent does the
work.

**Why it exists:** typing a 200-word structured prompt every time you need an
agent to do something is slow. Typing `fix the website` and letting `dispatch`
classify, enrich with cached project context, and route the result is fast.
In practice this is a **60-75% token saving** vs dumping full context on
every dispatch.

Built by [Shift The Culture](https://shifttheculture.media).

---

## Install

```bash
# via pipx (recommended — isolated)
pipx install dispatch-cli

# or via pip
pip install dispatch-cli

# or from source
git clone https://github.com/shifttheculture/dispatch
cd dispatch
pip install -e .
```

Requires Python ≥3.10.

---

## Quickstart

```bash
# Classify + enrich + broadcast to all spoke inboxes
dispatch exec "fix the website"

# Target a specific inbox
dispatch exec "draft launch post" --target content

# Target multiple inboxes
dispatch exec "ship the release" --target code,ops,deploy

# Interactive REPL
dispatch repl

# Show current workspace state
dispatch status

# Tail the dispatch log
dispatch log --tail 20

# List all routes
dispatch routes
```

---

## How It Works

```
  raw input (3-10 words)
          │
          ▼
  ┌──────────────┐
  │  classify    │  keyword scoring across routes.json
  └──────┬───────┘
         │ category (CODE / CONTENT / OPS / ...)
         ▼
  ┌──────────────┐
  │  supercharge │  pull matching context sections from cache
  └──────┬───────┘  render structured prompt (agent / cwd / files / notes)
         │
         ▼
  ┌──────────────┐
  │  fan out     │  write BROADCAST.md or INBOX_<NAME>.md
  └──────────────┘
```

Each dispatch is logged to `dispatch_log.jsonl` with raw input, category,
agent, and token stats (raw / supercharged / full-context / saved).

---

## Configuration

`dispatch` reads from a workspace directory. By default this is the current
directory; override with `--workspace <path>` or `DISPATCH_WORKSPACE=<path>`.

A workspace contains:

| File | Purpose |
|------|---------|
| `routes.json` | Category → keywords + agent + context sections map |
| `context_cache.json` | Pre-built context snippets injected per category |
| `BROADCAST.md` | Auto-written on broadcast dispatches |
| `INBOX_<NAME>.md` | Auto-written on targeted dispatches |
| `dispatch_log.jsonl` | Append-only JSONL dispatch history |

Bootstrap a new workspace:

```bash
dispatch init my-workspace
cd my-workspace
dispatch exec "hello world"
```

---

## Adding a Route

Edit `routes.json`:

```json
{
  "PODCAST": {
    "description": "Podcast production tasks",
    "keywords": ["podcast", "episode", "mic", "edit audio"],
    "agent": "Audio producer agent",
    "cwd": "~/Media/podcast",
    "context_sections": ["podcast_pipeline", "brand_voice"],
    "priority_files": ["SHOW_NOTES.md", "episode_template.md"]
  }
}
```

No code change required. Classification and supercharge read `routes.json` on
every call.

---

## REPL Grammar

```
> fix the website                 # one-shot, broadcast to all inboxes
> @code: deploy the staging build # target the CODE inbox
> /target content,ops rewrite bio # target multiple
> /broadcast all hands             # force broadcast
> /raw show the prompt without sending
> /last  repeat last dispatch
> /status  show workspace state
> /inbox code  read INBOX_CODE.md
> /log  tail last 10 dispatches
> /routes  list available routes
> /help
> /quit
```

---

## Token Economics

For a typical workspace with ~1,800 tokens of cached context:

| Mode | Tokens per dispatch | Savings |
|------|--------------------|---------|
| Raw input only | ~10 | (no context — agent asks questions) |
| Full context dump | ~4,800 | 0% |
| `dispatch` supercharged | ~400-700 | **60-75%** |

---

## Development

```bash
git clone https://github.com/shifttheculture/dispatch
cd dispatch
uv venv
uv pip install -e ".[dev]"
pytest tests/
```

## License

MIT. See [LICENSE](LICENSE).

---

*Built in Nashville by [Shift The Culture](https://shifttheculture.media).*

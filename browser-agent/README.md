# Task 3: Browser Automation Agent

A FastAPI service that accepts a natural-language task and drives a Playwright browser using Claude via a tool-use loop. Claude decides which browser actions to take (navigate, click, type, search, extract) until it produces a final answer or hits the step limit.

## Architecture

```
POST /run-task
    └─> ClaudeClient (OpenAI-compat via litellm-proxy)
            └─> tool-use loop
                    ├─ search(query)       → DuckDuckGo HTML search
                    ├─ navigate(url)       → Playwright goto
                    ├─ extract_text()      → page body text (≤8000 chars)
                    ├─ click(selector)     → Playwright click
                    ├─ type_text(sel,text) → Playwright fill
                    └─ done(answer)        → terminates loop
```

The agent depends on **litellm-proxy** (Task 1) as its Claude backend.

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- litellm-proxy running (locally or deployed)
- `LITELLM_URL` and `LITELLM_MASTER_KEY` set in environment

## Local Setup

```bash
cd browser-agent
uv venv && uv pip install -e ".[dev]"
uv run playwright install chromium
```

## Run Service

```bash
LITELLM_URL=http://localhost:4000 \
LITELLM_MASTER_KEY=sk-1234 \
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Via Docker

```bash
docker build -t vici-browser-agent .
docker run -d --rm -p 8000:8000 \
  -e LITELLM_URL=http://host.docker.internal:4000 \
  -e LITELLM_MASTER_KEY=sk-1234 \
  vici-browser-agent
```

## Run Tests

```bash
# Unit tests (no service needed)
uv run pytest tests/ -v -m "not integration"

# Integration tests (service + litellm-proxy must be running)
uv run pytest tests/ -v
```

## Usage

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"browser-agent"}
```

### Run a task

```bash
curl -X POST http://localhost:8000/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is the current version of Python?",
    "max_steps": 10
  }'
```

Response:

```json
{
  "task_id": "abc-123",
  "status": "completed",
  "result": "The current stable Python version is 3.12.x.",
  "steps_taken": 3,
  "logs": [
    {"step": 1, "action": "search", "input": {"query": "current Python version"}, "output": "..."},
    {"step": 2, "action": "navigate", "input": {"url": "https://python.org"}, "output": "..."},
    {"step": 3, "action": "done", "input": {"answer": "The current stable Python version is 3.12.x."}, "output": "..."}
  ]
}
```

## Zeabur Deployment

1. Push to GitHub
2. Create new project in Zeabur, connect repo, select `browser-agent/` subfolder
3. Set env vars in Zeabur dashboard:
   - `LITELLM_URL` — deployed litellm-proxy URL
   - `LITELLM_MASTER_KEY` — your chosen master key
   - `LITELLM_MODEL` — model name (default: `claude-cli`)
4. Zeabur auto-detects Dockerfile and deploys

## Bot Detection Evasion

The agent uses [`playwright-stealth`](https://github.com/AtuboDad/playwright_stealth) to avoid being blocked by sites that detect headless browsers:

- **JS fingerprint patching** — `Stealth().use_async(page)` patches `navigator.webdriver`, WebGL vendor/renderer, plugin lists, and other JS properties that reveal headless Chrome
- **Real User-Agent** — uses a macOS Chrome 120 User-Agent string instead of the default headless one
- **Headless mode retained** — stealth patches work with `headless=True`, so deployment compatibility is unchanged

This significantly improves success rates on DuckDuckGo, ESPN, and other bot-aware sites.

## Key Assumptions

- Uses DuckDuckGo HTML endpoint for search (no API key required)
- Page text is truncated to 8000 characters per extraction to stay within context limits
- The `done` tool terminates the loop early; if not called within `max_steps`, returns `max_steps_reached`
- Claude model must support tool use (function calling)

## AI Workflow Notes

Built with Claude Code using the `writing-plans` skill, then implemented task-by-task with strict TDD (red → green cycles in git history).

# Task 1: Claude CLI → LiteLLM Endpoint

Wraps the `claude` CLI tool into an OpenAI-compatible endpoint via a LiteLLM `CustomLLM` provider. The proxy exposes `/v1/chat/completions`, supporting both streaming and non-streaming requests.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) for Python environment management
- [claude CLI](https://docs.anthropic.com/claude/docs/claude-cli) installed and accessible in PATH
- `ANTHROPIC_API_KEY` set in your environment

## Local Setup

```bash
cd task1
uv venv && uv pip install -e ".[dev]"
cp .env.example .env  # fill in values
```

## Run Proxy

**Locally:**

```bash
uv run litellm --config config.yaml
```

**Via Docker (recommended):**

```bash
docker build -t vici-task1 .
docker run -d --rm -p 4000:4000 --env-file .env vici-task1
```

The proxy starts at `http://localhost:4000`.

> **Note:** When running via Docker, always use `--env-file .env` to pass `ANTHROPIC_API_KEY`. The container's Claude CLI reads it from the environment.

## Run Tests

```bash
# Unit tests (no proxy needed, ~2s)
uv run python -m pytest tests/ -v -m "not integration"

# Integration tests (proxy must be running on localhost:4000)
uv run python -m pytest tests/test_proxy.py -v
```

## Usage

### Non-streaming request

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-cli","messages":[{"role":"user","content":"Say hi"}]}'
```

### Streaming request

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-cli","messages":[{"role":"user","content":"Count 1 2 3"}],"stream":true}'
```

### LiteLLM client config (for using deployed URL)

```yaml
model_list:
  - model_name: claude-via-proxy
    litellm_params:
      model: openai/claude-cli
      api_base: https://<your-app>.zeabur.app
      api_key: os.environ/LITELLM_MASTER_KEY
```

## Zeabur Deployment

1. Push code to GitHub
2. Create new project in Zeabur, connect your repo
3. Set env vars in Zeabur dashboard:
   - `LITELLM_MASTER_KEY` — your chosen master key
   - `ANTHROPIC_API_KEY` — your Anthropic API key
4. Zeabur auto-detects Dockerfile and deploys

## Key Assumptions

- The `claude` CLI is available at `$CLAUDE_PATH` (default: `claude`)
- Claude CLI auth uses `ANTHROPIC_API_KEY` environment variable
- Model names are passed as `claude-cli/<model>` (provider prefix stripped before invoking CLI)
- Timeout for CLI calls: 120 seconds
- `_SUBPROCESS_ENV` must be `dict(os.environ)` — uvloop (used inside the Docker container) rejects `os.environ` directly as it expects a plain `dict`

## AI Workflow Notes

Built entirely with Claude Code using the writing-plans skill for architecture, then executing the plan task-by-task with full TDD workflow (red → green cycles evidenced in git history).                      

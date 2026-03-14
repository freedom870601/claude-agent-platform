# VICI Take-Home Tasks

Three advanced tasks demonstrating AI-assisted development with full TDD workflow, deployed online.

## Tasks

| Task | Folder | Description | Deploy |
|------|--------|-------------|--------|
| 1 | `litellm-proxy/` | Wrap Claude CLI into a LiteLLM-compatible OpenAI endpoint | Zeabur |
| 2 | `github-skills/` | Package GitHub CI/CD workflows as Claude Code Skills | — |
| 3 | `browser-agent/` | Browser automation agent driven by Claude via tool-use loop | Zeabur |

## Quick Start

Each task has its own `pyproject.toml` and `.venv`. Use `uv` throughout.

```bash
# Task 1
cd litellm-proxy && uv run litellm --config config.yaml

# Task 2
cd github-skills && uv run pytest tests/ -v

# Task 3
cd browser-agent && uv run uvicorn app.main:app --reload
```

See each subfolder's `README.md` for full setup, usage, and deployment instructions.

## AI Workflow

All tasks were built with Claude Code using:
- `writing-plans` skill for upfront architecture
- Strict TDD: failing test committed first, implementation second (evidenced in git history)
- `git-commit` skill for conventional commit messages

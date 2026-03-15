# VICI Take-Home Tasks

Three advanced tasks demonstrating AI-assisted development with full TDD workflow, deployed online.

## Completion Status (as of 2026-03-14)

| Task | Folder | Status | Unit Tests | Integration Tests | Deploy |
|------|--------|--------|-----------|-------------------|--------|
| 1 | `litellm-proxy/` | ✅ Complete | 28 passing | 5 (marked, require running service) | Zeabur (port 8080) |
| 2 | `github-skills/` | ✅ Complete | 13 passing | — | Local skill files |
| 3 | `browser-agent/` | ✅ Complete | 32 passing | 1 (marked, requires litellm-proxy) | Zeabur (port 8080) |

**Total: 73 unit tests passing across all tasks. All CI checks green.**

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

## CI/CD via GitHub Skills

Three GitHub Actions workflows back the Task 2 skills:

| Workflow | File | Trigger | Skills |
|----------|------|---------|--------|
| Test | `.github/workflows/test.yml` | Every push + `workflow_dispatch` | `/gh-test` |
| Lint | `.github/workflows/lint.yml` | Every push + `workflow_dispatch` | `/gh-lint` |
| Deploy | `.github/workflows/deploy.yml` | `workflow_dispatch` only | `/gh-deploy` |

### Install Skills

In this repo, `.claude/commands/` is a symlink to `github-skills/skills/` — no copying needed. Skills and slash commands stay in sync automatically.

For other repos, symlink or curl:

```bash
# Symlink (recommended)
ln -s /path/to/claude-agent-platform/github-skills/skills .claude/commands

# Or curl individual files
REPO="https://raw.githubusercontent.com/freedom870601/claude-agent-platform/main"
mkdir -p .claude/commands
for skill in gh-lint gh-test gh-deploy gh-status; do
  curl "$REPO/github-skills/skills/${skill}.md" -o .claude/commands/${skill}.md
done
```

### Example Commands

`/gh-deploy` auto-detects `repo` (from `git remote`) and `service` (from changed files):

```
/gh-status
/gh-test
/gh-lint
/gh-deploy environment: production

# Override explicitly if needed
/gh-deploy repo: freedom870601/claude-agent-platform  service: litellm-proxy  environment: production
```

### Required GitHub Secrets

| Secret | Purpose |
|--------|---------|
| `ZEABUR_TOKEN` | Zeabur deploy token (set in repo Settings → Secrets) |

## AI Workflow

All tasks were built with Claude Code using:
- `writing-plans` skill for upfront architecture
- Strict TDD: failing test committed first, implementation second (evidenced in git history)
- `git-commit` skill for conventional commit messages

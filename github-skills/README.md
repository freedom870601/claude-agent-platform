# Task 2 — GitHub CI/CD as Claude Skills

Packages four GitHub Actions workflows as reusable Claude Code Skills backed by the `gh` CLI.

## Skills

| Skill | File | Description |
|---|---|---|
| `/gh-lint` | `skills/gh-lint.md` | Trigger lint workflow, report pass/fail |
| `/gh-test` | `skills/gh-test.md` | Trigger test suite, report results |
| `/gh-deploy` | `skills/gh-deploy.md` | Trigger deploy with `CONFIRM` gate |
| `/gh-status` | `skills/gh-status.md` | List recent workflow runs (read-only) |

## Installation

Copy skill files from this repo into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp github-skills/skills/gh-lint.md ~/.claude/skills/
```

Install all skills at once:

```bash
mkdir -p ~/.claude/skills
for skill in gh-lint gh-test gh-deploy gh-status; do
  cp github-skills/skills/${skill}.md ~/.claude/skills/
done
```

Or from a published GitHub repo:

```bash
REPO="https://raw.githubusercontent.com/laiyanru/claude-agent-platform/main"
for skill in gh-lint gh-test gh-deploy gh-status; do
  curl "$REPO/github-skills/skills/${skill}.md" -o ~/.claude/skills/${skill}.md
done
```

## Safe Execution Boundary

- Skills only issue `gh` CLI commands — no direct API calls with embedded credentials.
- `gh-deploy` requires the user to type `CONFIRM` before any workflow is dispatched.
- All commands are displayed to the user before execution.

## Validator

```bash
cd github-skills

# Run unit tests
uv run pytest tests/ -v

# Validate all skill files structurally
uv run python check_skills.py
```

## Development

```bash
cd github-skills
uv sync --extra dev
uv run pytest tests/ -v
```

## This Repo as a Live Example

`laiyanru/claude-agent-platform` uses these skills against itself. Every push
triggers `test.yml` and `lint.yml`, providing real CI run logs as verifiable output.

### Workflow → Skill mapping

| Workflow file | Skill | Notes |
|---------------|-------|-------|
| `test.yml` | `/gh-test` | Runs unit tests for all three tasks |
| `lint.yml` | `/gh-lint` | Ruff check across all task folders |
| `deploy.yml` | `/gh-deploy` | Manual dispatch; `service` input selects target |

### Full demo flow

```
# 1. Check recent runs
/gh-status repo: laiyanru/claude-agent-platform

# 2. Trigger tests on current branch
/gh-test repo: laiyanru/claude-agent-platform

# 3. Trigger lint
/gh-lint repo: laiyanru/claude-agent-platform

# 4. Deploy a specific service (CONFIRM gate required)
/gh-deploy repo: laiyanru/claude-agent-platform  service: litellm-proxy  environment: production
```

## Example: `/gh-status`

```
$ /gh-status
repo: owner/my-repo

gh run list --repo owner/my-repo --limit 10 --json workflowName,status,conclusion,createdAt,url

| Workflow | Status    | Conclusion | Created             | URL                                      |
|----------|-----------|------------|---------------------|------------------------------------------|
| CI       | completed | success    | 2026-03-14T10:22:01 | https://github.com/owner/my-repo/runs/1  |
| CI       | completed | failure    | 2026-03-13T18:05:33 | https://github.com/owner/my-repo/runs/2  |
```

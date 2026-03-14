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

### In this repo (symlink — recommended)

`.claude/commands/` is already a symlink to `github-skills/skills/`, so all skills are available as slash commands with no copying needed:

```bash
ls -la .claude/commands
# .claude/commands -> ../github-skills/skills
```

Edit files under `github-skills/skills/` and changes are instantly reflected in Claude Code.

### In another repo (symlink)

```bash
ln -s /path/to/claude-agent-platform/github-skills/skills .claude/commands
```

### From a published GitHub repo (curl)

```bash
REPO="https://raw.githubusercontent.com/freedom870601/claude-agent-platform/main"
mkdir -p .claude/commands
for skill in gh-lint gh-test gh-deploy gh-status; do
  curl "$REPO/github-skills/skills/${skill}.md" -o .claude/commands/${skill}.md
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

`freedom870601/claude-agent-platform` uses these skills against itself. Every push
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
/gh-status repo: freedom870601/claude-agent-platform

# 2. Trigger tests on current branch
/gh-test repo: freedom870601/claude-agent-platform

# 3. Trigger lint
/gh-lint repo: freedom870601/claude-agent-platform

# 4. Deploy — repo and service are auto-detected from git remote + changed files
/gh-deploy environment: production

# 4b. Override explicitly if needed
/gh-deploy repo: freedom870601/claude-agent-platform  service: litellm-proxy  environment: production
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

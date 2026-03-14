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

Install one skill:

```bash
curl https://raw.githubusercontent.com/<user>/VICI_task2/main/task2/skills/gh-lint.md \
  -o ~/.claude/skills/gh-lint.md
```

Install all skills:

```bash
for skill in gh-lint gh-test gh-deploy gh-status; do
  curl https://raw.githubusercontent.com/<user>/VICI_task2/main/task2/skills/${skill}.md \
    -o ~/.claude/skills/${skill}.md
done
```

## Safe Execution Boundary

- Skills only issue `gh` CLI commands — no direct API calls with embedded credentials.
- `gh-deploy` requires the user to type `CONFIRM` before any workflow is dispatched.
- All commands are displayed to the user before execution.

## Validator

```bash
cd task2

# Run unit tests
uv run pytest tests/ -v

# Validate all skill files structurally
uv run python check_skills.py
```

## Development

```bash
cd task2
uv sync --extra dev
uv run pytest tests/ -v
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

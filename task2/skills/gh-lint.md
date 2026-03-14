---
name: gh-lint
description: Trigger and report GitHub Actions lint workflow
version: "1.0"
inputs:
  - repo: "owner/name format"
  - branch: "target branch (default: main)"
outputs:
  - conclusion: "success | failure"
  - run_url: "link to workflow run logs"
---

Trigger the lint workflow for a GitHub repository and report pass/fail.

## Usage

When the user invokes `/gh-lint`, ask for:
- `repo` — repository in `owner/name` format (required)
- `branch` — branch to lint (default: `main`)

## Steps

1. Display the command to the user before running it.
2. Trigger the workflow:
   ```bash
   gh workflow run lint.yml --repo <repo> --ref <branch>
   ```
3. Wait briefly, then fetch the latest run:
   ```bash
   gh run list --repo <repo> --workflow lint.yml --limit 1 --json status,conclusion,url
   ```
4. Poll until `status` is `completed` (check every 10 seconds, up to 5 minutes):
   ```bash
   gh run watch <run_id> --repo <repo>
   ```
5. Report the `conclusion` (`success` or `failure`) and the `url` to the workflow run logs.

## Output

```
Lint result: success
Run URL: https://github.com/<repo>/actions/runs/<id>
```

---
name: gh-status
description: List recent GitHub Actions workflow runs (read-only)
version: "1.0"
inputs:
  - repo: "owner/name format"
  - limit: "number of runs to show (default: 10)"
outputs:
  - runs: "list of recent workflow runs with status and conclusion"
---

List recent GitHub Actions workflow runs for a repository. Read-only, no side effects.

## Usage

When the user invokes `/gh-status`, ask for:
- `repo` — repository in `owner/name` format (required)
- `limit` — number of runs to display (default: `10`)

## Steps

1. Display the command to the user before running it.
2. Fetch recent runs:
   ```bash
   gh run list --repo <repo> --limit <limit> --json workflowName,status,conclusion,createdAt,url
   ```
3. Format and display the results as a table:

   | Workflow | Status | Conclusion | Created | URL |
   |---|---|---|---|---|
   | ... | ... | ... | ... | ... |

## Output

A table of recent workflow runs sorted by creation time (newest first).

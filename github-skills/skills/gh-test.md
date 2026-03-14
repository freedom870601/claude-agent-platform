---
name: gh-test
description: Trigger test suite workflow and report results
version: "1.0"
inputs:
  - repo: "owner/name format"
  - branch: "target branch (default: main)"
outputs:
  - conclusion: "success | failure"
  - run_url: "link to workflow run logs"
---

Trigger the test workflow for a GitHub repository and report results.

## Usage

When the user invokes `/gh-test`, ask for:
- `repo` — repository in `owner/name` format (required)
- `branch` — branch to test (default: `main`)

## Steps

1. Display the command to the user before running it.
2. Trigger the workflow:
   ```bash
   gh workflow run test.yml --repo <repo> --ref <branch>
   ```
3. Fetch the latest run ID:
   ```bash
   gh run list --repo <repo> --workflow test.yml --limit 1 --json databaseId,status,conclusion,url
   ```
4. Watch until complete:
   ```bash
   gh run watch <run_id> --repo <repo>
   ```
5. Report the `conclusion` and run URL.

## Output

```
Test result: success
Run URL: https://github.com/<repo>/actions/runs/<id>
```

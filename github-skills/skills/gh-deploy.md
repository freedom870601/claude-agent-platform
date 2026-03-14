---
name: gh-deploy
description: Trigger deploy workflow with CONFIRM gate before dispatch
version: "1.0"
inputs:
  - repo: "owner/name format"
  - branch: "branch to deploy (default: main)"
  - environment: "deployment target environment (e.g. production, staging)"
  - service: "service to deploy: litellm-proxy | browser-agent | all (default: all)"
outputs:
  - conclusion: "success | failure"
  - run_url: "link to workflow run logs"
---

Trigger the deploy workflow with a mandatory confirmation step.

## Usage

When the user invokes `/gh-deploy`, ask for:
- `repo` — repository in `owner/name` format (required)
- `branch` — branch to deploy (default: `main`)
- `environment` — target environment (e.g. `production`, `staging`)
- `service` — which service to deploy: `litellm-proxy`, `browser-agent`, or `all` (default: `all`)

## Steps

1. **CONFIRM gate** — Before running anything, display:
   ```
   You are about to deploy service '<service>' on branch '<branch>' to '<environment>' in repo '<repo>'.
   Type CONFIRM to proceed, or anything else to cancel.
   ```
   Wait for user input. Only proceed if the user types exactly `CONFIRM`. Otherwise abort.

2. Display the command before running it.

3. Trigger the workflow:
   ```bash
   gh workflow run deploy.yml --repo <repo> --ref <branch> -f environment=<environment> -f service=<service>
   ```

4. Fetch the latest run:
   ```bash
   gh run list --repo <repo> --workflow deploy.yml --limit 1 --json databaseId,status,conclusion,url
   ```

5. Watch until complete:
   ```bash
   gh run watch <run_id> --repo <repo>
   ```

6. Report the `conclusion` and run URL.

## Output

```
Deploy result: success
Run URL: https://github.com/<repo>/actions/runs/<id>
```

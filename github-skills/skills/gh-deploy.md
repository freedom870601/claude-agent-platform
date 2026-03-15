---
name: gh-deploy
description: Trigger deploy workflow with CONFIRM gate before dispatch
version: "1.0"
inputs:
  - repo: "owner/name format"
  - branch: "branch to deploy (default: main)"
  - environment: "deployment target environment (e.g. production, staging)"
  - service: "service to deploy: litellm-proxy | browser-agent (required — no default)"
outputs:
  - conclusion: "success | failure"
  - run_url: "link to workflow run logs"
---

Trigger the deploy workflow with a mandatory confirmation step.

## Usage

When the user invokes `/gh-deploy`:

### Auto-detect `repo`
If `repo` was not supplied, run:
```bash
git remote get-url origin
```
Parse `owner/name` from the output:
- HTTPS: `https://github.com/owner/name.git` → `owner/name`
- SSH: `git@github.com:owner/name.git` → `owner/name`

### Auto-detect `service`
If `service` was not supplied, run:
```bash
git diff --name-only HEAD~1
```
Map changed paths to a service:
- Any path starting with `litellm-proxy/` only → `litellm-proxy`
- Any path starting with `browser-agent/` only → `browser-agent`
- Paths in **both** folders, or **neither** folder changed → ask the user:
  ```
  Changed paths touch both services (or neither). Which service do you want to deploy?
  Enter 'litellm-proxy' or 'browser-agent':
  ```
  Wait for the user's answer before continuing.

### Optional inputs (ask only if not auto-detected or not provided)
- `branch` — branch to deploy (default: `main`)
- `environment` — target environment (e.g. `production`, `staging`)

Show the detected/resolved values to the user before proceeding to the CONFIRM gate.

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

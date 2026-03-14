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

Run the lint workflow using `gh workflow run lint.yml`.

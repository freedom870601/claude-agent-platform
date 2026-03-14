# VICI Take-Home — Project Conventions

## Repo Structure
- task1/ — Wrap Claude CLI into a LiteLLM endpoint
- task2/ — Package GitHub CI/CD as Claude Skills
- task3/ — Browser automation agent

## Universal Rules

### Environment
- Always use `uv` for Python environments (never bare pip)
- Each task has its own `pyproject.toml` and `.venv`
- Python version: 3.11+

### TDD Workflow (MANDATORY)
1. Write a failing test first → commit with `test(<task>): add failing test for <thing>`
2. Run the test → confirm it FAILS before implementing
3. Write minimal code to make it pass → commit with `feat(<task>): implement <thing>`
4. Run the test again → confirm it PASSES before moving on
5. Never skip steps — the red→green cycle is the evidence of correctness

### Git Commit Conventions
- Prefix: `chore`, `feat`, `test`, `fix`, `docs`, `refactor`
- Scope: always include task scope e.g. `feat(task1):`, `test(task2):`
- Keep commits small — one logical change per commit
- Never bundle test + implementation in the same commit

### Testing
- Unit tests: mock subprocess/external calls — must pass without network/claude CLI
- Integration tests: mark with `@pytest.mark.integration` — require real running service
- Run unit tests first: `uv run pytest tests/test_*.py -v -m "not integration"`
- Run integration tests separately after service is running

### Docker / Deployment
- Every task deploys to Zeabur via Dockerfile in the task folder
- Required env vars in zeabur.yaml (values set in Zeabur dashboard, not in file)
- Always include a GET /health (or equivalent) endpoint for Zeabur health checks

### Claude CLI Notes
- Non-streaming: `claude -p "<prompt>" --output-format json --model <model>`
  - Parse `result` field from stdout JSON
- Streaming: `--output-format stream-json` — read line-by-line, parse `assistant` events
- Auth: set `ANTHROPIC_API_KEY` env var (claude CLI picks it up automatically)
- Multi-turn history: collapse to `Human: ...\nAssistant: ...` pairs
- System message: pass via `--system-prompt "<text>"`

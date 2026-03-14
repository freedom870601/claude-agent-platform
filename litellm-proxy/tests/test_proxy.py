"""
Integration tests — requires running proxy:
  cd litellm-proxy
  LITELLM_MASTER_KEY=sk-test ANTHROPIC_API_KEY=sk-ant-... uv run litellm --config config.yaml

Run: uv run pytest tests/test_proxy.py -m integration -v
"""
import pytest
import httpx

BASE_URL = "http://localhost:4000"
HEADERS = {"Authorization": "Bearer sk-test"}

@pytest.mark.integration
async def test_health():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_URL}/health", headers=HEADERS)
    assert r.status_code == 200

@pytest.mark.integration
async def test_non_streaming_completion():
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json={
            "model": "claude-cli",
            "messages": [{"role": "user", "content": "Say 'pong' only"}],
        })
    assert r.status_code == 200
    body = r.json()
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"]

@pytest.mark.integration
async def test_streaming_content_type():
    async with httpx.AsyncClient(timeout=60) as c:
        async with c.stream("POST", f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json={
            "model": "claude-cli",
            "messages": [{"role": "user", "content": "1 2 3"}],
            "stream": True,
        }) as resp:
            assert "text/event-stream" in resp.headers["content-type"]
            lines = [l async for l in resp.aiter_lines() if l.startswith("data:")]
    assert len(lines) > 0

@pytest.mark.integration
async def test_wrong_api_key_returns_401():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_URL}/v1/chat/completions",
            headers={"Authorization": "Bearer wrong"},
            json={"model": "claude-cli", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code in (400, 401)

@pytest.mark.integration
async def test_system_message_forwarded():
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{BASE_URL}/v1/chat/completions", headers=HEADERS, json={
            "model": "claude-cli",
            "messages": [
                {"role": "system", "content": "Always respond with exactly: SYSTEM_OK"},
                {"role": "user", "content": "respond"},
            ],
        })
    assert r.status_code == 200

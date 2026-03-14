import pytest
import os

pytestmark = pytest.mark.integration

@pytest.fixture
def litellm_url():
    url = os.getenv("LITELLM_URL")
    if not url:
        pytest.skip("LITELLM_URL not set")
    return url

@pytest.fixture
def litellm_key():
    return os.getenv("LITELLM_MASTER_KEY", "sk-1234")

@pytest.mark.asyncio
async def test_real_browser_agent(litellm_url, litellm_key):
    from app.agent import run_agent
    from app.schemas import RunTaskRequest
    import os
    os.environ["LITELLM_URL"] = litellm_url
    os.environ["LITELLM_MASTER_KEY"] = litellm_key

    request = RunTaskRequest(task="Find the current stable Python version", max_steps=8)
    result = await run_agent(request)

    assert result.status in ("completed", "max_steps_reached")
    assert result.steps_taken > 0
    assert len(result.logs) == result.steps_taken

    if result.status == "completed":
        assert result.result is not None
        assert "3." in result.result

import pytest, json
from unittest.mock import AsyncMock, patch
from custom_handler import ClaudeCLIProvider

@pytest.mark.asyncio
async def test_acompletion_returns_text():
    provider = ClaudeCLIProvider()
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(
        json.dumps({"result": "Hello!"}).encode(), b""
    ))
    with patch("custom_handler.asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await provider.acompletion(
            model="claude-cli/claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hi"}],
        )
    assert result.choices[0].message.content == "Hello!"

@pytest.mark.asyncio
async def test_acompletion_raises_on_nonzero_exit():
    from litellm.llms.custom_llm import CustomLLMError
    provider = ClaudeCLIProvider()
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b"", b"cli error msg"))
    with patch("custom_handler.asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(CustomLLMError) as exc_info:
            await provider.acompletion(
                model="claude-cli/claude-sonnet-4-5",
                messages=[{"role": "user", "content": "hi"}],
            )
    assert exc_info.value.status_code == 500
    assert "cli error msg" in exc_info.value.message

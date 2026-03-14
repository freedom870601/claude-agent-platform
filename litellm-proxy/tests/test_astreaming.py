import pytest
import json
from unittest.mock import AsyncMock, patch
from custom_handler import ClaudeCLIProvider

@pytest.mark.asyncio
async def test_astreaming_yields_text():
    provider = ClaudeCLIProvider()

    async def fake_stdout():
        yield json.dumps({
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "Hi"}]}
        }).encode() + b"\n"
        yield json.dumps({"type": "result", "result": "Hi"}).encode() + b"\n"

    mock_proc = AsyncMock()
    mock_proc.stdout = fake_stdout()
    mock_proc.wait = AsyncMock()

    with patch("custom_handler.asyncio.create_subprocess_exec", return_value=mock_proc):
        chunks = []
        async for chunk in provider.astreaming(
            model="claude-cli/claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hi"}],
        ):
            chunks.append(chunk)

    text_chunks = [c for c in chunks if c["text"]]
    assert len(text_chunks) >= 1
    assert text_chunks[0]["text"] == "Hi"

@pytest.mark.asyncio
async def test_astreaming_ends_with_done_chunk():
    provider = ClaudeCLIProvider()

    async def fake_stdout():
        yield json.dumps({
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "A"}]}
        }).encode() + b"\n"

    mock_proc = AsyncMock()
    mock_proc.stdout = fake_stdout()
    mock_proc.wait = AsyncMock()

    with patch("custom_handler.asyncio.create_subprocess_exec", return_value=mock_proc):
        chunks = []
        async for chunk in provider.astreaming(
            model="claude-cli/claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hi"}],
        ):
            chunks.append(chunk)

    last = chunks[-1]
    assert last["is_finished"] is True
    assert last["finish_reason"] == "stop"

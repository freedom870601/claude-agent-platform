import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

def make_tool_call(name, args, call_id="call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = json.dumps(args)
    return tc

def make_message(content=None, tool_calls=None):
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = tool_calls
    return msg

def make_response(message):
    choice = MagicMock()
    choice.message = message
    resp = MagicMock()
    resp.choices = [choice]
    return resp

@pytest.mark.asyncio
async def test_agent_done_tool_terminates():
    from app.schemas import RunTaskRequest

    done_tc = make_tool_call("done", {"answer": "Python 3.13"})
    msg = make_message(tool_calls=[done_tc])
    resp = make_response(msg)

    with patch("app.agent.BrowserSession") as MockBrowser, \
         patch("app.agent.ClaudeClient") as MockClient, \
         patch("asyncio.to_thread", new=AsyncMock(return_value=resp)):

        mock_browser_inst = AsyncMock()
        MockBrowser.return_value = mock_browser_inst

        mock_client_inst = MagicMock()
        mock_client_inst.messages = []
        MockClient.return_value = mock_client_inst

        from app.agent import run_agent
        request = RunTaskRequest(task="Find Python version", max_steps=5)
        result = await run_agent(request)

        assert result.status == "completed"
        assert result.result == "Python 3.13"
        assert result.steps_taken == 1

@pytest.mark.asyncio
async def test_agent_max_steps_reached():
    from app.schemas import RunTaskRequest

    search_tc = make_tool_call("browser_search", {"query": "python"})
    msg = make_message(tool_calls=[search_tc])
    resp = make_response(msg)

    with patch("app.agent.BrowserSession") as MockBrowser, \
         patch("app.agent.ClaudeClient") as MockClient, \
         patch("asyncio.to_thread", new=AsyncMock(return_value=resp)):

        mock_browser_inst = AsyncMock()
        mock_browser_inst.search = AsyncMock(return_value="some results")
        MockBrowser.return_value = mock_browser_inst

        mock_client_inst = MagicMock()
        mock_client_inst.messages = []
        MockClient.return_value = mock_client_inst

        from app.agent import run_agent
        request = RunTaskRequest(task="Search forever", max_steps=3)
        result = await run_agent(request)

        assert result.status == "max_steps_reached"
        assert result.steps_taken == 3

@pytest.mark.asyncio
async def test_agent_browser_error_recovery():
    from app.schemas import RunTaskRequest

    search_tc = make_tool_call("browser_search", {"query": "python"}, "call_1")
    done_tc = make_tool_call("done", {"answer": "recovered"}, "call_2")

    msg1 = make_message(tool_calls=[search_tc])
    msg2 = make_message(tool_calls=[done_tc])
    resp1 = make_response(msg1)
    resp2 = make_response(msg2)

    responses = [resp1, resp2]
    call_count = [0]

    async def mock_to_thread(fn, *args, **kwargs):
        r = responses[call_count[0]]
        call_count[0] += 1
        return r

    with patch("app.agent.BrowserSession") as MockBrowser, \
         patch("app.agent.ClaudeClient") as MockClient, \
         patch("asyncio.to_thread", side_effect=mock_to_thread):

        mock_browser_inst = AsyncMock()
        mock_browser_inst.search = AsyncMock(side_effect=Exception("Network error"))
        MockBrowser.return_value = mock_browser_inst

        mock_client_inst = MagicMock()
        mock_client_inst.messages = []
        MockClient.return_value = mock_client_inst

        from app.agent import run_agent
        request = RunTaskRequest(task="Search with error", max_steps=5)
        result = await run_agent(request)

        assert result.status == "completed"
        # Error was returned to Claude, not propagated up
        error_log = next(l for l in result.logs if l.action == "browser_search")
        assert "Error" in error_log.output

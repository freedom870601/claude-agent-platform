import pytest
from unittest.mock import MagicMock, patch

def make_mock_response(content=None, tool_calls=None):
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = tool_calls or []
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp

def test_claude_client_init():
    with patch("app.claude_client.OpenAI") as mock_openai:
        from app.claude_client import ClaudeClient
        client = ClaudeClient(base_url="http://localhost:4000", api_key="sk-test")
        mock_openai.assert_called_once_with(base_url="http://localhost:4000/v1", api_key="sk-test")
        assert client.model == "claude-cli"

def test_add_user():
    with patch("app.claude_client.OpenAI"):
        from app.claude_client import ClaudeClient
        client = ClaudeClient("http://localhost:4000", "sk-test")
        client.add_user("hello")
        assert client.messages[-1] == {"role": "user", "content": "hello"}

def test_add_tool_result():
    with patch("app.claude_client.OpenAI"):
        from app.claude_client import ClaudeClient
        client = ClaudeClient("http://localhost:4000", "sk-test")
        client.add_tool_result("call_123", "result text")
        assert client.messages[-1] == {"role": "tool", "tool_call_id": "call_123", "content": "result text"}

def test_step_calls_openai():
    with patch("app.claude_client.OpenAI") as mock_openai_cls:
        from app.claude_client import ClaudeClient, TOOLS
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response("hi")

        client = ClaudeClient("http://localhost:4000", "sk-test")
        client.add_user("find python version")
        resp = client.step()

        mock_client.chat.completions.create.assert_called_once_with(
            model="claude-cli",
            messages=client.messages,
            tools=TOOLS,
        )

def test_tools_list_has_expected_tools():
    from app.claude_client import TOOLS
    names = [t["function"]["name"] for t in TOOLS]
    assert "search" in names
    assert "navigate" in names
    assert "extract_text" in names
    assert "click" in names
    assert "type_text" in names
    assert "done" in names

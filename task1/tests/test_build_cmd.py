from custom_handler import _build_cmd

def test_basic_non_streaming_cmd():
    cmd = _build_cmd("hello", None, "claude-cli/claude-sonnet-4-5", None, stream=False)
    assert "claude" in cmd[0] or cmd[0].endswith("claude")
    assert "-p" in cmd
    assert "hello" in cmd
    assert "--output-format" in cmd
    assert "json" in cmd
    assert "--model" in cmd
    assert "claude-sonnet-4-5" in cmd  # provider prefix stripped

def test_streaming_flag():
    cmd = _build_cmd("hello", None, "claude-cli/sonnet", None, stream=True)
    idx = cmd.index("--output-format")
    assert cmd[idx + 1] == "stream-json"

def test_system_prompt_appended():
    cmd = _build_cmd("hello", "Be helpful", "sonnet", None, stream=False)
    assert "--system-prompt" in cmd
    assert "Be helpful" in cmd

def test_max_tokens_appended():
    cmd = _build_cmd("hello", None, "sonnet", 100, stream=False)
    assert "--max-tokens" in cmd
    assert "100" in cmd

def test_no_system_no_system_flag():
    cmd = _build_cmd("hello", None, "sonnet", None, stream=False)
    assert "--system-prompt" not in cmd

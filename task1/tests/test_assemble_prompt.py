from custom_handler import assemble_prompt

def test_simple_user_message():
    messages = [{"role": "user", "content": "hello"}]
    prompt, system = assemble_prompt(messages)
    assert "hello" in prompt
    assert system is None

def test_system_message_extracted():
    messages = [
        {"role": "system", "content": "Be helpful"},
        {"role": "user", "content": "hi"},
    ]
    prompt, system = assemble_prompt(messages)
    assert system == "Be helpful"
    assert "hi" in prompt
    assert "Be helpful" not in prompt  # system not in prompt body

def test_multiturn_ordering():
    messages = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "And 3+3?"},
    ]
    prompt, system = assemble_prompt(messages)
    assert "Human: What is 2+2?" in prompt
    assert "Assistant: 4" in prompt
    assert "Human: And 3+3?" in prompt
    # ordering: first user before last user
    assert prompt.index("2+2") < prompt.index("3+3")

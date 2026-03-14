from custom_handler import assemble_prompt

def test_simple_user_message():
    messages = [{"role": "user", "content": "hello"}]
    prompt, system = assemble_prompt(messages)
    assert "hello" in prompt
    assert system is None

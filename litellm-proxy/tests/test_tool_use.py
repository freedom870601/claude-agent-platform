"""Tests for tool use support in custom_handler."""
import json
import pytest
from custom_handler import assemble_prompt, parse_tool_response, build_tools_system_prompt


TOOLS = [
    {"type": "function", "function": {
        "name": "search",
        "description": "Search the web",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "done",
        "description": "Return final answer",
        "parameters": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]},
    }},
]


# --- assemble_prompt with tool messages ---

def test_assemble_prompt_tool_result_included():
    messages = [
        {"role": "user", "content": "Find Python version"},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "tc1", "function": {"name": "search", "arguments": '{"query": "python version"}'}}
        ]},
        {"role": "tool", "tool_call_id": "tc1", "content": "Python 3.13"},
    ]
    prompt, _ = assemble_prompt(messages)
    assert "search" in prompt
    assert "Python 3.13" in prompt


def test_assemble_prompt_assistant_tool_call_rendered():
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "tc1", "function": {"name": "done", "arguments": '{"answer": "hello"}'}}
        ]},
    ]
    prompt, _ = assemble_prompt(messages)
    assert "done" in prompt
    assert "hello" in prompt


# --- build_tools_system_prompt ---

def test_build_tools_system_prompt_contains_tool_names():
    system = build_tools_system_prompt(TOOLS)
    assert "search" in system
    assert "done" in system


def test_build_tools_system_prompt_contains_json_instruction():
    system = build_tools_system_prompt(TOOLS)
    assert "JSON" in system or "json" in system


def test_build_tools_system_prompt_none_when_no_tools():
    assert build_tools_system_prompt([]) is None
    assert build_tools_system_prompt(None) is None


# --- parse_tool_response ---

def test_parse_tool_response_detects_tool_call():
    text = '{"tool": "search", "arguments": {"query": "python version"}}'
    result = parse_tool_response(text)
    assert result is not None
    assert result["name"] == "search"
    assert result["arguments"] == {"query": "python version"}


def test_parse_tool_response_returns_none_for_plain_text():
    result = parse_tool_response("Python 3.13 is the latest version.")
    assert result is None


def test_parse_tool_response_handles_extra_whitespace():
    text = '  \n{"tool": "done", "arguments": {"answer": "42"}}\n  '
    result = parse_tool_response(text)
    assert result is not None
    assert result["name"] == "done"


def test_parse_tool_response_returns_none_for_unrelated_json():
    result = parse_tool_response('{"status": "ok"}')
    assert result is None


def test_parse_tool_response_handles_function_calls_wrapper():
    text = '<function_calls>\n{"tool": "navigate", "arguments": {"url": "https://example.com"}}\n</function_calls>'
    result = parse_tool_response(text)
    assert result is not None
    assert result["name"] == "navigate"
    assert result["arguments"] == {"url": "https://example.com"}


def test_parse_tool_response_returns_first_when_multiple():
    text = '<function_calls>\n{"tool": "navigate", "arguments": {"url": "https://a.com"}}\n</function_calls>\n<function_calls>\n{"tool": "extract_text", "arguments": {}}\n</function_calls>'
    result = parse_tool_response(text)
    assert result is not None
    assert result["name"] == "navigate"

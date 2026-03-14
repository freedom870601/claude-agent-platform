import asyncio
import json
import os
import subprocess
import time
import uuid
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
import litellm
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse, Choices, Message, Usage
from litellm.llms.custom_llm import CustomLLMError

load_dotenv()

CLAUDE_PATH = os.environ.get("CLAUDE_PATH", "claude")

# Pass full environment so Claude CLI can use ANTHROPIC_API_KEY
# Must be a plain dict — uvloop rejects os.environ (_Environ type)
_SUBPROCESS_ENV = dict(os.environ)


def build_tools_system_prompt(tools: list | None) -> str | None:
    """Convert OpenAI-format tools list into a system prompt instruction for Claude CLI."""
    if not tools:
        return None
    tool_lines = []
    for t in tools:
        fn = t.get("function", {})
        name = fn.get("name", "")
        desc = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        param_names = list(params.keys())
        tool_lines.append(f"- {name}({', '.join(param_names)}): {desc}")
    lines = [
        "You are an agent with access to external browser tools.",
        "RULES (strictly follow):",
        "1. To call ONE tool, output ONLY a single raw JSON object on one line. No XML, no markdown, no <function_calls> tags, no extra text:",
        '   {"tool": "<tool_name>", "arguments": {<arguments>}}',
        "2. Call ONE tool at a time. Wait for the result before calling the next tool.",
        "3. Do NOT ask for permission. Do NOT explain. Just output the JSON.",
        "4. When finished, call the 'done' tool with your final answer.",
        "",
        "Available tools:",
    ] + tool_lines
    return "\n".join(lines)


def parse_tool_response(text: str) -> dict | None:
    """Parse Claude's text output into a tool call dict, or return None if plain text.

    Handles both clean JSON and <function_calls>...</function_calls> wrapped output.
    When multiple tool calls are present, returns only the first one.
    """
    stripped = text.strip()

    # Try clean JSON first
    try:
        data = json.loads(stripped)
        if "tool" in data and "arguments" in data:
            return {"name": data["tool"], "arguments": data["arguments"]}
    except (json.JSONDecodeError, ValueError):
        pass

    # Scan for JSON objects that contain "tool" key
    i = 0
    while i < len(text):
        if text[i] == '{':
            # Try to decode a JSON object starting at position i
            decoder = json.JSONDecoder()
            try:
                data, end = decoder.raw_decode(text, i)
                if isinstance(data, dict) and "tool" in data and "arguments" in data:
                    return {"name": data["tool"], "arguments": data["arguments"]}
                i = end
                continue
            except (json.JSONDecodeError, ValueError):
                pass
        i += 1

    return None


def _make_response(text: str, model: str) -> ModelResponse:
    return ModelResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        choices=[Choices(finish_reason="stop", index=0, message=Message(content=text, role="assistant"))],
        created=int(time.time()),
        model=model,
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


def _make_tool_call_response(tool: dict, model: str) -> ModelResponse:
    """Return a ModelResponse containing a single tool call."""
    from litellm.types.utils import ChatCompletionMessageToolCall, Function
    tool_call = ChatCompletionMessageToolCall(
        id=f"call_{uuid.uuid4().hex[:8]}",
        type="function",
        function=Function(name=tool["name"], arguments=json.dumps(tool["arguments"])),
    )
    msg = Message(content=None, role="assistant", tool_calls=[tool_call])
    return ModelResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        choices=[Choices(finish_reason="tool_calls", index=0, message=msg)],
        created=int(time.time()),
        model=model,
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


def _resolve_response(text: str, model: str, has_tools: bool) -> ModelResponse:
    """If tools are active and Claude returned a tool call JSON, wrap it; else plain text."""
    if has_tools:
        tool = parse_tool_response(text)
        if tool:
            return _make_tool_call_response(tool, model)
    return _make_response(text, model)


def assemble_prompt(messages: list[dict]) -> tuple[str, Optional[str]]:
    system = None
    parts = []
    for m in messages:
        role = m["role"]
        if role == "system":
            system = m["content"]
        elif role == "user":
            parts.append(f"Human: {m['content']}")
        elif role == "assistant":
            tool_calls = m.get("tool_calls")
            if tool_calls:
                # Render tool calls as the assistant's JSON response
                tc = tool_calls[0]
                fn = tc["function"]
                args = json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"]
                rendered = json.dumps({"tool": fn["name"], "arguments": args})
                parts.append(f"Assistant: {rendered}")
            else:
                parts.append(f"Assistant: {m['content']}")
        elif role == "tool":
            # Tool result follows the assistant's tool call
            parts.append(f"Human: [Tool result]: {m['content']}")
    return "\n".join(parts), system


def _build_cmd(prompt: str, system: Optional[str], model_name: str,
               max_tokens: Optional[int], stream: bool) -> list[str]:
    if "/" in model_name:
        model_name = model_name.split("/", 1)[1]
    cmd = [
        CLAUDE_PATH, "-p", prompt,
        "--output-format", "stream-json" if stream else "json",
        "--model", model_name,
        "--tools", "",
    ]
    if system:
        cmd += ["--system-prompt", system]
    if max_tokens:
        cmd += ["--max-tokens", str(max_tokens)]
    return cmd


class ClaudeCLIProvider(CustomLLM):

    async def acompletion(self, model: str, messages: list, **kwargs) -> ModelResponse:
        optional_params = kwargs.get("optional_params", {})
        tools = kwargs.get("tools") or optional_params.get("tools")
        prompt, system = assemble_prompt(messages)
        tools_system = build_tools_system_prompt(tools)
        if tools_system:
            system = f"{tools_system}\n\n{system}" if system else tools_system
        max_tokens = kwargs.get("max_tokens")
        cmd = _build_cmd(prompt, system, model, max_tokens, stream=False)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_SUBPROCESS_ENV,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        if proc.returncode != 0 and not stdout:
            raise CustomLLMError(500, stderr.decode())
        data = json.loads(stdout)
        if data.get("is_error"):
            raise CustomLLMError(500, data.get("result", "Claude CLI error"))
        text = data.get("result", "")
        return _resolve_response(text, model, has_tools=bool(tools))

    async def astreaming(self, model: str, messages: list, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        prompt, system = assemble_prompt(messages)
        cmd = _build_cmd(prompt, system, model, None, stream=True)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_SUBPROCESS_ENV,
        )
        async for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        yield GenericStreamingChunk(
                            text=block["text"],
                            is_finished=False,
                            finish_reason=None,
                            index=0,
                            tool_use=None,
                            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        )
        await proc.wait()
        yield GenericStreamingChunk(
            text="",
            is_finished=True,
            finish_reason="stop",
            index=0,
            tool_use=None,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )

    def completion(self, model: str, messages: list, **kwargs) -> ModelResponse:
        optional_params = kwargs.get("optional_params", {})
        tools = kwargs.get("tools") or optional_params.get("tools")
        prompt, system = assemble_prompt(messages)
        tools_system = build_tools_system_prompt(tools)
        if tools_system:
            system = f"{tools_system}\n\n{system}" if system else tools_system
        max_tokens = kwargs.get("max_tokens")
        cmd = _build_cmd(prompt, system, model, max_tokens, stream=False)
        result = subprocess.run(cmd, capture_output=True, timeout=120, env=_SUBPROCESS_ENV)
        if result.returncode != 0 and not result.stdout:
            raise CustomLLMError(500, result.stderr.decode())
        data = json.loads(result.stdout)
        if data.get("is_error"):
            raise CustomLLMError(500, data.get("result", "Claude CLI error"))
        text = data.get("result", "")
        return _resolve_response(text, model, has_tools=bool(tools))

    def streaming(self, model: str, messages: list, **kwargs):
        prompt, system = assemble_prompt(messages)
        cmd = _build_cmd(prompt, system, model, None, stream=True)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_SUBPROCESS_ENV)
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        yield GenericStreamingChunk(
                            text=block["text"],
                            is_finished=False,
                            finish_reason=None,
                            index=0,
                            tool_use=None,
                            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        )
        proc.wait()
        yield GenericStreamingChunk(
            text="",
            is_finished=True,
            finish_reason="stop",
            index=0,
            tool_use=None,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )


# Singleton instance — referenced in config.yaml
claude_cli_provider = ClaudeCLIProvider()

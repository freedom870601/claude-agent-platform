import asyncio
import json
import os
import subprocess
import time
import uuid
from typing import AsyncIterator, Optional

import litellm
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse, Choices, Message, Usage
from litellm.llms.custom_llm import CustomLLMError

CLAUDE_PATH = os.environ.get("CLAUDE_PATH", "claude")

# Build subprocess env without ANTHROPIC_API_KEY so Claude CLI uses OAuth login
_SUBPROCESS_ENV = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


def _make_response(text: str, model: str) -> ModelResponse:
    return ModelResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        choices=[Choices(finish_reason="stop", index=0, message=Message(content=text, role="assistant"))],
        created=int(time.time()),
        model=model,
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


def assemble_prompt(messages: list[dict]) -> tuple[str, Optional[str]]:
    system = None
    parts = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        elif m["role"] == "user":
            parts.append(f"Human: {m['content']}")
        elif m["role"] == "assistant":
            parts.append(f"Assistant: {m['content']}")
    return "\n".join(parts), system


def _build_cmd(prompt: str, system: Optional[str], model_name: str,
               max_tokens: Optional[int], stream: bool) -> list[str]:
    if "/" in model_name:
        model_name = model_name.split("/", 1)[1]
    cmd = [
        CLAUDE_PATH, "-p", prompt,
        "--output-format", "stream-json" if stream else "json",
        "--model", model_name,
    ]
    if system:
        cmd += ["--system-prompt", system]
    if max_tokens:
        cmd += ["--max-tokens", str(max_tokens)]
    return cmd


class ClaudeCLIProvider(CustomLLM):

    async def acompletion(self, model: str, messages: list, **kwargs) -> ModelResponse:
        prompt, system = assemble_prompt(messages)
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
        return _make_response(text, model)

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
        prompt, system = assemble_prompt(messages)
        max_tokens = kwargs.get("max_tokens")
        cmd = _build_cmd(prompt, system, model, max_tokens, stream=False)
        result = subprocess.run(cmd, capture_output=True, timeout=120, env=_SUBPROCESS_ENV)
        if result.returncode != 0 and not result.stdout:
            raise CustomLLMError(500, result.stderr.decode())
        data = json.loads(result.stdout)
        if data.get("is_error"):
            raise CustomLLMError(500, data.get("result", "Claude CLI error"))
        text = data.get("result", "")
        return _make_response(text, model)

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

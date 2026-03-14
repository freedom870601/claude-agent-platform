import asyncio
import json
import os
import subprocess
from typing import AsyncIterator, Optional

CLAUDE_PATH = os.environ.get("CLAUDE_PATH", "claude")


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

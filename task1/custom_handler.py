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

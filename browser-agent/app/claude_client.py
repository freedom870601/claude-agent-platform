from openai import OpenAI

TOOLS = [
    {"type": "function", "function": {"name": "browser_search", "description": "Search the web using a browser", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "navigate", "description": "Navigate to URL", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "extract_text", "description": "Get visible text from current page", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "click", "description": "Click an element", "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}}},
    {"type": "function", "function": {"name": "type_text", "description": "Type into an element", "parameters": {"type": "object", "properties": {"selector": {"type": "string"}, "text": {"type": "string"}}, "required": ["selector", "text"]}}},
    {"type": "function", "function": {"name": "done", "description": "Return final answer", "parameters": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}}},
]

class ClaudeClient:
    def __init__(self, base_url: str, api_key: str, model: str = "claude-cli"):
        self.client = OpenAI(base_url=f"{base_url}/v1", api_key=api_key)
        self.model = model
        self.messages: list[dict] = []

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, message):
        self.messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

    def add_tool_result(self, tool_call_id: str, result: str):
        self.messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})

    def step(self):
        return self.client.chat.completions.create(
            model=self.model, messages=self.messages, tools=TOOLS
        )

import asyncio
import json
from .browser import BrowserSession
from .claude_client import ClaudeClient
from .logger import RunLogger
from .schemas import RunTaskRequest, RunTaskResponse
import os

async def run_agent(request: RunTaskRequest) -> RunTaskResponse:
    import uuid
    task_id = str(uuid.uuid4())
    logger = RunLogger()
    browser = BrowserSession()

    base_url = os.getenv("LITELLM_URL", "http://localhost:4000")
    api_key = os.getenv("LITELLM_MASTER_KEY", "sk-1234")
    model = os.getenv("LITELLM_MODEL", "claude-cli")

    client = ClaudeClient(base_url=base_url, api_key=api_key, model=model)
    client.add_user(request.task)

    try:
        await browser.start()

        for step in range(1, request.max_steps + 1):
            response = await asyncio.to_thread(client.step)
            message = response.choices[0].message
            client.add_assistant(message)

            if not message.tool_calls:
                return RunTaskResponse(
                    task_id=task_id,
                    status="completed",
                    result=message.content,
                    steps_taken=step,
                    logs=logger.logs,
                )

            all_done = False
            final_answer = None

            for tool_call in message.tool_calls:
                fn = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                try:
                    if fn == "done":
                        final_answer = args["answer"]
                        all_done = True
                        result_str = final_answer
                    elif fn == "browser_search":
                        result_str = await browser.search(args["query"])
                    elif fn == "navigate":
                        result_str = await browser.navigate(args["url"])
                    elif fn == "extract_text":
                        result_str = await browser.extract_text()
                    elif fn == "click":
                        result_str = await browser.click(args["selector"])
                    elif fn == "type_text":
                        result_str = await browser.type_text(args["selector"], args["text"])
                    else:
                        result_str = f"Unknown tool: {fn}"
                except Exception as e:
                    result_str = f"Error: {e}"

                logger.log(step=step, action=fn, input=args, output=result_str)
                client.add_tool_result(tool_call.id, result_str)

            if all_done:
                return RunTaskResponse(
                    task_id=task_id,
                    status="completed",
                    result=final_answer,
                    steps_taken=step,
                    logs=logger.logs,
                )

        return RunTaskResponse(
            task_id=task_id,
            status="max_steps_reached",
            result=None,
            steps_taken=request.max_steps,
            logs=logger.logs,
        )

    except Exception as e:
        return RunTaskResponse(
            task_id=task_id,
            status="failed",
            result=None,
            steps_taken=len(logger.logs),
            logs=logger.logs,
            error=str(e),
        )
    finally:
        await browser.stop()

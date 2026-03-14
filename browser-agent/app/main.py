from fastapi import FastAPI
from .schemas import RunTaskRequest, RunTaskResponse
from .agent import run_agent

app = FastAPI(title="Browser Agent")

@app.get("/")
def root():
    return {"status": "ok", "service": "browser-agent"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "browser-agent"}

@app.post("/run-task", response_model=RunTaskResponse)
async def run_task(request: RunTaskRequest) -> RunTaskResponse:
    return await run_agent(request)

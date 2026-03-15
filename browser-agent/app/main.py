from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import RunTaskRequest, RunTaskResponse
from .agent import run_agent

app = FastAPI(title="Browser Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "browser-agent"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "browser-agent"}

@app.post("/run-task", response_model=RunTaskResponse)
async def run_task(request: RunTaskRequest) -> RunTaskResponse:
    return await run_agent(request)

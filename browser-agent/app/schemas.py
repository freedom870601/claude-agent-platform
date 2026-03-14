from pydantic import BaseModel, Field
from typing import Optional
import uuid

class RunTaskRequest(BaseModel):
    task: str
    max_steps: int = Field(default=10, ge=1, le=50)
    timeout_seconds: int = Field(default=120, ge=10, le=600)

class StepLog(BaseModel):
    step: int
    action: str
    input: dict
    output: str
    timestamp: str

class RunTaskResponse(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str  # "completed" | "failed" | "max_steps_reached"
    result: Optional[str] = None
    steps_taken: int = 0
    logs: list[StepLog] = Field(default_factory=list)
    error: Optional[str] = None

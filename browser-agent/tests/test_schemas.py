import pytest
from app.schemas import RunTaskRequest, RunTaskResponse, StepLog

def test_run_task_request_defaults():
    req = RunTaskRequest(task="Find something")
    assert req.task == "Find something"
    assert req.max_steps == 10
    assert req.timeout_seconds == 120

def test_run_task_request_custom():
    req = RunTaskRequest(task="Do it", max_steps=5, timeout_seconds=60)
    assert req.max_steps == 5
    assert req.timeout_seconds == 60

def test_run_task_request_max_steps_bounds():
    with pytest.raises(Exception):
        RunTaskRequest(task="x", max_steps=0)
    with pytest.raises(Exception):
        RunTaskRequest(task="x", max_steps=51)

def test_run_task_response_defaults():
    resp = RunTaskResponse(status="completed")
    assert resp.status == "completed"
    assert resp.steps_taken == 0
    assert resp.logs == []
    assert resp.error is None
    assert resp.task_id is not None

def test_run_task_response_with_logs():
    from datetime import datetime, timezone
    log = StepLog(step=1, action="search", input={"query": "python"}, output="results", timestamp=datetime.now(timezone.utc).isoformat())
    resp = RunTaskResponse(status="completed", result="found it", steps_taken=1, logs=[log])
    assert len(resp.logs) == 1
    assert resp.logs[0].action == "search"

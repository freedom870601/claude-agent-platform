from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.schemas import RunTaskResponse

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "browser-agent"

def test_run_task_success():
    mock_response = RunTaskResponse(
        task_id="test-uuid",
        status="completed",
        result="Python 3.13",
        steps_taken=2,
        logs=[],
    )

    with patch("app.main.run_agent", new=AsyncMock(return_value=mock_response)):
        resp = client.post("/run-task", json={"task": "Find Python version"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["result"] == "Python 3.13"

def test_run_task_invalid_request():
    resp = client.post("/run-task", json={"max_steps": 5})  # missing task
    assert resp.status_code == 422

def test_run_task_max_steps_exceeded():
    resp = client.post("/run-task", json={"task": "x", "max_steps": 100})
    assert resp.status_code == 422

def test_cors_headers_on_run_task():
    """Browser fetch() requires CORS headers — missing middleware causes preflight failure."""
    resp = client.options(
        "/run-task",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "*"

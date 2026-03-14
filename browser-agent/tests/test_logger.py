import pytest
from app.logger import RunLogger

def test_logger_empty():
    logger = RunLogger()
    assert logger.logs == []

def test_logger_single_step():
    logger = RunLogger()
    entry = logger.log(step=1, action="search", input={"query": "python"}, output="results")
    assert len(logger.logs) == 1
    assert entry.step == 1
    assert entry.action == "search"
    assert entry.input == {"query": "python"}
    assert entry.output == "results"
    assert entry.timestamp is not None

def test_logger_multiple_steps():
    logger = RunLogger()
    logger.log(1, "search", {"query": "q"}, "out1")
    logger.log(2, "navigate", {"url": "http://x.com"}, "out2")
    assert len(logger.logs) == 2
    assert logger.logs[1].action == "navigate"

def test_logger_timestamps_are_iso():
    import re
    logger = RunLogger()
    entry = logger.log(1, "done", {"answer": "42"}, "42")
    # Check ISO8601 format
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", entry.timestamp)

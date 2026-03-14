from datetime import datetime, timezone
from .schemas import StepLog

class RunLogger:
    def __init__(self):
        self.logs: list[StepLog] = []

    def log(self, step: int, action: str, input: dict, output: str) -> StepLog:
        entry = StepLog(
            step=step,
            action=action,
            input=input,
            output=output,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.logs.append(entry)
        return entry

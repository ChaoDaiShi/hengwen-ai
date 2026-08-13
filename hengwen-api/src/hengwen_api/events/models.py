from typing import Literal

TaskEventType = Literal[
    "task.started",
    "stage.started",
    "task.progress",
    "issue.detected",
    "stage.completed",
    "task.completed",
    "task.failed",
    "capability.unsupported",
]

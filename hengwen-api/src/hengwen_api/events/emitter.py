from typing import Any

from sqlalchemy.orm import Session

from hengwen_api.models.review_task import ReviewTask
from hengwen_api.models.task_event import TaskEvent
from hengwen_api.repositories.review_repository import ReviewRepository


class TaskEventEmitter:
    def emit(
        self,
        session: Session,
        task: ReviewTask,
        *,
        event_type: str,
        message: str,
        level: str = "info",
        data: dict[str, Any] | None = None,
    ) -> TaskEvent:
        return ReviewRepository(session).add_event(
            task=task,
            event_type=event_type,
            stage=task.stage,
            stage_index=task.stage_index,
            progress=task.progress,
            level=level,
            message=message,
            data=data,
        )

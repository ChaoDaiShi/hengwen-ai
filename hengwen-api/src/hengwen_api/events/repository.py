from sqlalchemy.orm import Session

from hengwen_api.models.task_event import TaskEvent
from hengwen_api.repositories.review_repository import ReviewRepository


class TaskEventRepository:
    def __init__(self, session: Session) -> None:
        self.repository = ReviewRepository(session)

    def list_after(self, task_id: str, event_id: int) -> list[TaskEvent]:
        return self.repository.list_events(task_id, after_id=event_id)

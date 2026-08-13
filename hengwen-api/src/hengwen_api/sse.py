import json
import time
from collections.abc import Iterator

from hengwen_api.db.session import SessionFactory
from hengwen_api.models.task_event import TaskEvent
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.schemas.review import TaskEventResponse

TERMINAL_EVENTS = {"task.completed", "task.failed"}


def _serialize_event(task_id: str, event: TaskEvent) -> str:
    data = TaskEventResponse(
        event_id=event.id,
        task_id=task_id,
        event_type=event.event_type,
        stage=event.stage,
        stage_index=event.stage_index,
        progress=event.progress,
        level=event.level,
        message=event.message,
        data=event.data_json,
    ).model_dump(by_alias=True)
    return (
        f"id: {event.id}\n"
        f"event: {event.event_type}\n"
        f"data: {json.dumps(data, ensure_ascii=False, separators=(',', ':'))}\n\n"
    )


def iter_task_events(
    session_factory: SessionFactory,
    task_id: str,
    *,
    after_id: int,
    poll_interval: float,
    keepalive_interval: float,
) -> Iterator[str]:
    cursor = after_id
    last_sent_at = time.monotonic()
    while True:
        with session_factory() as session:
            repository = ReviewRepository(session)
            task = repository.get_task(task_id)
            events = repository.list_events(task_id, after_id=cursor)
            task_status = task.status if task is not None else "failed"
        for event in events:
            cursor = event.id
            last_sent_at = time.monotonic()
            yield _serialize_event(task_id, event)
            if event.event_type in TERMINAL_EVENTS:
                return
        if task_status in {"completed", "failed"} and not events:
            return
        now = time.monotonic()
        if now - last_sent_at >= keepalive_interval:
            last_sent_at = now
            yield ": keepalive\n\n"
        time.sleep(poll_interval)

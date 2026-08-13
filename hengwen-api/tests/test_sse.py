import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from hengwen_api.core.config import Settings
from hengwen_api.events.emitter import TaskEventEmitter
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.sse import iter_task_events
from tests.test_report_api import create_completed_task


def parse_sse(text: str) -> list[dict[str, object]]:
    parsed: list[dict[str, object]] = []
    for frame in text.strip().split("\n\n"):
        lines = frame.splitlines()
        if not lines or lines[0].startswith(":"):
            continue
        values = dict(line.split(": ", 1) for line in lines)
        parsed.append(
            {
                "id": int(values["id"]),
                "event": values["event"],
                "data": json.loads(values["data"]),
            }
        )
    return parsed


def test_sse_replays_events_after_last_event_id(
    client: TestClient,
    uploaded_document_id: int,
) -> None:
    task_id, _report_id = create_completed_task(client, uploaded_document_id)
    all_response = client.get(f"/api/v1/review-tasks/{task_id}/events")
    all_events = parse_sse(all_response.text)
    cursor = int(all_events[1]["id"])

    resumed_response = client.get(
        f"/api/v1/review-tasks/{task_id}/events",
        headers={"Last-Event-ID": str(cursor)},
    )
    resumed = parse_sse(resumed_response.text)

    assert all(int(event["id"]) > cursor for event in resumed)
    assert resumed[-1]["event"] == "task.completed"
    assert resumed[-1]["data"]["progress"] == 100
    assert set(resumed[-1]["data"]) >= {
        "eventId",
        "taskId",
        "eventType",
        "stageIndex",
        "progress",
    }


def test_sse_generator_emits_keepalive_while_task_is_running(
    session_factory: sessionmaker[Session],
    settings: Settings,
    uploaded_document_id: int,
) -> None:
    with session_factory() as session:
        task = ReviewRepository(session).create_task(
            task_id="rvw_running",
            document_id=uploaded_document_id,
            org_name="",
            standard="default",
            check_format=False,
            check_citation=False,
            check_plagiarism=False,
            auto_report=False,
        )
        task.status = "running"
        session.commit()
    generator = iter_task_events(
        session_factory,
        "rvw_running",
        after_id=0,
        poll_interval=0.001,
        keepalive_interval=0.001,
    )

    assert next(generator) == ": keepalive\n\n"
    generator.close()


def test_sse_closes_after_failed_final_event(
    client: TestClient,
    session_factory: sessionmaker[Session],
    uploaded_document_id: int,
) -> None:
    with session_factory() as session:
        repository = ReviewRepository(session)
        task = repository.create_task(
            task_id="rvw_failed_stream",
            document_id=uploaded_document_id,
            org_name="",
            standard="default",
            check_format=False,
            check_citation=False,
            check_plagiarism=False,
            auto_report=False,
        )
        task.status = "failed"
        TaskEventEmitter().emit(
            session,
            task,
            event_type="task.failed",
            message="文档审查失败",
            level="error",
            data={"reason": "test"},
        )
        session.commit()

    response = client.get("/api/v1/review-tasks/rvw_failed_stream/events")
    events = parse_sse(response.text)

    assert events[-1]["event"] == "task.failed"
    assert events[-1]["data"]["taskId"] == "rvw_failed_stream"

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from hengwen_api.core.config import Settings
from hengwen_api.events.emitter import TaskEventEmitter
from hengwen_api.models.document import Document
from hengwen_api.models.review_task import ReviewTask
from hengwen_api.repositories.document_repository import DocumentRepository
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.schemas.review import ReviewSettingsCreate
from hengwen_api.services.review_service import ReviewService
from hengwen_api.workers.review_worker import ReviewWorker, recover_stale_tasks
from tests.factories import build_structured_docx

WORKER_LOG_SECRET = "mysql+pymysql://root:WORKER-SECRET@db.example/hengwen"


class FailingAIReviewer:
    def review(self, document):
        del document
        raise RuntimeError(WORKER_LOG_SECRET)


def store_document(
    session_factory: sessionmaker[Session],
    settings: Settings,
    *,
    valid: bool = True,
) -> Document:
    relative_path = Path("uploads/2026/08/review.docx")
    path = settings.storage_dir / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if valid:
        build_structured_docx(path)
    else:
        path.write_bytes(b"corrupt")
    with session_factory() as session:
        document = DocumentRepository(session).create(
            original_name="论文.docx",
            stored_name=path.name,
            file_type=".docx",
            file_size=path.stat().st_size,
            file_hash="d" * 64,
            storage_path=relative_path.as_posix(),
        )
        session.commit()
        return document


def create_review_task(
    session_factory: sessionmaker[Session],
    document: Document,
    *,
    check_plagiarism: bool = False,
) -> ReviewTask:
    settings = ReviewSettingsCreate(
        org_name="测试大学",
        standard="本科毕业论文规范（默认）",
        check_format=True,
        check_citation=True,
        check_plagiarism=check_plagiarism,
        auto_report=True,
    )
    return ReviewService(session_factory).create_task(document.id, settings)


def test_worker_completes_task_and_persists_ordered_events(
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    document = store_document(session_factory, settings)
    task = create_review_task(session_factory, document)

    ReviewWorker(session_factory, settings).run(task.task_id)

    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert saved is not None
    assert saved.status == "completed"
    assert saved.progress == 100
    assert saved.stage == "completed"
    assert saved.report_id is not None and saved.report_id.startswith("report_")
    assert saved.score is not None
    assert saved.verdict in {"pass", "pending", "fail"}
    assert saved.word_count > 0
    assert events[0].event_type == "task.started"
    assert events[-1].event_type == "task.completed"
    assert {event.stage for event in events} >= {
        "read",
        "format",
        "citation",
        "suggestion",
        "completed",
    }
    assert [event.id for event in events] == sorted(event.id for event in events)
    assert "task.progress" in {event.event_type for event in events}


def test_plagiarism_request_records_unsupported_event_without_fake_result(
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    document = store_document(session_factory, settings)
    task = create_review_task(
        session_factory,
        document,
        check_plagiarism=True,
    )

    ReviewWorker(session_factory, settings).run(task.task_id)

    with session_factory() as session:
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert any(
        event.message == "unsupported capability: plagiarism" for event in events
    )
    assert all(
        "重复率" not in json.dumps(event.data_json, ensure_ascii=False)
        for event in events
    )


def test_parser_failure_persists_safe_failed_state(
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    document = store_document(session_factory, settings, valid=False)
    task = create_review_task(session_factory, document)

    ReviewWorker(session_factory, settings).run(task.task_id)

    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert saved is not None
    assert saved.status == "failed"
    assert saved.error_message == "无法解析该文档"
    assert events[-1].event_type == "task.failed"
    assert "Traceback" not in events[-1].message
    assert str(settings.storage_dir) not in events[-1].message


def test_startup_recovery_fails_stale_tasks(
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    document = store_document(session_factory, settings)
    task = create_review_task(session_factory, document)
    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        assert saved is not None
        saved.status = "running"
        session.commit()

    recovered = recover_stale_tasks(session_factory)

    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
        events = ReviewRepository(session).list_events(task.task_id, after_id=0)
    assert recovered == 1
    assert saved is not None
    assert saved.status == "failed"
    assert events[-1].event_type == "task.failed"
    assert events[-1].data_json["reason"] == "application_restarted"


def test_emitter_uses_callers_transaction(
    db_session: Session,
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    document = store_document(session_factory, settings)
    task = ReviewRepository(db_session).create_task(
        task_id="rvw_rollback",
        document_id=document.id,
        org_name="",
        standard="default",
        check_format=False,
        check_citation=False,
        check_plagiarism=False,
        auto_report=False,
    )
    TaskEventEmitter().emit(
        db_session,
        task,
        event_type="task.progress",
        message="not committed",
    )
    db_session.rollback()

    with session_factory() as session:
        assert ReviewRepository(session).list_events("rvw_rollback", after_id=0) == []


def test_worker_logs_exception_type_without_sensitive_exception_text(
    session_factory: sessionmaker[Session],
    settings: Settings,
    caplog,
) -> None:
    document = store_document(session_factory, settings)
    task = create_review_task(session_factory, document)
    caplog.set_level(logging.ERROR)

    ReviewWorker(
        session_factory,
        settings,
        ai_reviewer=FailingAIReviewer(),
    ).run(task.task_id)

    with session_factory() as session:
        saved = ReviewRepository(session).get_task(task.task_id)
    assert saved is not None
    assert saved.status == "failed"
    assert "RuntimeError" in caplog.text
    assert f"task_id={task.task_id}" in caplog.text
    assert f"document_id={document.id}" in caplog.text
    assert "stage=suggestion" in caplog.text
    assert "duration_ms=" in caplog.text
    assert WORKER_LOG_SECRET not in caplog.text

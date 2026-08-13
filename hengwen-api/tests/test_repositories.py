from sqlalchemy.orm import Session

from hengwen_api.repositories.document_repository import DocumentRepository
from hengwen_api.repositories.review_repository import ReviewRepository


def test_document_repository_round_trip(db_session: Session) -> None:
    repository = DocumentRepository(db_session)

    document = repository.create(
        original_name="论文.docx",
        stored_name="generated.docx",
        file_type=".docx",
        file_size=128,
        file_hash="a" * 64,
        storage_path="uploads/2026/08/generated.docx",
    )
    db_session.commit()

    loaded = repository.get(document.id)
    assert loaded is not None
    assert loaded.original_name == "论文.docx"
    assert loaded.status == "uploaded"


def test_review_repository_persists_task_issue_and_event(db_session: Session) -> None:
    document = DocumentRepository(db_session).create(
        original_name="paper.md",
        stored_name="generated.md",
        file_type=".md",
        file_size=32,
        file_hash="b" * 64,
        storage_path="uploads/2026/08/generated.md",
    )
    db_session.flush()
    repository = ReviewRepository(db_session)
    task = repository.create_task(
        task_id="rvw_1234567890abcdef",
        document_id=document.id,
        org_name="测试大学",
        standard="本科毕业论文规范（默认）",
        check_format=True,
        check_citation=True,
        check_plagiarism=False,
        auto_report=True,
    )
    repository.add_issue(
        task=task,
        public_id="iss_1234567890abcdef",
        severity="warning",
        title="缺少关键词",
        location="摘要",
        summary="摘要后未发现关键词",
        original="摘要正文",
        suggestion="增加关键词",
        rule_code="STR003",
        issue_type="structure",
    )
    event = repository.add_event(
        task=task,
        event_type="task.progress",
        stage="format",
        stage_index=1,
        progress=45,
        level="info",
        message="正在检查格式规范…",
        data={"source": "test"},
    )
    db_session.commit()

    loaded = repository.get_task(task.task_id)
    assert loaded is not None
    assert loaded.document_id == document.id
    assert loaded.issues[0].rule_code == "STR003"
    assert repository.list_events(task.task_id, after_id=0) == [event]
    assert repository.list_events(task.task_id, after_id=event.id) == []


def test_completed_report_pagination_is_stable(db_session: Session) -> None:
    document = DocumentRepository(db_session).create(
        original_name="paper.md",
        stored_name="generated.md",
        file_type=".md",
        file_size=32,
        file_hash="c" * 64,
        storage_path="uploads/2026/08/generated.md",
    )
    db_session.flush()
    repository = ReviewRepository(db_session)
    first = repository.create_task(
        task_id="rvw_first",
        document_id=document.id,
        org_name="",
        standard="default",
        check_format=False,
        check_citation=False,
        check_plagiarism=False,
        auto_report=False,
    )
    second = repository.create_task(
        task_id="rvw_second",
        document_id=document.id,
        org_name="",
        standard="default",
        check_format=False,
        check_citation=False,
        check_plagiarism=False,
        auto_report=False,
    )
    first.status = "completed"
    first.report_id = "report_first"
    second.status = "completed"
    second.report_id = "report_second"
    db_session.commit()

    page = repository.list_completed_reports(offset=0, limit=1)

    assert len(page) == 1
    assert repository.count_completed_reports() == 2
    assert page[0].task_id == "rvw_second"

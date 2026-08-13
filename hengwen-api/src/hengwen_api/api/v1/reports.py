from typing import Annotated, cast

from fastapi import APIRouter, Depends, Query

from hengwen_api.api.dependencies import get_session_factory
from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.db.session import SessionFactory
from hengwen_api.document_engine.models import Severity, Verdict
from hengwen_api.models.review_task import ReviewTask
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.schemas.report import (
    FileType,
    IssueResponse,
    ReportPageResponse,
    ReportResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])


def _to_report(task: ReviewTask) -> ReportResponse:
    if (
        task.report_id is None
        or task.completed_at is None
        or task.score is None
        or task.verdict is None
    ):
        raise AppError(
            ErrorCode.REPORT_NOT_FOUND,
            "未找到该审查报告",
            status_code=404,
        )
    return ReportResponse(
        id=task.report_id,
        filename=task.document.original_name,
        file_type=cast(FileType, task.document.file_type),
        checked_at=task.completed_at,
        word_count=task.word_count,
        score=task.score,
        verdict=cast(Verdict, task.verdict),
        issues=[
            IssueResponse(
                id=issue.public_id,
                severity=cast(Severity, issue.severity),
                title=issue.title,
                location=issue.location,
                summary=issue.summary,
                original=issue.original,
                suggestion=issue.suggestion,
            )
            for issue in task.issues
        ],
    )


@router.get("", response_model=ReportPageResponse)
def list_reports(
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> ReportPageResponse:
    with session_factory() as session:
        repository = ReviewRepository(session)
        tasks = repository.list_completed_reports(
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        total = repository.count_completed_reports()
        items = [_to_report(task) for task in tasks]
    return ReportPageResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
) -> ReportResponse:
    with session_factory() as session:
        task = ReviewRepository(session).get_task_by_report(report_id)
        if task is None or task.status != "completed":
            raise AppError(
                ErrorCode.REPORT_NOT_FOUND,
                "未找到该审查报告",
                status_code=404,
            )
        return _to_report(task)

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status
from fastapi.responses import StreamingResponse

from hengwen_api.api.dependencies import get_app_settings, get_session_factory
from hengwen_api.core.config import Settings
from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.db.session import SessionFactory
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.schemas.review import (
    AnalysisTaskResponse,
    ReviewTaskCreate,
    TaskStatusResponse,
)
from hengwen_api.services.review_service import ReviewService
from hengwen_api.sse import iter_task_events
from hengwen_api.workers.review_worker import ReviewWorker

router = APIRouter(prefix="/review-tasks", tags=["review-tasks"])


def _load_task(session_factory: SessionFactory, task_id: str):
    with session_factory() as session:
        task = ReviewRepository(session).get_task(task_id)
        if task is None:
            raise AppError(
                ErrorCode.TASK_NOT_FOUND,
                "未找到该审查任务",
                status_code=404,
            )
        return task


@router.post(
    "",
    response_model=AnalysisTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_review_task(
    payload: ReviewTaskCreate,
    background_tasks: BackgroundTasks,
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AnalysisTaskResponse:
    task = ReviewService(session_factory).create_task(
        payload.document_id,
        payload.settings,
    )
    loaded = _load_task(session_factory, task.task_id)
    background_tasks.add_task(
        ReviewWorker(session_factory, settings).run,
        task.task_id,
    )
    return AnalysisTaskResponse(
        id=loaded.task_id,
        filename=loaded.document.original_name,
        file_type=loaded.document.file_type,
        stage_index=loaded.stage_index,
        progress=loaded.progress,
        started_at=loaded.created_at,
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_review_task(
    task_id: str,
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
) -> TaskStatusResponse:
    task = _load_task(session_factory, task_id)
    return TaskStatusResponse(
        id=task.task_id,
        filename=task.document.original_name,
        file_type=task.document.file_type,
        stage_index=task.stage_index,
        progress=task.progress,
        started_at=task.started_at or task.created_at,
        status=task.status,
        stage=task.stage,
        report_id=task.report_id,
        error_message=task.error_message,
    )


@router.get("/{task_id}/events")
def stream_review_events(
    task_id: str,
    session_factory: Annotated[SessionFactory, Depends(get_session_factory)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    last_event_id: Annotated[int | None, Header(alias="Last-Event-ID", ge=0)] = None,
) -> StreamingResponse:
    _load_task(session_factory, task_id)
    return StreamingResponse(
        iter_task_events(
            session_factory,
            task_id,
            after_id=last_event_id or 0,
            poll_interval=settings.sse_poll_interval_seconds,
            keepalive_interval=settings.sse_keepalive_seconds,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

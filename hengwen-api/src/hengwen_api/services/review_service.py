from uuid import uuid4

from sqlalchemy.orm import Session

from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.db.session import SessionFactory
from hengwen_api.models.review_task import ReviewTask
from hengwen_api.repositories.document_repository import DocumentRepository
from hengwen_api.repositories.review_repository import ReviewRepository
from hengwen_api.schemas.review import ReviewSettingsCreate


class ReviewService:
    def __init__(self, session_factory: SessionFactory) -> None:
        self.session_factory = session_factory

    def create_task(
        self,
        document_id: int,
        settings: ReviewSettingsCreate,
    ) -> ReviewTask:
        with self.session_factory() as session:
            return self._create_in_session(session, document_id, settings)

    def _create_in_session(
        self,
        session: Session,
        document_id: int,
        settings: ReviewSettingsCreate,
    ) -> ReviewTask:
        document = DocumentRepository(session).get(document_id)
        if document is None or document.deleted_at is not None:
            raise AppError(
                ErrorCode.DOCUMENT_NOT_FOUND,
                "未找到该文档",
                status_code=404,
            )
        if document.status != "uploaded":
            raise AppError(
                ErrorCode.INVALID_TASK_STATE,
                "该文档当前不可审查",
                status_code=409,
            )
        task = ReviewRepository(session).create_task(
            task_id=f"rvw_{uuid4().hex}",
            document_id=document.id,
            org_name=settings.org_name,
            standard=settings.standard,
            check_format=settings.check_format,
            check_citation=settings.check_citation,
            check_plagiarism=settings.check_plagiarism,
            auto_report=settings.auto_report,
        )
        session.commit()
        return task

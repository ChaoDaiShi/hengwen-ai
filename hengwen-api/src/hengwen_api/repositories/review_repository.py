from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from hengwen_api.models.review_issue import ReviewIssue
from hengwen_api.models.review_task import ReviewTask
from hengwen_api.models.task_event import TaskEvent


class ReviewRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_task(
        self,
        *,
        task_id: str,
        document_id: int,
        org_name: str,
        standard: str,
        check_format: bool,
        check_citation: bool,
        check_plagiarism: bool,
        auto_report: bool,
    ) -> ReviewTask:
        task = ReviewTask(
            task_id=task_id,
            document_id=document_id,
            org_name=org_name,
            standard=standard,
            check_format=check_format,
            check_citation=check_citation,
            check_plagiarism=check_plagiarism,
            auto_report=auto_report,
        )
        self.session.add(task)
        self.session.flush()
        return task

    def get_task(self, task_id: str) -> ReviewTask | None:
        statement = (
            select(ReviewTask)
            .where(ReviewTask.task_id == task_id)
            .options(
                selectinload(ReviewTask.document),
                selectinload(ReviewTask.issues),
                selectinload(ReviewTask.events),
            )
        )
        return self.session.scalar(statement)

    def get_task_by_report(self, report_id: str) -> ReviewTask | None:
        statement = (
            select(ReviewTask)
            .where(ReviewTask.report_id == report_id)
            .options(
                selectinload(ReviewTask.document),
                selectinload(ReviewTask.issues),
            )
        )
        return self.session.scalar(statement)

    def add_issue(
        self,
        *,
        task: ReviewTask,
        public_id: str,
        severity: str,
        title: str,
        location: str,
        summary: str,
        original: str,
        suggestion: str,
        rule_code: str,
        issue_type: str,
    ) -> ReviewIssue:
        issue = ReviewIssue(
            task=task,
            public_id=public_id,
            severity=severity,
            title=title,
            location=location,
            summary=summary,
            original=original,
            suggestion=suggestion,
            rule_code=rule_code,
            issue_type=issue_type,
        )
        self.session.add(issue)
        self.session.flush()
        return issue

    def add_event(
        self,
        *,
        task: ReviewTask,
        event_type: str,
        stage: str | None,
        stage_index: int | None,
        progress: int,
        level: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> TaskEvent:
        event = TaskEvent(
            task=task,
            event_type=event_type,
            stage=stage,
            stage_index=stage_index,
            progress=progress,
            level=level,
            message=message,
            data_json=data or {},
        )
        self.session.add(event)
        self.session.flush()
        return event

    def list_events(self, task_id: str, *, after_id: int) -> list[TaskEvent]:
        statement = (
            select(TaskEvent)
            .join(ReviewTask, ReviewTask.id == TaskEvent.task_id)
            .where(ReviewTask.task_id == task_id, TaskEvent.id > after_id)
            .order_by(TaskEvent.id)
        )
        return list(self.session.scalars(statement))

    def list_completed_reports(self, *, offset: int, limit: int) -> list[ReviewTask]:
        statement = (
            select(ReviewTask)
            .where(
                ReviewTask.status == "completed",
                ReviewTask.report_id.is_not(None),
            )
            .options(
                selectinload(ReviewTask.document),
                selectinload(ReviewTask.issues),
            )
            .order_by(ReviewTask.created_at.desc(), ReviewTask.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def count_completed_reports(self) -> int:
        statement = select(func.count(ReviewTask.id)).where(
            ReviewTask.status == "completed",
            ReviewTask.report_id.is_not(None),
        )
        return self.session.scalar(statement) or 0

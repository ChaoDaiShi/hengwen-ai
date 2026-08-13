import logging
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

from hengwen_api.ai.reviewer import AIReviewer, NullAIReviewer
from hengwen_api.core.config import Settings
from hengwen_api.core.exceptions import AppError
from hengwen_api.db.base import utc_now
from hengwen_api.db.session import SessionFactory
from hengwen_api.document_engine.models import DocumentModel, RuleIssue
from hengwen_api.document_engine.parser import parse_document
from hengwen_api.document_engine.rule_engine import RuleEngine
from hengwen_api.document_engine.scoring import score_issues
from hengwen_api.events.emitter import TaskEventEmitter
from hengwen_api.models.review_task import ReviewTask
from hengwen_api.repositories.review_repository import ReviewRepository

logger = logging.getLogger(__name__)

STAGES = {
    "read": (0, 20, "正在读取文档…"),
    "format": (1, 45, "正在检查格式规范…"),
    "citation": (2, 70, "正在核查引用与文献…"),
    "suggestion": (3, 90, "正在生成修改建议…"),
    "completed": (4, 100, "分析完成"),
}


class ReviewWorker:
    def __init__(
        self,
        session_factory: SessionFactory,
        settings: Settings,
        *,
        rule_engine: RuleEngine | None = None,
        ai_reviewer: AIReviewer | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings
        self.rule_engine = rule_engine or RuleEngine()
        self.ai_reviewer = ai_reviewer or NullAIReviewer()
        self.emitter = TaskEventEmitter()

    def _transition(
        self,
        task_id: str,
        stage: str,
        *,
        event_type: str,
        message: str | None = None,
    ) -> None:
        stage_index, progress, default_message = STAGES[stage]
        with self.session_factory() as session:
            task = ReviewRepository(session).get_task(task_id)
            if task is None:
                return
            task.stage = stage
            task.stage_index = stage_index
            task.progress = progress
            if task.status == "pending":
                task.status = "running"
                task.started_at = utc_now()
            self.emitter.emit(
                session,
                task,
                event_type=event_type,
                message=message or default_message,
            )
            session.commit()

    def _load_document(self, task_id: str) -> tuple[DocumentModel, int]:
        with self.session_factory() as session:
            task = ReviewRepository(session).get_task(task_id)
            if task is None:
                raise RuntimeError("task not found")
            document = task.document
            path = self.settings.storage_dir / Path(document.storage_path)
            file_type = document.file_type
        parsed = parse_document(path, file_type)
        return parsed, parsed.word_count

    def _persist_issues(
        self,
        task_id: str,
        issues: list[RuleIssue],
    ) -> None:
        with self.session_factory() as session:
            repository = ReviewRepository(session)
            task = repository.get_task(task_id)
            if task is None:
                raise RuntimeError("task not found")
            for issue in issues:
                saved = repository.add_issue(
                    task=task,
                    public_id=f"iss_{uuid4().hex}",
                    severity=issue.severity,
                    title=issue.title,
                    location=issue.location,
                    summary=issue.summary,
                    original=issue.original,
                    suggestion=issue.suggestion,
                    rule_code=issue.rule_code,
                    issue_type=issue.issue_type,
                )
                self.emitter.emit(
                    session,
                    task,
                    event_type="issue.detected",
                    message=issue.title,
                    data={
                        "issueId": saved.public_id,
                        "ruleCode": saved.rule_code,
                        "severity": saved.severity,
                    },
                )
            session.commit()

    def _complete(
        self,
        task_id: str,
        *,
        word_count: int,
        issues: list[RuleIssue],
    ) -> None:
        result = score_issues(issues)
        stage_index, progress, message = STAGES["completed"]
        with self.session_factory() as session:
            task = ReviewRepository(session).get_task(task_id)
            if task is None:
                raise RuntimeError("task not found")
            task.status = "completed"
            task.stage = "completed"
            task.stage_index = stage_index
            task.progress = progress
            task.score = result.score
            task.verdict = result.verdict
            task.word_count = word_count
            task.report_id = f"report_{uuid4().hex}"
            task.completed_at = utc_now()
            self.emitter.emit(
                session,
                task,
                event_type="task.completed",
                message=message,
                data={"reportId": task.report_id},
            )
            session.commit()

    def _fail(self, task_id: str, *, reason: str, exception_name: str) -> None:
        with self.session_factory() as session:
            task = ReviewRepository(session).get_task(task_id)
            if task is None:
                return
            task.status = "failed"
            task.error_message = (
                "无法解析该文档" if reason == "parse_failed" else "文档审查失败"
            )
            task.completed_at = utc_now()
            self.emitter.emit(
                session,
                task,
                event_type="task.failed",
                message=task.error_message,
                level="error",
                data={"reason": reason, "exception": exception_name},
            )
            session.commit()

    def run(self, task_id: str) -> None:
        try:
            self._transition(
                task_id,
                "read",
                event_type="task.started",
            )
            document, word_count = self._load_document(task_id)
            self._transition(
                task_id,
                "read",
                event_type="stage.completed",
                message="文档读取完成",
            )
            self._transition(task_id, "format", event_type="stage.started")
            with self.session_factory() as session:
                task = ReviewRepository(session).get_task(task_id)
                if task is None:
                    raise RuntimeError("task not found")
                check_format = task.check_format
                check_citation = task.check_citation
                check_plagiarism = task.check_plagiarism
            issues = self.rule_engine.review(
                document,
                check_format=check_format,
                check_citation=False,
            )
            self._transition(
                task_id,
                "format",
                event_type="stage.completed",
                message="格式与结构检查完成",
            )
            self._transition(task_id, "citation", event_type="stage.started")
            if check_citation:
                citation_issues = self.rule_engine.review(
                    document,
                    check_format=False,
                    check_citation=True,
                )
                issues.extend(
                    item for item in citation_issues if item.rule_code.startswith("REF")
                )
            if check_plagiarism:
                with self.session_factory() as session:
                    task = ReviewRepository(session).get_task(task_id)
                    if task is None:
                        raise RuntimeError("task not found")
                    self.emitter.emit(
                        session,
                        task,
                        event_type="capability.unsupported",
                        message="unsupported capability: plagiarism",
                        level="warning",
                        data={"capability": "plagiarism", "supported": False},
                    )
                    session.commit()
            self._transition(
                task_id,
                "citation",
                event_type="stage.completed",
                message="引用与文献检查完成",
            )
            self._transition(task_id, "suggestion", event_type="stage.started")
            issues.extend(self.ai_reviewer.review(document))
            self._persist_issues(task_id, issues)
            self._transition(
                task_id,
                "suggestion",
                event_type="stage.completed",
                message="修改建议生成完成",
            )
            self._complete(task_id, word_count=word_count, issues=issues)
        except AppError as exc:
            logger.warning(
                "review failed task_id=%s exception=%s",
                task_id,
                type(exc).__name__,
                extra={"request_id": "-"},
            )
            self._fail(
                task_id,
                reason="parse_failed",
                exception_name=type(exc).__name__,
            )
        except Exception as exc:  # worker boundary must persist a terminal event
            logger.exception(
                "review failed task_id=%s exception=%s",
                task_id,
                type(exc).__name__,
                extra={"request_id": "-"},
            )
            self._fail(
                task_id,
                reason="review_failed",
                exception_name=type(exc).__name__,
            )


def recover_stale_tasks(session_factory: SessionFactory) -> int:
    with session_factory() as session:
        statement = select(ReviewTask).where(
            ReviewTask.status.in_(("pending", "running"))
        )
        tasks = list(session.scalars(statement))
        emitter = TaskEventEmitter()
        for task in tasks:
            task.status = "failed"
            task.error_message = "应用重启，任务未能继续执行"
            task.completed_at = utc_now()
            emitter.emit(
                session,
                task,
                event_type="task.failed",
                message=task.error_message,
                level="error",
                data={"reason": "application_restarted"},
            )
        session.commit()
        return len(tasks)

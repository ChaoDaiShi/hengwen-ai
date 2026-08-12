from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hengwen_api.db.base import Base, utc_now

if TYPE_CHECKING:
    from hengwen_api.models.document import Document
    from hengwen_api.models.review_issue import ReviewIssue
    from hengwen_api.models.task_event import TaskEvent


class ReviewTask(Base):
    __tablename__ = "review_tasks"
    __table_args__ = (
        Index("ix_review_tasks_document_id", "document_id"),
        Index("ix_review_tasks_status", "status"),
        Index("ix_review_tasks_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    report_id: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(32), default="pending")
    stage: Mapped[str] = mapped_column(String(32), default="created")
    stage_index: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    org_name: Mapped[str] = mapped_column(String(255), default="")
    standard: Mapped[str] = mapped_column(String(255))
    check_format: Mapped[bool] = mapped_column(Boolean, default=True)
    check_citation: Mapped[bool] = mapped_column(Boolean, default=True)
    check_plagiarism: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_report: Mapped[bool] = mapped_column(Boolean, default=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(16), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    document: Mapped["Document"] = relationship(back_populates="review_tasks")
    issues: Mapped[list["ReviewIssue"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="ReviewIssue.id",
    )
    events: Mapped[list["TaskEvent"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskEvent.id",
    )

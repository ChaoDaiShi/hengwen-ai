from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hengwen_api.db.base import Base, utc_now

if TYPE_CHECKING:
    from hengwen_api.models.review_task import ReviewTask


class ReviewIssue(Base):
    __tablename__ = "review_issues"
    __table_args__ = (
        Index("ix_review_issues_task_id", "task_id"),
        Index("ix_review_issues_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    public_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("review_tasks.id", ondelete="CASCADE")
    )
    severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    original: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str] = mapped_column(Text)
    rule_code: Mapped[str] = mapped_column(String(32), index=True)
    issue_type: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    task: Mapped["ReviewTask"] = relationship(back_populates="issues")

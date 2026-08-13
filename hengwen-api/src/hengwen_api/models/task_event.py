from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    BigInteger,
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
    from hengwen_api.models.review_task import ReviewTask


class TaskEvent(Base):
    __tablename__ = "task_events"
    __table_args__ = (
        Index("ix_task_events_task_id_id", "task_id", "id"),
        Index("ix_task_events_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("review_tasks.id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(String(64))
    stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    stage_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(16), default="info")
    message: Mapped[str] = mapped_column(Text)
    data_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    task: Mapped["ReviewTask"] = relationship(back_populates="events")

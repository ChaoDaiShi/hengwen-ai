"""Initialize the core document review tables.

Revision ID: 20260813_0001
Revises:
Create Date: 2026-08-13
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from sqlalchemy.types import TypeEngine

from alembic import op

revision: str = "20260813_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _id_type() -> TypeEngine[Any]:
    return sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=8), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )
    op.create_index("ix_documents_created_at", "documents", ["created_at"])
    op.create_index("ix_documents_file_hash", "documents", ["file_hash"])
    op.create_index("ix_documents_status", "documents", ["status"])

    op.create_table(
        "review_tasks",
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("report_id", sa.String(length=64), nullable=True),
        sa.Column("document_id", _id_type(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False),
        sa.Column("stage_index", sa.Integer(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("org_name", sa.String(length=255), nullable=False),
        sa.Column("standard", sa.String(length=255), nullable=False),
        sa.Column("check_format", sa.Boolean(), nullable=False),
        sa.Column("check_citation", sa.Boolean(), nullable=False),
        sa.Column("check_plagiarism", sa.Boolean(), nullable=False),
        sa.Column("auto_report", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("verdict", sa.String(length=16), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_tasks_created_at", "review_tasks", ["created_at"])
    op.create_index("ix_review_tasks_document_id", "review_tasks", ["document_id"])
    op.create_index(
        "ix_review_tasks_report_id", "review_tasks", ["report_id"], unique=True
    )
    op.create_index("ix_review_tasks_status", "review_tasks", ["status"])
    op.create_index("ix_review_tasks_task_id", "review_tasks", ["task_id"], unique=True)

    op.create_table(
        "review_issues",
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", _id_type(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("original", sa.Text(), nullable=False),
        sa.Column("suggestion", sa.Text(), nullable=False),
        sa.Column("rule_code", sa.String(length=32), nullable=False),
        sa.Column("issue_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["review_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_issues_created_at", "review_issues", ["created_at"])
    op.create_index(
        "ix_review_issues_public_id", "review_issues", ["public_id"], unique=True
    )
    op.create_index("ix_review_issues_rule_code", "review_issues", ["rule_code"])
    op.create_index("ix_review_issues_task_id", "review_issues", ["task_id"])

    op.create_table(
        "task_events",
        sa.Column("id", _id_type(), autoincrement=True, nullable=False),
        sa.Column("task_id", _id_type(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=True),
        sa.Column("stage_index", sa.Integer(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["review_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_events_created_at", "task_events", ["created_at"])
    op.create_index("ix_task_events_task_id_id", "task_events", ["task_id", "id"])


def downgrade() -> None:
    op.drop_index("ix_task_events_task_id_id", table_name="task_events")
    op.drop_index("ix_task_events_created_at", table_name="task_events")
    op.drop_table("task_events")
    op.drop_index("ix_review_issues_task_id", table_name="review_issues")
    op.drop_index("ix_review_issues_rule_code", table_name="review_issues")
    op.drop_index("ix_review_issues_public_id", table_name="review_issues")
    op.drop_index("ix_review_issues_created_at", table_name="review_issues")
    op.drop_table("review_issues")
    op.drop_index("ix_review_tasks_task_id", table_name="review_tasks")
    op.drop_index("ix_review_tasks_status", table_name="review_tasks")
    op.drop_index("ix_review_tasks_report_id", table_name="review_tasks")
    op.drop_index("ix_review_tasks_document_id", table_name="review_tasks")
    op.drop_index("ix_review_tasks_created_at", table_name="review_tasks")
    op.drop_table("review_tasks")
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_file_hash", table_name="documents")
    op.drop_index("ix_documents_created_at", table_name="documents")
    op.drop_table("documents")

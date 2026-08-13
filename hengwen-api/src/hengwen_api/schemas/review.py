from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from hengwen_api.schemas.common import CamelModel


class ReviewSettingsCreate(CamelModel):
    org_name: str = Field(default="", max_length=255)
    standard: str = Field(
        default="本科毕业论文规范（默认）",
        min_length=1,
        max_length=255,
    )
    check_format: bool = True
    check_citation: bool = True
    check_plagiarism: bool = False
    auto_report: bool = True


class ReviewTaskCreate(CamelModel):
    document_id: int = Field(gt=0)
    settings: ReviewSettingsCreate = Field(default_factory=ReviewSettingsCreate)


class AnalysisTaskResponse(CamelModel):
    id: str
    filename: str
    file_type: Literal[".docx", ".pdf", ".md"]
    stage_index: int
    progress: int
    started_at: datetime


class TaskStatusResponse(AnalysisTaskResponse):
    status: Literal["pending", "running", "completed", "failed"]
    stage: str
    report_id: str | None = None
    error_message: str | None = None


class TaskEventResponse(CamelModel):
    event_id: int
    task_id: str
    event_type: str
    stage: str | None = None
    stage_index: int | None = None
    progress: int
    level: str
    message: str
    data: dict[str, Any]

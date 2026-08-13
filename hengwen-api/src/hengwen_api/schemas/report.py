from datetime import datetime
from typing import Literal

from pydantic import Field

from hengwen_api.schemas.common import CamelModel

FileType = Literal[".docx", ".pdf", ".md"]


class IssueResponse(CamelModel):
    id: str
    severity: Literal["error", "warning", "info"]
    title: str
    location: str
    summary: str
    original: str
    suggestion: str


class ReportResponse(CamelModel):
    id: str
    filename: str
    file_type: FileType
    checked_at: datetime
    word_count: int
    score: int
    verdict: Literal["pass", "pending", "fail"]
    issues: list[IssueResponse]


class ReportPageResponse(CamelModel):
    items: list[ReportResponse]
    page: int
    page_size: int
    total: int


class ReportPagination(CamelModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

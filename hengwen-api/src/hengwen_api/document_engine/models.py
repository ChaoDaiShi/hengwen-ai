import re
from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["error", "warning", "info"]
Verdict = Literal["pass", "pending", "fail"]


@dataclass(slots=True)
class RunModel:
    text: str
    font_name: str | None = None
    font_size: float | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None


@dataclass(slots=True)
class ParagraphModel:
    index: int
    text: str
    style_name: str | None = None
    alignment: str | None = None
    line_spacing: float | None = None
    runs: list[RunModel] = field(default_factory=list)
    section: int = 0


@dataclass(slots=True)
class HeadingModel:
    paragraph_index: int
    text: str
    level: int


@dataclass(slots=True)
class TableModel:
    index: int
    rows: list[list[str]]
    caption: str | None = None


@dataclass(slots=True)
class FigureModel:
    index: int
    relationship_id: str | None = None
    caption: str | None = None


@dataclass(slots=True)
class ReferenceModel:
    index: int
    text: str
    number: int | None = None


@dataclass(slots=True)
class SectionModel:
    index: int
    top_margin: float | None = None
    right_margin: float | None = None
    bottom_margin: float | None = None
    left_margin: float | None = None
    header_text: str = ""
    footer_text: str = ""


@dataclass(slots=True)
class DocumentModel:
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    sections: list[SectionModel] = field(default_factory=list)
    paragraphs: list[ParagraphModel] = field(default_factory=list)
    headings: list[HeadingModel] = field(default_factory=list)
    tables: list[TableModel] = field(default_factory=list)
    figures: list[FigureModel] = field(default_factory=list)
    references: list[ReferenceModel] = field(default_factory=list)
    raw_text: str = ""

    @property
    def word_count(self) -> int:
        return len(re.findall(r"[\u3400-\u9fff]|[A-Za-z0-9]+", self.raw_text))


@dataclass(frozen=True, slots=True)
class RuleIssue:
    severity: Severity
    title: str
    location: str
    summary: str
    original: str
    suggestion: str
    rule_code: str
    issue_type: str

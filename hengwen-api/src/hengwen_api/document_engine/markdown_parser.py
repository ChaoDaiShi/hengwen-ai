import re
from pathlib import Path

from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.document_engine.models import (
    DocumentModel,
    HeadingModel,
    ParagraphModel,
    ReferenceModel,
    RunModel,
    TableModel,
)

ATX_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*$")
SETEXT_HEADING = re.compile(r"^\s*(=+|-+)\s*$")
REFERENCE_HEADING = re.compile(r"^#{1,6}\s*参考文献\s*#*$|^参考文献\s*$")
REFERENCE_ENTRY = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.、])\s*(.+)$")


def parse_markdown(path: Path) -> DocumentModel:
    try:
        raw_text = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError) as exc:
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "无法解析该 Markdown 文档",
            status_code=422,
        ) from exc
    if not raw_text.strip():
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "Markdown 文件没有可分析内容",
            status_code=422,
        )

    lines = raw_text.splitlines()
    paragraphs: list[ParagraphModel] = []
    headings: list[HeadingModel] = []
    references: list[ReferenceModel] = []
    quotes: list[str] = []
    tables: list[TableModel] = []
    in_references = False
    skip_indexes: set[int] = set()

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if SETEXT_HEADING.match(stripped) and index > 0 and lines[index - 1].strip():
            skip_indexes.add(index)
            continue
        atx_match = ATX_HEADING.match(stripped)
        if atx_match:
            heading_text = atx_match.group(2).strip()
            headings.append(
                HeadingModel(
                    paragraph_index=len(paragraphs),
                    text=heading_text,
                    level=len(atx_match.group(1)),
                )
            )
        elif index + 1 < len(lines) and SETEXT_HEADING.match(lines[index + 1].strip()):
            marker = lines[index + 1].strip()[0]
            headings.append(
                HeadingModel(
                    paragraph_index=len(paragraphs),
                    text=stripped,
                    level=1 if marker == "=" else 2,
                )
            )
        if stripped.startswith(">"):
            quotes.append(stripped.lstrip("> "))
        if REFERENCE_HEADING.match(stripped):
            in_references = True
        elif in_references:
            reference_match = REFERENCE_ENTRY.match(stripped)
            if reference_match:
                references.append(
                    ReferenceModel(
                        index=len(references),
                        text=stripped,
                        number=int(
                            reference_match.group(1) or reference_match.group(2)
                        ),
                    )
                )

    for index, line in enumerate(lines):
        if index in skip_indexes or not line.strip():
            continue
        text = line.strip()
        paragraphs.append(
            ParagraphModel(
                index=len(paragraphs),
                text=text,
                style_name="markdown",
                runs=[RunModel(text=text)],
            )
        )

    table_rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in lines
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if table_rows:
        tables.append(TableModel(index=0, rows=table_rows))

    return DocumentModel(
        file_type=".md",
        metadata={"source": path.name, "quotes": quotes},
        paragraphs=paragraphs,
        headings=headings,
        tables=tables,
        references=references,
        raw_text=raw_text,
    )

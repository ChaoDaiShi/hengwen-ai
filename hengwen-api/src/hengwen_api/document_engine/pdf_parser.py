import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.document_engine.models import (
    DocumentModel,
    HeadingModel,
    ParagraphModel,
    ReferenceModel,
    RunModel,
)

NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
REFERENCE_HEADING = re.compile(r"^参考文献\s*$")
REFERENCE_ENTRY = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.、])\s*(.+)$")


def parse_pdf(path: Path) -> DocumentModel:
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise PdfReadError("encrypted PDF")
        page_text = [(page.extract_text() or "").strip() for page in reader.pages]
    except (PdfReadError, OSError, ValueError, KeyError) as exc:
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "无法提取该 PDF 的文本",
            status_code=422,
        ) from exc

    raw_text = "\n".join(text for text in page_text if text)
    if not raw_text.strip():
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "PDF 没有可提取的文本",
            status_code=422,
        )

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    paragraphs = [
        ParagraphModel(
            index=index,
            text=line,
            style_name=None,
            runs=[RunModel(text=line)],
        )
        for index, line in enumerate(lines)
    ]
    headings: list[HeadingModel] = []
    references: list[ReferenceModel] = []
    in_references = False
    for index, line in enumerate(lines):
        heading_match = NUMBERED_HEADING.match(line)
        if heading_match and len(line) <= 80:
            headings.append(
                HeadingModel(
                    paragraph_index=index,
                    text=line,
                    level=heading_match.group(1).count(".") + 1,
                )
            )
        if REFERENCE_HEADING.match(line):
            in_references = True
            continue
        if in_references:
            reference_match = REFERENCE_ENTRY.match(line)
            if reference_match:
                references.append(
                    ReferenceModel(
                        index=len(references),
                        text=line,
                        number=int(
                            reference_match.group(1) or reference_match.group(2)
                        ),
                    )
                )

    return DocumentModel(
        file_type=".pdf",
        metadata={"source": path.name, "page_count": len(reader.pages)},
        paragraphs=paragraphs,
        headings=headings,
        references=references,
        raw_text=raw_text,
    )

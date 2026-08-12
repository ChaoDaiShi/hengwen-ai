from pathlib import Path

from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.document_engine.docx_parser import parse_docx
from hengwen_api.document_engine.markdown_parser import parse_markdown
from hengwen_api.document_engine.models import DocumentModel
from hengwen_api.document_engine.pdf_parser import parse_pdf


def parse_document(path: Path, file_type: str) -> DocumentModel:
    normalized_type = file_type.lower()
    if normalized_type == ".docx":
        return parse_docx(path)
    if normalized_type == ".md":
        return parse_markdown(path)
    if normalized_type == ".pdf":
        return parse_pdf(path)
    raise AppError(
        ErrorCode.INVALID_FILE_TYPE,
        "不支持的文档类型",
        status_code=415,
    )

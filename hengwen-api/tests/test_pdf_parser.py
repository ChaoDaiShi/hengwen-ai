from pathlib import Path

import pytest

from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.document_engine.parser import parse_document
from tests.factories import build_pdf_bytes


def test_pdf_parser_extracts_text_without_word_format_claims(tmp_path: Path) -> None:
    path = tmp_path / "paper.pdf"
    path.write_bytes(build_pdf_bytes("HengWen PDF Review"))

    model = parse_document(path, ".pdf")

    assert "HengWen PDF Review" in model.raw_text
    assert model.file_type == ".pdf"
    assert model.sections == []
    assert all(run.font_name is None for item in model.paragraphs for run in item.runs)


def test_pdf_parser_rejects_invalid_pdf(tmp_path: Path) -> None:
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-invalid")

    with pytest.raises(AppError) as captured:
        parse_document(path, ".pdf")

    assert captured.value.code == ErrorCode.INVALID_DOCUMENT


def test_parser_rejects_unknown_file_type(tmp_path: Path) -> None:
    path = tmp_path / "paper.txt"
    path.write_text("content", encoding="utf-8")

    with pytest.raises(AppError) as captured:
        parse_document(path, ".txt")

    assert captured.value.code == ErrorCode.INVALID_FILE_TYPE

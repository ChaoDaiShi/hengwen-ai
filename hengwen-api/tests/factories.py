from io import BytesIO

from docx import Document as DocxDocument

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def build_docx_bytes(*paragraphs: str) -> bytes:
    document = DocxDocument()
    for text in paragraphs or ("衡文测试文档",):
        document.add_paragraph(text)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def build_pdf_bytes() -> bytes:
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF"

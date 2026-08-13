import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from hengwen_api.core.config import Settings
from hengwen_api.repositories.document_repository import DocumentRepository
from tests.factories import DOCX_MIME, build_pdf_bytes


def test_upload_docx_uses_generated_path(
    client: TestClient,
    docx_bytes: bytes,
    session_factory: sessionmaker[Session],
    settings: Settings,
) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("../../论文.docx", docx_bytes, DOCX_MIME)},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "论文.docx"
    assert body["fileType"] == ".docx"
    assert body["fileHash"] == hashlib.sha256(docx_bytes).hexdigest()
    assert set(body) == {
        "id",
        "filename",
        "fileType",
        "fileSize",
        "fileHash",
        "status",
        "createdAt",
    }
    with session_factory() as session:
        document = DocumentRepository(session).get(body["id"])
        assert document is not None
        stored_path = settings.storage_dir / document.storage_path
    assert stored_path.is_relative_to(settings.storage_dir)
    assert stored_path.name != "论文.docx"
    assert stored_path.read_bytes() == docx_bytes


@pytest.mark.parametrize("name", ["paper.exe", "paper.doc", "paper.docx.exe"])
def test_rejects_invalid_extension(client: TestClient, name: str) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": (name, b"x", "application/octet-stream")},
    )

    assert response.status_code == 415
    assert response.json()["code"] == "INVALID_FILE_TYPE"
    assert response.json()["requestId"].startswith("req_")


def test_rejects_file_larger_than_configured_limit(
    small_limit_client: TestClient,
) -> None:
    response = small_limit_client.post(
        "/api/v1/documents",
        files={"file": ("large.md", b"a" * (1024 * 1024 + 1), "text/markdown")},
    )

    assert response.status_code == 413
    assert response.json()["code"] == "FILE_TOO_LARGE"


def test_rejects_fake_pdf_and_removes_partial_file(
    client: TestClient,
    storage_dir: Path,
) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("fake.pdf", b"not-pdf", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_DOCUMENT"
    assert [path for path in storage_dir.rglob("*") if path.is_file()] == []


def test_rejects_corrupt_docx(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("broken.docx", b"PK-not-openxml", DOCX_MIME)},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_DOCUMENT"


def test_rejects_non_utf8_markdown(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("broken.md", b"\xff\xfe\x00", "text/markdown")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_DOCUMENT"


@pytest.mark.parametrize(
    ("filename", "content", "mime"),
    [
        ("valid.pdf", build_pdf_bytes(), "application/pdf"),
        ("valid.md", "# 标题\n\n正文".encode(), "text/markdown"),
    ],
)
def test_accepts_valid_pdf_and_markdown(
    client: TestClient,
    filename: str,
    content: bytes,
    mime: str,
) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": (filename, content, mime)},
    )

    assert response.status_code == 201
    assert response.json()["fileHash"] == hashlib.sha256(content).hexdigest()

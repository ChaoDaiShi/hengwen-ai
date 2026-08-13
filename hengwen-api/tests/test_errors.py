import logging
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from hengwen_api.core.config import Settings
from hengwen_api.main import create_app
from hengwen_api.repositories.document_repository import DocumentRepository


def test_database_error_is_safe_and_removes_uploaded_file(
    client: TestClient,
    storage_dir: Path,
    monkeypatch,
    caplog,
) -> None:
    document_body = "# 不应进入日志的论文正文：HENGWEN-BODY-SECRET"
    database_secret = "mysql+pymysql://root:HENGWEN-DB-SECRET@db.example/hengwen"

    def fail_create(*args, **kwargs):
        raise SQLAlchemyError(database_secret)

    monkeypatch.setattr(DocumentRepository, "create", fail_create)
    caplog.set_level(logging.INFO)

    response = client.post(
        "/api/v1/documents",
        files={"file": ("论文.md", document_body.encode(), "text/markdown")},
    )

    assert response.status_code == 500
    assert response.json() == {
        "code": "DATABASE_ERROR",
        "message": "数据库操作失败",
        "details": None,
        "requestId": response.headers["x-request-id"],
    }
    assert database_secret not in response.text
    assert document_body not in caplog.text
    assert database_secret not in caplog.text
    assert [path for path in storage_dir.rglob("*") if path.is_file()] == []


def test_unexpected_error_logs_only_exception_type(
    settings: Settings,
    session_factory: sessionmaker[Session],
    monkeypatch,
    caplog,
) -> None:
    api_secret = "sk-HENGWEN-API-SECRET"

    def fail_create(*args, **kwargs):
        raise RuntimeError(api_secret)

    monkeypatch.setattr(DocumentRepository, "create", fail_create)
    caplog.set_level(logging.ERROR)

    with TestClient(
        create_app(settings=settings, session_factory=session_factory),
        raise_server_exceptions=False,
    ) as safe_client:
        response = safe_client.post(
            "/api/v1/documents",
            files={"file": ("论文.md", b"# title", "text/markdown")},
        )

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_SERVER_ERROR"
    assert response.headers["x-request-id"] == response.json()["requestId"]
    assert "RuntimeError" in caplog.text
    assert api_secret not in caplog.text

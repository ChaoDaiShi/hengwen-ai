from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from hengwen_api.core.config import Settings
from hengwen_api.db.base import Base
from hengwen_api.db.session import create_engine_for_url, create_session_factory
from hengwen_api.main import create_app
from tests.factories import DOCX_MIME, build_docx_bytes, build_structured_docx


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{(tmp_path / 'test.sqlite').as_posix()}"


@pytest.fixture
def db_engine(database_url: str) -> Iterator[Engine]:
    engine = create_engine_for_url(database_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(db_engine: Engine) -> sessionmaker[Session]:
    return create_session_factory(db_engine)


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


@pytest.fixture
def settings(tmp_path: Path, database_url: str) -> Settings:
    return Settings(
        env="test",
        database_url=database_url,
        storage_dir=tmp_path / "storage",
        max_file_size_mb=20,
        sse_poll_interval_seconds=0.01,
        sse_keepalive_seconds=0.01,
    )


@pytest.fixture
def client(
    settings: Settings,
    session_factory: sessionmaker[Session],
) -> Iterator[TestClient]:
    with TestClient(
        create_app(settings=settings, session_factory=session_factory)
    ) as test_client:
        yield test_client


@pytest.fixture
def storage_dir(settings: Settings) -> Path:
    return settings.storage_dir


@pytest.fixture
def docx_bytes() -> bytes:
    return build_docx_bytes("衡文测试文档")


@pytest.fixture
def small_limit_client(
    settings: Settings,
    session_factory: sessionmaker[Session],
) -> Iterator[TestClient]:
    small_settings = settings.model_copy(update={"max_file_size_mb": 1})
    with TestClient(
        create_app(settings=small_settings, session_factory=session_factory)
    ) as test_client:
        yield test_client


@pytest.fixture
def valid_thesis_docx(tmp_path: Path) -> bytes:
    return build_structured_docx(tmp_path / "thesis.docx").read_bytes()


@pytest.fixture
def uploaded_document_id(client: TestClient, valid_thesis_docx: bytes) -> int:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("毕业论文.docx", valid_thesis_docx, DOCX_MIME)},
    )
    assert response.status_code == 201
    return int(response.json()["id"])

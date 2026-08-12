from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from hengwen_api.core.config import Settings
from hengwen_api.db.session import SessionFactory


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_factory(request: Request) -> SessionFactory:
    session_factory: SessionFactory | None = request.app.state.session_factory
    if session_factory is None:
        raise RuntimeError("Database session factory is not configured")
    return session_factory


def get_session(request: Request) -> Iterator[Session]:
    session_factory = get_session_factory(request)
    with session_factory() as session:
        yield session

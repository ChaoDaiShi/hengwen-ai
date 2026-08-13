import logging
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from hengwen_api import __version__
from hengwen_api.api.v1.router import router as v1_router
from hengwen_api.core.config import Settings, get_settings
from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.core.logging import configure_logging
from hengwen_api.db.session import create_engine_for_url, create_session_factory
from hengwen_api.schemas.common import ErrorResponse
from hengwen_api.workers.review_worker import recover_stale_tasks

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", f"req_{uuid4().hex}")


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    content = ErrorResponse(
        code=code,
        message=message,
        details=details,
        request_id=_request_id(request),
    ).model_dump(by_alias=True)
    return JSONResponse(status_code=status_code, content=content)


def create_app(
    settings: Settings | None = None,
    session_factory: Any = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    owned_engine = None
    if session_factory is None:
        owned_engine = create_engine_for_url(resolved_settings.database_url)
        session_factory = create_session_factory(owned_engine)

    @asynccontextmanager
    async def lifespan(_application: FastAPI):
        recover_stale_tasks(session_factory)
        yield
        if owned_engine is not None:
            owned_engine.dispose()

    application = FastAPI(
        title="衡文 AI API",
        version=__version__,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    application.state.engine = owned_engine
    application.state.session_factory = session_factory
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def add_request_context(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or f"req_{uuid4().hex}"
        request.state.request_id = request_id
        started_at = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request completed method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started_at) * 1000,
            extra={"request_id": request_id},
        )
        return response

    @application.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(
            request,
            status_code=422,
            code=ErrorCode.VALIDATION_ERROR,
            message="请求参数无效",
            details=exc.errors(),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled request error exception=%s",
            type(exc).__name__,
            extra={"request_id": _request_id(request)},
        )
        return _error_response(
            request,
            status_code=500,
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="服务器内部错误",
        )

    application.include_router(v1_router)
    return application


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "hengwen_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )

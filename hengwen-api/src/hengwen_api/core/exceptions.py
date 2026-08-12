from enum import StrEnum
from http import HTTPStatus
from typing import Any


class ErrorCode(StrEnum):
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_DOCUMENT = "INVALID_DOCUMENT"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    REPORT_NOT_FOUND = "REPORT_NOT_FOUND"
    INVALID_TASK_STATE = "INVALID_TASK_STATE"
    REVIEW_FAILED = "REVIEW_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status_code: int = HTTPStatus.BAD_REQUEST,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

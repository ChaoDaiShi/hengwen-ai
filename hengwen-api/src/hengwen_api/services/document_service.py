import hashlib
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import UploadFile
from sqlalchemy.orm import Session

from hengwen_api.core.config import Settings
from hengwen_api.core.exceptions import AppError, ErrorCode
from hengwen_api.models.document import Document
from hengwen_api.repositories.document_repository import DocumentRepository

ALLOWED_FILE_TYPES = {".docx", ".pdf", ".md"}
UPLOAD_CHUNK_SIZE = 64 * 1024


def _safe_display_name(filename: str | None) -> str:
    if not filename:
        return "document"
    normalized = filename.replace("\\", "/")
    return Path(normalized).name or "document"


def _validate_docx(path: Path) -> None:
    try:
        with ZipFile(path) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise AppError(
                    ErrorCode.INVALID_DOCUMENT,
                    "DOCX 文件结构无效",
                    status_code=422,
                )
            archive.read("word/document.xml")
    except (BadZipFile, KeyError, OSError) as exc:
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "DOCX 文件结构无效",
            status_code=422,
        ) from exc


def _validate_pdf(path: Path) -> None:
    with path.open("rb") as source:
        if source.read(5) != b"%PDF-":
            raise AppError(
                ErrorCode.INVALID_DOCUMENT,
                "PDF 文件头无效",
                status_code=422,
            )


def _validate_markdown(path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "Markdown 文件编码无效",
            status_code=422,
        ) from exc
    if not content.strip():
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "Markdown 文件没有可分析内容",
            status_code=422,
        )


def _validate_file(path: Path, file_type: str) -> None:
    if path.stat().st_size == 0:
        raise AppError(
            ErrorCode.INVALID_DOCUMENT,
            "文件没有可分析内容",
            status_code=422,
        )
    if file_type == ".docx":
        _validate_docx(path)
    elif file_type == ".pdf":
        _validate_pdf(path)
    else:
        _validate_markdown(path)


class DocumentService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repository = DocumentRepository(session)

    async def store(self, upload: UploadFile) -> Document:
        original_name = _safe_display_name(upload.filename)
        file_type = Path(original_name).suffix.lower()
        if file_type not in ALLOWED_FILE_TYPES:
            raise AppError(
                ErrorCode.INVALID_FILE_TYPE,
                "仅支持 .docx / .pdf / .md 文件",
                status_code=415,
            )

        now = datetime.now().astimezone()
        relative_directory = Path("uploads") / str(now.year) / f"{now.month:02d}"
        target_directory = self.settings.storage_dir / relative_directory
        target_directory.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4().hex}{file_type}"
        final_path = target_directory / stored_name
        temporary_path = target_directory / f".{stored_name}.part"
        digest = hashlib.sha256()
        file_size = 0

        try:
            with temporary_path.open("xb") as destination:
                while chunk := await upload.read(UPLOAD_CHUNK_SIZE):
                    file_size += len(chunk)
                    if file_size > self.settings.max_file_size_bytes:
                        raise AppError(
                            ErrorCode.FILE_TOO_LARGE,
                            f"文件大小不能超过 {self.settings.max_file_size_mb} MB",
                            status_code=413,
                        )
                    destination.write(chunk)
                    digest.update(chunk)

            _validate_file(temporary_path, file_type)
            temporary_path.replace(final_path)
            document = self.repository.create(
                original_name=original_name,
                stored_name=stored_name,
                file_type=file_type,
                file_size=file_size,
                file_hash=digest.hexdigest(),
                storage_path=str(relative_directory / stored_name).replace("\\", "/"),
            )
            self.session.commit()
            return document
        except Exception:
            self.session.rollback()
            temporary_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

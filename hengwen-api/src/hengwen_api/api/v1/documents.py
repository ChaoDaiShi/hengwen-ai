from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from hengwen_api.api.dependencies import get_app_settings, get_session
from hengwen_api.core.config import Settings
from hengwen_api.schemas.document import DocumentResponse
from hengwen_api.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> DocumentResponse:
    document = await DocumentService(session, settings).store(file)
    return DocumentResponse(
        id=document.id,
        filename=document.original_name,
        file_type=document.file_type,
        file_size=document.file_size,
        file_hash=document.file_hash,
        status=document.status,
        created_at=document.created_at,
    )

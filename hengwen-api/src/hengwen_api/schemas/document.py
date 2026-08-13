from hengwen_api.schemas.common import CamelModel, UtcDateTime


class DocumentResponse(CamelModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    file_hash: str
    status: str
    created_at: UtcDateTime

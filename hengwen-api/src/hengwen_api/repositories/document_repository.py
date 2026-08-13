from sqlalchemy.orm import Session

from hengwen_api.models.document import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        original_name: str,
        stored_name: str,
        file_type: str,
        file_size: int,
        file_hash: str,
        storage_path: str,
        status: str = "uploaded",
    ) -> Document:
        document = Document(
            original_name=original_name,
            stored_name=stored_name,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            storage_path=storage_path,
            status=status,
        )
        self.session.add(document)
        self.session.flush()
        return document

    def get(self, document_id: int) -> Document | None:
        return self.session.get(Document, document_id)

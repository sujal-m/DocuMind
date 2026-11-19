from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models import Document, DocumentChunk

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_hash(self, file_hash: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.file_hash == file_hash).first()

    def get_by_name(self, filename: str) -> Optional[Document]:
        return self.db.query(Document).filter(
            (Document.original_name == filename) | (Document.filename == filename)
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        return (
            self.db.query(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update_status(
        self,
        document_id: str,
        status: str,
        page_count: Optional[int] = None,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        doc = self.get_by_id(document_id)
        if not doc:
            return None
        doc.status = status
        if page_count is not None:
            doc.page_count = page_count
        if chunk_count is not None:
            doc.chunk_count = chunk_count
        if error_message is not None:
            doc.error_message = error_message
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, document_id: str) -> bool:
        doc = self.get_by_id(document_id)
        if not doc:
            return False
        self.db.delete(doc)
        self.db.commit()
        return True


from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models import DocumentChunk

class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    def get_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    def get_by_faiss_id(self, faiss_id: int) -> Optional[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(DocumentChunk.faiss_id == faiss_id).first()

    def get_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()

    def get_all(self) -> List[DocumentChunk]:
        return self.db.query(DocumentChunk).order_by(DocumentChunk.created_at.asc()).all()

    def bulk_create(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.db.add_all(chunks)
        self.db.commit()
        return chunks

    def delete_by_document_id(self, document_id: str) -> int:
        deleted = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted

    def update_faiss_ids(self, chunk_faiss_map: dict[str, int]):
        """
        Updates faiss_id mapping for a batch of chunk IDs.
        """
        for chunk_id, f_id in chunk_faiss_map.items():
            self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).update({"faiss_id": f_id})
        self.db.commit()


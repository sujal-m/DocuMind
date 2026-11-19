from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore
from backend.app.schemas.search import RetrievedPassage

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.chunk_repo = ChunkRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        min_score: Optional[float] = None
    ) -> List[RetrievedPassage]:
        """
        Executes semantic vector retrieval across document chunks with metadata filtering.
        """
        if not query or not query.strip():
            return []

        threshold = min_score if min_score is not None else settings.SIMILARITY_THRESHOLD

        # 1. Resolve allowed chunk IDs if filtering by document_ids
        allowed_chunk_ids = None
        if document_ids:
            allowed_chunks = []
            for doc_id in document_ids:
                allowed_chunks.extend(self.chunk_repo.get_by_document_id(doc_id))
            allowed_chunk_ids = {c.id for c in allowed_chunks}
            if not allowed_chunk_ids:
                logger.info(f"No chunks found for filtered document IDs: {document_ids}")
                return []

        # 2. Vectorize user query
        query_vec = self.embedding_service.embed_text(query)

        # 3. Search FAISS index
        raw_matches = self.vector_store.search(
            query_embedding=query_vec,
            top_k=top_k,
            allowed_chunk_ids=allowed_chunk_ids
        )

        if not raw_matches:
            logger.info(f"Zero vector matches for query: '{query}'")
            return []

        # 4. Filter by similarity threshold
        filtered_matches = [(cid, score) for cid, score in raw_matches if score >= threshold]
        if not filtered_matches:
            logger.info(f"All {len(raw_matches)} matches fell below threshold {threshold}")
            # If nothing matched above threshold, return top 1 if close to avoid total blackout
            if raw_matches and raw_matches[0][1] >= 0.20:
                filtered_matches = [raw_matches[0]]
            else:
                return []

        # 5. Hydrate chunks with document metadata
        chunk_ids = [cid for cid, _ in filtered_matches]
        chunks = self.chunk_repo.get_by_ids(chunk_ids)
        chunk_map = {c.id: c for c in chunks}

        # Cache document names to prevent repeated DB queries
        doc_names = {}
        for c in chunks:
            if c.document_id not in doc_names:
                doc = self.doc_repo.get_by_id(c.document_id)
                doc_names[c.document_id] = doc.original_name if doc else "Unknown Document"

        # 6. Assemble ordered RetrievedPassage objects
        results: List[RetrievedPassage] = []
        for cid, score in filtered_matches:
            chunk = chunk_map.get(cid)
            if not chunk:
                continue

            results.append(RetrievedPassage(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_name=doc_names.get(chunk.document_id, "Unknown Document"),
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity_score=round(score, 4),
                token_count=chunk.token_count
            ))

        return results

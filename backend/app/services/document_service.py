import os
import shutil
from typing import List, Optional, Tuple
from fastapi import UploadFile, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.security import sanitize_filename, validate_file_metadata
from backend.app.utils.hashing import calculate_sha256
from backend.app.models import Document, DocumentChunk
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.services.extraction_service import ExtractionService, ExtractionError
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def process_document_background(self, document_id: str, file_path: str, file_type: str):
        """
        Executes extraction, chunking, embedding, and vector indexing in the background.
        """
        logger.info(f"Starting background processing for document: {document_id}")
        self.doc_repo.update_status(document_id, status="processing")

        try:
            # 1. Text & metadata extraction
            pages_data, total_pages = ExtractionService.extract(file_path, file_type)

            # 2. Chunking
            chunks_data = self.chunking_service.chunk_pages(pages_data, document_id)
            if not chunks_data:
                raise ExtractionError("Chunking resulted in 0 chunks.")

            # 3. Embedding generation
            chunk_texts = [c["content"] for c in chunks_data]
            embeddings = self.embedding_service.embed_batch(chunk_texts)

            # 4. Create chunk records in SQLite
            chunk_models = []
            for c_data in chunks_data:
                c_model = DocumentChunk(
                    document_id=document_id,
                    chunk_index=c_data["chunk_index"],
                    page_number=c_data["page_number"],
                    content=c_data["content"],
                    token_count=c_data["token_count"]
                )
                chunk_models.append(c_model)

            created_chunks = self.chunk_repo.bulk_create(chunk_models)
            chunk_ids = [c.id for c in created_chunks]

            # 5. Add embeddings to FAISS
            faiss_ids = self.vector_store.add_embeddings(chunk_ids, embeddings)

            # 6. Map FAISS IDs back to chunks
            chunk_faiss_map = {cid: fid for cid, fid in zip(chunk_ids, faiss_ids)}
            self.chunk_repo.update_faiss_ids(chunk_faiss_map)

            # 7. Update document status
            self.doc_repo.update_status(
                document_id,
                status="indexed",
                page_count=total_pages,
                chunk_count=len(created_chunks)
            )
            logger.info(f"Successfully indexed document {document_id} with {len(created_chunks)} chunks.")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process document {document_id}: {error_msg}")
            self.doc_repo.update_status(document_id, status="error", error_message=error_msg)

    async def upload_document(
        self,
        file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> Tuple[Document, bool]:
        """
        Validates, saves, detects duplicates, and enqueues document for indexing.
        Returns: (document, is_duplicate)
        """
        # Validate metadata
        original_name = file.filename or "unknown_file"
        file_bytes = await file.read()
        file_size = len(file_bytes)
        ext = validate_file_metadata(original_name, file_size, file.content_type)
        file_hash = calculate_sha256(file_bytes)

        # Check for duplicates
        existing = self.doc_repo.get_by_hash(file_hash)
        if existing and existing.status == "indexed":
            logger.info(f"Document with hash {file_hash} already indexed (ID: {existing.id}).")
            return existing, True

        # Save to disk
        safe_name = sanitize_filename(original_name)
        storage_filename = f"{file_hash[:16]}_{safe_name}"
        destination_path = os.path.join(settings.UPLOAD_DIR, storage_filename)

        with open(destination_path, "wb") as f:
            f.write(file_bytes)

        # If document existed with error, reuse or create new
        if existing and existing.status == "error":
            doc = existing
            doc.filename = storage_filename
            doc.status = "pending"
            doc.error_message = None
            self.db.commit()
            self.db.refresh(doc)
        else:
            doc = Document(
                filename=storage_filename,
                original_name=original_name,
                file_type=ext.lstrip("."),
                file_size=file_size,
                file_hash=file_hash,
                status="pending"
            )
            doc = self.doc_repo.create(doc)

        # Trigger background processing
        background_tasks.add_task(
            self.process_document_background,
            doc.id,
            destination_path,
            doc.file_type
        )

        return doc, False

    def list_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        return self.doc_repo.get_all(skip=skip, limit=limit)

    def get_document(self, document_id: str) -> Optional[Document]:
        return self.doc_repo.get_by_id(document_id)

    def delete_document(self, document_id: str) -> bool:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            return False

        # 1. Fetch chunks to remove from FAISS
        chunks = self.chunk_repo.get_by_document_id(document_id)
        chunk_ids = [c.id for c in chunks]
        self.vector_store.remove_chunks(chunk_ids)

        # 2. Delete file from disk if no other document shares this file
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete disk file {file_path}: {e}")

        # 3. Delete from DB (cascading deletes chunks)
        return self.doc_repo.delete(document_id)

    def reindex_document(self, document_id: str, background_tasks: BackgroundTasks) -> Document:
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source file not found on disk")

        # 1. Clean existing chunks
        chunks = self.chunk_repo.get_by_document_id(document_id)
        chunk_ids = [c.id for c in chunks]
        self.vector_store.remove_chunks(chunk_ids)
        self.chunk_repo.delete_by_document_id(document_id)

        # 2. Reset status
        self.doc_repo.update_status(document_id, status="pending", error_message=None)

        # 3. Enqueue background indexing
        background_tasks.add_task(
            self.process_document_background,
            doc.id,
            file_path,
            doc.file_type
        )
        return doc


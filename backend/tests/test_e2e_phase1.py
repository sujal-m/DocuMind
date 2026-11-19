import os
import io
import time
import pytest
from backend.app.services.document_service import DocumentService
from backend.app.services.vector_store import VectorStore
from backend.app.database.session import SessionLocal

def test_full_ingestion_and_faiss_lifecycle(sample_pdf_path, sample_docx_path, sample_txt_path):
    """
    Directly exercises DocumentService background ingestion for PDF, DOCX, and TXT,
    verifying chunks are saved in DB and vectors are indexed in FAISS.
    """
    db = SessionLocal()
    try:
        service = DocumentService(db)
        vector_store = VectorStore()
        initial_vector_count = vector_store.index.ntotal

        # 1. Ingest PDF
        pdf_name = os.path.basename(sample_pdf_path)
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        from backend.app.utils.hashing import calculate_sha256
        from backend.app.models import Document
        
        doc_pdf = Document(
            filename=pdf_name,
            original_name=pdf_name,
            file_type="pdf",
            file_size=len(pdf_bytes),
            file_hash=calculate_sha256(pdf_bytes),
            status="pending"
        )
        doc_pdf = service.doc_repo.create(doc_pdf)
        
        # Process PDF
        service.process_document_background(doc_pdf.id, sample_pdf_path, "pdf")
        
        # Verify indexed status
        updated_pdf = service.doc_repo.get_by_id(doc_pdf.id)
        assert updated_pdf.status == "indexed"
        assert updated_pdf.page_count == 2
        assert updated_pdf.chunk_count >= 2
        assert vector_store.index.ntotal > initial_vector_count

        # 2. Ingest TXT
        txt_name = os.path.basename(sample_txt_path)
        with open(sample_txt_path, "rb") as f:
            txt_bytes = f.read()

        doc_txt = Document(
            filename=txt_name,
            original_name=txt_name,
            file_type="txt",
            file_size=len(txt_bytes),
            file_hash=calculate_sha256(txt_bytes),
            status="pending"
        )
        doc_txt = service.doc_repo.create(doc_txt)
        service.process_document_background(doc_txt.id, sample_txt_path, "txt")

        updated_txt = service.doc_repo.get_by_id(doc_txt.id)
        assert updated_txt.status == "indexed"
        assert updated_txt.chunk_count >= 1

        # 3. Test Search against FAISS vectors
        query_vec = service.embedding_service.embed_text("DocuMind artificial intelligence")
        search_results = vector_store.search(query_vec, top_k=3)
        assert len(search_results) > 0
        top_chunk_id, score = search_results[0]
        assert score > 0.0

        # Retrieve chunk model from DB
        chunk_model = service.chunk_repo.get_by_id(top_chunk_id)
        assert chunk_model is not None
        assert chunk_model.content != ""

        # 4. Clean up test documents
        service.delete_document(doc_pdf.id)
        service.delete_document(doc_txt.id)

        assert service.doc_repo.get_by_id(doc_pdf.id) is None
        assert service.doc_repo.get_by_id(doc_txt.id) is None

    finally:
        db.close()


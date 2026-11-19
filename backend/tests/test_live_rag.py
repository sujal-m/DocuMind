import os
import pytest
from backend.app.core.config import settings
from backend.app.schemas.rag import RAGQueryRequest
from backend.app.services.rag_service import RAGService
from backend.app.services.document_service import DocumentService
from backend.app.database.session import SessionLocal

@pytest.mark.skipif(not settings.GEMINI_API_KEY, reason="Requires GEMINI_API_KEY in settings")
def test_live_rag_with_gemini(sample_txt_path):
    """
    Live integration test executing actual retrieval and calling Google Gemini.
    """
    db = SessionLocal()
    try:
        doc_service = DocumentService(db)
        
        # 1. Ingest test doc
        with open(sample_txt_path, "rb") as f:
            content = f.read()
        
        from backend.app.models import Document
        from backend.app.utils.hashing import calculate_sha256
        
        doc = Document(
            filename="live_test.txt",
            original_name="live_test.txt",
            file_type="txt",
            file_size=len(content),
            file_hash=calculate_sha256(content),
            status="pending"
        )
        doc = doc_service.doc_repo.create(doc)
        doc_service.process_document_background(doc.id, sample_txt_path, "txt")
        
        # 2. Run real RAG query
        rag_service = RAGService(db)
        req = RAGQueryRequest(
            question="What methods and models does DocuMind use according to the text?",
            document_ids=[doc.id],
            top_k=3
        )
        
        response = rag_service.answer_query(req)
        
        assert response.answer is not None
        assert len(response.answer) > 10
        assert len(response.retrieved_passages) > 0
        assert response.confidence in ("high", "medium")
        assert response.model_name != ""
        
        # Clean up
        doc_service.delete_document(doc.id)
        
    finally:
        db.close()

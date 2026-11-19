import pytest
from unittest.mock import MagicMock
from backend.app.schemas.search import RetrievedPassage
from backend.app.schemas.rag import RAGQueryRequest
from backend.app.services.rag_service import RAGService
from backend.app.services.retrieval_service import RetrievalService

def test_rag_citation_extraction():
    service = RAGService(db=None)
    passages = [
        RetrievedPassage(
            chunk_id="chunk-1",
            document_id="doc-1",
            document_name="AI_Specs.pdf",
            page_number=3,
            chunk_index=0,
            content="DocuMind uses FAISS for vector search with 384 dimensions.",
            similarity_score=0.88,
            token_count=12
        ),
        RetrievedPassage(
            chunk_id="chunk-2",
            document_id="doc-1",
            document_name="AI_Specs.pdf",
            page_number=4,
            chunk_index=1,
            content="SentenceTransformers generates normalized L2 embeddings.",
            similarity_score=0.82,
            token_count=10
        )
    ]

    answer = "DocuMind implements FAISS [1] and sentence embeddings [2] for search."
    citations = service._extract_citations(answer, passages)

    assert len(citations) == 2
    assert citations[0].index == 1
    assert citations[0].chunk_id == "chunk-1"
    assert citations[0].page_number == 3
    assert citations[1].index == 2
    assert citations[1].chunk_id == "chunk-2"
    assert citations[1].page_number == 4

def test_rag_fallback_when_empty_context():
    service = RAGService(db=None)
    service.retrieval_service = MagicMock()
    service.retrieval_service.retrieve.return_value = []

    req = RAGQueryRequest(question="What is the quantum encryption key?")
    res = service.answer_query(req)

    assert "do not contain information" in res.answer.lower()
    assert res.confidence == "insufficient_data"
    assert len(res.citations) == 0
    assert len(res.retrieved_passages) == 0

def test_rag_generation_mocked():
    service = RAGService(db=None)
    service.retrieval_service = MagicMock()
    service.gemini_service = MagicMock()

    service.retrieval_service.retrieve.return_value = [
        RetrievedPassage(
            chunk_id="c-100",
            document_id="d-1",
            document_name="Architecture.docx",
            page_number=1,
            chunk_index=0,
            content="DocuMind utilizes SQLite with repository pattern for persistence.",
            similarity_score=0.91,
            token_count=10
        )
    ]
    service.gemini_service.generate_content.return_value = {
        "text": "The persistence layer uses SQLite with repository abstractions [1].",
        "model_used": "gemini-3.1-flash-lite"
    }

    req = RAGQueryRequest(question="What database does DocuMind use?")
    res = service.answer_query(req)

    assert "SQLite" in res.answer
    assert len(res.citations) == 1
    assert res.citations[0].document_name == "Architecture.docx"
    assert res.confidence in ("high", "medium")

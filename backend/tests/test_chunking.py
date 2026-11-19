from backend.app.services.chunking_service import ChunkingService

def test_chunking_preserves_page_numbers():
    service = ChunkingService(chunk_size=50, chunk_overlap=10)
    pages = [
        {"page_number": 1, "text": "This is page one text discussing vector similarity retrieval in depth."},
        {"page_number": 2, "text": "This is page two text discussing Google Gemini reasoning and prompt engineering."}
    ]
    chunks = service.chunk_pages(pages, document_id="doc-123")
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["document_id"] == "doc-123"
    assert chunks[0]["chunk_index"] == 0
    assert any(c["page_number"] == 2 for c in chunks)

def test_chunking_large_text():
    service = ChunkingService(chunk_size=20, chunk_overlap=5)
    long_para = "Sentence one. " * 30
    pages = [{"page_number": 1, "text": long_para}]
    chunks = service.chunk_pages(pages, document_id="doc-long")
    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c["chunk_index"] == i
        assert len(c["content"]) > 0


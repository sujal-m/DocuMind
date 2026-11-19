import os
import pytest
from backend.app.core.config import settings
from backend.app.database.session import SessionLocal
from backend.app.schemas.agent import AgentChatRequest
from backend.app.services.document_service import DocumentService
from backend.app.services.agent_service import AgentService

@pytest.mark.skipif(not settings.GEMINI_API_KEY, reason="Requires GEMINI_API_KEY in settings")
def test_live_agent_function_calling_and_memory(sample_txt_path):
    """
    Live test verifying Gemini Function Calling loop and multi-turn conversational memory.
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
            filename="agent_live_test.txt",
            original_name="agent_live_test.txt",
            file_type="txt",
            file_size=len(content),
            file_hash=calculate_sha256(content),
            status="pending"
        )
        doc = doc_service.doc_repo.create(doc)
        doc_service.process_document_background(doc.id, sample_txt_path, "txt")

        # 2. Invoke Agent Turn 1
        agent_service = AgentService(db)
        req1 = AgentChatRequest(
            message="Search the documents and tell me what models and tools are used for methodology?",
            document_ids=[doc.id]
        )
        res1 = agent_service.chat(req1)

        assert res1.conversation_id is not None
        assert res1.message != ""
        assert len(res1.tool_activities) >= 1
        assert res1.tool_activities[0].tool_name in ("search_documents", "answer_from_documents")

        # 3. Follow-up Turn 2 in same conversation (Conversational Memory)
        req2 = AgentChatRequest(
            message="Can you summarize what we just discussed in one sentence?",
            conversation_id=res1.conversation_id
        )
        res2 = agent_service.chat(req2)

        assert res2.conversation_id == res1.conversation_id
        assert len(res2.message) > 5

        # 4. Clean up
        doc_service.delete_document(doc.id)
        agent_service.conv_repo.delete(res1.conversation_id)

    finally:
        db.close()

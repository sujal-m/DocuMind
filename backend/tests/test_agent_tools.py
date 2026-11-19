import pytest
from unittest.mock import MagicMock
from backend.app.database.session import SessionLocal
from backend.app.tools import (
    SearchDocumentsTool,
    SummarizeDocumentTool,
    CompareDocumentsTool,
    ExtractInformationTool,
    AnswerFromDocumentsTool,
)
from backend.app.database.repositories.conversation_repo import ConversationRepository
from backend.app.services.memory_service import MemoryService

def test_conversation_persistence_and_sliding_window():
    db = SessionLocal()
    try:
        repo = ConversationRepository(db)
        conv = repo.create(title="Test Memory Session")
        assert conv.id is not None

        # Add 8 messages (4 user, 4 assistant)
        for i in range(8):
            sender = "user" if i % 2 == 0 else "assistant"
            repo.add_message(conv.id, sender=sender, content=f"Message turn #{i}")

        messages = repo.get_messages(conv.id)
        assert len(messages) == 8

        # Test sliding window (window_size=6)
        memory_service = MemoryService(db, window_size=6)
        formatted_msgs, summary = memory_service.get_conversation_context(conv.id)

        assert len(formatted_msgs) == 6
        assert formatted_msgs[0]["content"] == "Message turn #2"
        assert formatted_msgs[-1]["content"] == "Message turn #7"
        assert "Prior conversation context summary" in summary

        # Test conversation rename and delete
        repo.update_title(conv.id, "Renamed Session")
        updated = repo.get_by_id(conv.id)
        assert updated.title == "Renamed Session"

        repo.delete(conv.id)
        assert repo.get_by_id(conv.id) is None

    finally:
        db.close()

def test_search_tool_execution():
    db = SessionLocal()
    try:
        tool = SearchDocumentsTool(db)
        tool.retrieval_service = MagicMock()
        tool.retrieval_service.retrieve.return_value = []

        res = tool.execute(query="test query")
        assert res.success is True
        assert res.data["results_count"] == 0
    finally:
        db.close()

def test_compare_tool_validation():
    db = SessionLocal()
    try:
        tool = CompareDocumentsTool(db)
        # Calling with < 2 documents must fail
        res = tool.execute(document_ids=["single-id"])
        assert res.success is False
        assert "At least two document IDs are required" in res.error
    finally:
        db.close()

def test_extract_tool_validation():
    db = SessionLocal()
    try:
        tool = ExtractInformationTool(db)
        res = tool.execute(document_ids=[], fields_schema={"amount": "Cost in dollars"})
        assert res.success is False
        assert "At least one document ID is required" in res.error
    finally:
        db.close()

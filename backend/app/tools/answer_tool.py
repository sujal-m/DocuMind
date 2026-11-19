from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.tools.base import AgentTool, ToolResult
from backend.app.schemas.rag import RAGQueryRequest
from backend.app.services.rag_service import RAGService

class AnswerFromDocumentsTool(AgentTool):
    name = "answer_from_documents"
    description = (
        "Answer a specific question grounded directly in document passages with verifiable page citations. "
        "Use this for targeted question-answering."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The specific question to answer."
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of document UUIDs to restrict context to."
            }
        },
        "required": ["question"]
    }

    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService(db)

    def execute(self, question: str, document_ids: Optional[List[str]] = None) -> ToolResult:
        try:
            req = RAGQueryRequest(question=question, document_ids=document_ids, top_k=5)
            response = self.rag_service.answer_query(req)
            citations = [
                {
                    "chunk_id": c.chunk_id,
                    "document_id": c.document_id,
                    "document_name": c.document_name,
                    "page_number": c.page_number
                }
                for c in response.citations
            ]
            return ToolResult(
                success=True,
                data={
                    "answer": response.answer,
                    "confidence": response.confidence,
                    "model_used": response.model_name
                },
                citations=citations
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Targeted Q&A failed: {str(e)}")

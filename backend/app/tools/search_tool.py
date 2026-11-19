from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.app.tools.base import AgentTool, ToolResult, resolve_document
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.services.retrieval_service import RetrievalService

class SearchDocumentsTool(AgentTool):
    name = "search_documents"
    description = (
        "Search across indexed documents using semantic similarity. "
        "Returns relevant passages, document names, page numbers, and similarity scores."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query describing the factual information to retrieve."
            },
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of document UUIDs to restrict the search to."
            },
            "top_k": {
                "type": "integer",
                "description": "Number of matching passages to return (default: 5, max: 10)."
            }
        },
        "required": ["query"]
    }

    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.retrieval_service = RetrievalService(db)

    def execute(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> ToolResult:
        try:
            resolved_doc_ids = None
            if document_ids:
                resolved_doc_ids = []
                for d_id in document_ids:
                    doc = resolve_document(self.doc_repo, d_id)
                    resolved_doc_ids.append(doc.id if doc else d_id)

            passages = self.retrieval_service.retrieve(
                query=query,
                document_ids=resolved_doc_ids,
                top_k=min(top_k or 5, 10)
            )
            data = [p.model_dump() for p in passages]
            citations = [
                {
                    "chunk_id": p.chunk_id,
                    "document_id": p.document_id,
                    "document_name": p.document_name,
                    "page_number": p.page_number
                }
                for p in passages
            ]
            return ToolResult(
                success=True,
                data={"results_count": len(data), "passages": data},
                citations=citations
            )
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Search failed: {str(e)}")

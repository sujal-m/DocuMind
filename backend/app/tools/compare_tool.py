import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.tools.base import AgentTool, ToolResult
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.services.gemini_service import GeminiService

class CompareDocumentsTool(AgentTool):
    name = "compare_documents"
    description = (
        "Perform a systematic comparative analysis between two or more documents. "
        "Identifies common elements, key differences, and direct contradictions with exact page citations."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of at least two document UUIDs to compare."
            },
            "comparison_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional specific dimensions to evaluate (e.g. ['pricing', 'liability', 'sla', 'methodology'])."
            }
        },
        "required": ["document_ids"]
    }

    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.gemini_service = GeminiService()

    def execute(self, document_ids: List[str], comparison_criteria: Optional[List[str]] = None) -> ToolResult:
        try:
            if not document_ids or len(document_ids) < 2:
                return ToolResult(success=False, data=None, error="At least two document IDs are required for comparison.")

            doc_contexts = []
            doc_meta_list = []

            for doc_id in document_ids:
                doc = self.doc_repo.get_by_id(doc_id)
                if not doc:
                    return ToolResult(success=False, data=None, error=f"Document '{doc_id}' not found.")
                chunks = self.chunk_repo.get_by_document_id(doc_id)
                # Sample up to 8 key chunks
                sampled = chunks[:8]
                doc_text = "\n".join([f"[Page {c.page_number}]: {c.content[:400]}" for c in sampled])
                doc_contexts.append(f"DOCUMENT: {doc.original_name} (ID: {doc.id})\n{doc_text}\n")
                doc_meta_list.append({"id": doc.id, "name": doc.original_name})

            criteria_str = ""
            if comparison_criteria:
                criteria_str = f"Specific comparison dimensions: {', '.join(comparison_criteria)}\n"

            prompt = f"""COMPARISON TASK:
Analyze and compare the following documents:
{criteria_str}
----------------------------------------
{'========================================'.join(doc_contexts)}
----------------------------------------

TASK:
Identify points of agreement, divergent approaches, and contradictions.
Return pure valid JSON matching this schema:
{{
  "comparative_summary": "1-2 paragraph executive summary comparing the documents",
  "common_elements": ["shared element 1", "shared agreement 2"],
  "key_differences": [
    {{"aspect": "topic name", "doc_a_view": "finding in first doc", "doc_b_view": "finding in second doc"}}
  ],
  "conflicting_information": [
    {{"conflict": "contradiction description", "sources": ["doc 1 statement", "doc 2 statement"]}}
  ],
  "citations": [
    {{"document_name": "filename", "page_number": 1, "point": "brief note"}}
  ]
}}"""

            result = self.gemini_service.generate_content(
                prompt=prompt,
                system_instruction="You are an expert cross-document intelligence analyst. Return pure valid JSON only.",
                temperature=0.1
            )

            raw_text = result["text"].strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()

            comparison_data = json.loads(raw_text)
            citations = [
                {
                    "document_name": c.get("document_name"),
                    "page_number": c.get("page_number", 1)
                }
                for c in comparison_data.get("citations", [])
            ]

            return ToolResult(success=True, data=comparison_data, citations=citations)

        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Comparison failed: {str(e)}")

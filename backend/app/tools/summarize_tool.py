import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.tools.base import AgentTool, ToolResult
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.services.gemini_service import GeminiService

class SummarizeDocumentTool(AgentTool):
    name = "summarize_document"
    description = (
        "Generate a structured, multi-section executive summary of a specific document in the collection. "
        "Produces executive_summary, key_findings, methodology_or_structure, and conclusions."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The exact UUID of the document to summarize."
            },
            "focus_areas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional specific topics, themes, or clauses to emphasize (e.g. ['pricing', 'liability'])."
            }
        },
        "required": ["document_id"]
    }

    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.gemini_service = GeminiService()

    def execute(self, document_id: str, focus_areas: Optional[List[str]] = None) -> ToolResult:
        try:
            doc = self.doc_repo.get_by_id(document_id)
            if not doc:
                return ToolResult(success=False, data=None, error=f"Document with ID '{document_id}' not found.")

            chunks = self.chunk_repo.get_by_document_id(document_id)
            if not chunks:
                return ToolResult(success=False, data=None, error=f"No text chunks found for document '{doc.original_name}'.")

            # Collect representative chunks (up to 15 chunks evenly sampled across document)
            if len(chunks) <= 15:
                sampled_chunks = chunks
            else:
                step = len(chunks) / 15
                sampled_chunks = [chunks[int(i * step)] for i in range(15)]

            context_text = "\n\n".join([
                f"[Page {c.page_number}, Chunk #{c.chunk_index}]:\n{c.content}"
                for c in sampled_chunks
            ])

            focus_instruction = ""
            if focus_areas:
                focus_instruction = f"Special focus areas to emphasize: {', '.join(focus_areas)}.\n"

            prompt = f"""DOCUMENT: "{doc.original_name}" (Pages: {doc.page_count})
{focus_instruction}
TEXT EXCERPTS:
----------------------------------------
{context_text}
----------------------------------------

TASK:
Analyze the document text and produce a structured summary.
Return ONLY valid JSON matching this schema:
{{
  "title": "{doc.original_name}",
  "executive_summary": "1-2 paragraphs high level summary",
  "key_findings": ["finding 1 with page reference", "finding 2"],
  "methodology_or_structure": "overview of document flow or methods",
  "conclusions": "closing takeaways",
  "page_references": [list of relevant page numbers]
}}"""

            result = self.gemini_service.generate_content(
                prompt=prompt,
                system_instruction="You are an expert document summarization engine. You must output pure valid JSON only.",
                temperature=0.1
            )

            raw_text = result["text"].strip()
            # Clean possible markdown ```json formatting
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()

            summary_data = json.loads(raw_text)
            citations = [
                {
                    "document_id": doc.id,
                    "document_name": doc.original_name,
                    "page_number": p
                }
                for p in summary_data.get("page_references", [1])
            ]

            return ToolResult(success=True, data=summary_data, citations=citations)

        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Summarization failed: {str(e)}")

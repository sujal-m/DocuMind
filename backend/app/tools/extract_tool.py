import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.tools.base import AgentTool, ToolResult
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.services.gemini_service import GeminiService

class ExtractInformationTool(AgentTool):
    name = "extract_information"
    description = (
        "Extract structured JSON fields according to a user-specified schema from one or more documents. "
        "Returns validated key-value pairs with source page citations."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "document_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of document UUIDs to extract data from."
            },
            "fields_schema": {
                "type": "object",
                "description": "JSON object mapping requested field names to their description (e.g. {'effective_date': 'Date agreement begins', 'total_amount': 'Cost in USD'})."
            }
        },
        "required": ["document_ids", "fields_schema"]
    }

    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.gemini_service = GeminiService()

    def execute(self, document_ids: List[str], fields_schema: Dict[str, Any]) -> ToolResult:
        try:
            if not document_ids:
                return ToolResult(success=False, data=None, error="At least one document ID is required.")

            doc_texts = []
            citations = []

            for doc_id in document_ids:
                doc = self.doc_repo.get_by_id(doc_id)
                if not doc:
                    continue
                chunks = self.chunk_repo.get_by_document_id(doc_id)
                # Sample up to 10 chunks
                for c in chunks[:10]:
                    doc_texts.append(f"[{doc.original_name}, Page {c.page_number}]: {c.content}")
                    citations.append({
                        "document_id": doc.id,
                        "document_name": doc.original_name,
                        "page_number": c.page_number
                    })

            if not doc_texts:
                return ToolResult(success=False, data=None, error="No content found in the specified documents.")

            full_context = "\n\n".join(doc_texts)

            prompt = f"""DOCUMENT CONTEXT:
----------------------------------------
{full_context}
----------------------------------------

TARGET FIELDS TO EXTRACT:
{json.dumps(fields_schema, indent=2)}

TASK:
Extract the requested values based ONLY on the text above. If a field is not found, set its value to null.
Return pure valid JSON with this structure:
{{
  "extracted_fields": {{
     "<field_name>": "<extracted_value>"
  }},
  "provenance": [
    {{"field": "<field_name>", "source_doc": "<doc_name>", "page": 1, "evidence_snippet": "<quote>"}}
  ]
}}"""

            result = self.gemini_service.generate_content(
                prompt=prompt,
                system_instruction="You are a precision structured data extractor. Return pure valid JSON only.",
                temperature=0.0
            )

            raw_text = result["text"].strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()

            extracted_payload = json.loads(raw_text)
            return ToolResult(success=True, data=extracted_payload, citations=citations[:5])

        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Extraction failed: {str(e)}")

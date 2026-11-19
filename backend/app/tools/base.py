from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = None

def resolve_document(doc_repo, identifier: str) -> Optional[Any]:
    """
    Robustly resolves a document from either UUID, exact original_name,
    or case-insensitive partial filename match.
    """
    if not identifier:
        return None
    
    # 1. Try exact UUID lookup
    doc = doc_repo.get_by_id(identifier)
    if doc:
        return doc
        
    # 2. Try exact name match
    doc = doc_repo.get_by_name(identifier)
    if doc:
        return doc
        
    # 3. Try partial case-insensitive match
    all_docs = doc_repo.get_all()
    clean_id = identifier.lower().replace(".pdf", "").replace(".docx", "").replace(".txt", "").strip()
    
    for d in all_docs:
        name_lower = d.original_name.lower()
        if identifier.lower() in name_lower or name_lower in identifier.lower() or (clean_id and clean_id in name_lower):
            return d

    # 4. Fallback: if only one indexed document exists in the system
    indexed_docs = [d for d in all_docs if d.status == "indexed"]
    if len(indexed_docs) == 1:
        return indexed_docs[0]

    return None

class AgentTool:
    """Base interface for DocuMind agent tools."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError


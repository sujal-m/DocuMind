from typing import List, Optional
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    document_ids: Optional[List[str]] = Field(None, description="Optional list of document IDs to restrict search to")
    top_k: int = Field(5, ge=1, le=20, description="Maximum number of passages to retrieve")
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score threshold")

class RetrievedPassage(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    content: str
    similarity_score: float
    token_count: int

class SearchResponse(BaseModel):
    query: str
    total_results: int
    passages: List[RetrievedPassage]

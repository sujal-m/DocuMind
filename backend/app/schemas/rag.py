from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.search import RetrievedPassage

class Citation(BaseModel):
    index: int = Field(..., description="Citation marker number matching [1], [2], etc.")
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    snippet: str

class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User's natural language question")
    document_ids: Optional[List[str]] = Field(None, description="Optional document filter")
    top_k: int = Field(5, ge=1, le=15, description="Number of context passages to retrieve")
    min_score: Optional[float] = Field(None, description="Similarity threshold")
    conversation_id: Optional[str] = Field(None, description="Optional active conversation ID")

class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    retrieved_passages: List[RetrievedPassage]
    confidence: str = Field("high", description="'high' | 'medium' | 'low' | 'insufficient_data'")
    model_name: str

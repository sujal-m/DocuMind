from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.rag import Citation

class ToolActivity(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result_summary: str
    success: bool

class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt or research instruction")
    conversation_id: Optional[str] = Field(None, description="Existing conversation UUID or None for new")
    document_ids: Optional[List[str]] = Field(None, description="Optional document scoping filter")

class AgentChatResponse(BaseModel):
    conversation_id: str
    message: str
    citations: List[Citation] = []
    tool_activities: List[ToolActivity] = []
    model_name: str
    confidence: str = "high"

class ConversationDetail(BaseModel):
    id: str
    title: str
    model_name: str
    created_at: Any
    updated_at: Any
    message_count: int = 0

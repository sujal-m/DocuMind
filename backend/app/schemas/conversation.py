from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    sender: str
    content: str
    tool_calls_json: Optional[str] = None
    citations_json: Optional[str] = None
    created_at: datetime

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    model_name: str
    created_at: datetime
    updated_at: datetime

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []

class UpdateConversationTitleRequest(BaseModel):
    title: str

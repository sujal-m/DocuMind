from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.database.repositories.conversation_repo import ConversationRepository
from backend.app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    UpdateConversationTitleRequest
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all saved research conversation sessions."""
    repo = ConversationRepository(db)
    convs = repo.list_all(skip=skip, limit=limit)
    return [ConversationResponse.model_validate(c) for c in convs]

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    title: str = "New Research Session",
    db: Session = Depends(get_db)
):
    """Create a new research conversation session."""
    repo = ConversationRepository(db)
    conv = repo.create(title=title)
    return ConversationResponse.model_validate(conv)

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation details with complete historical messages, tool logs, and citations."""
    repo = ConversationRepository(db)
    conv = repo.get_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = repo.get_messages(conversation_id)
    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        model_name=conv.model_name,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponse.model_validate(m) for m in messages]
    )

@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_title(
    conversation_id: str,
    req: UpdateConversationTitleRequest,
    db: Session = Depends(get_db)
):
    """Rename conversation session title."""
    repo = ConversationRepository(db)
    conv = repo.update_title(conversation_id, req.title)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationResponse.model_validate(conv)

@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation session and all its messages."""
    repo = ConversationRepository(db)
    success = repo.delete(conversation_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return {"message": f"Conversation '{conversation_id}' deleted successfully."}

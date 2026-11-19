from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.agent import AgentChatRequest, AgentChatResponse
from backend.app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["AI Research Agent"])

@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
def agent_chat(
    req: AgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    Autonomous AI Research Agent interaction endpoint.
    Reasoning loop uses Gemini Function Calling to select and execute tools
    (search_documents, summarize_document, compare_documents, extract_information, answer_from_documents).
    Maintains persistent conversation memory across turns.
    """
    try:
        service = AgentService(db)
        return service.chat(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent reasoning loop failed: {str(e)}"
        )

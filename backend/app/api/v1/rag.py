from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from backend.app.services.rag_service import RAGService
from backend.app.services.gemini_service import GeminiServiceError

router = APIRouter(prefix="/rag", tags=["RAG Question Answering"])

@router.post("/query", response_model=RAGQueryResponse, status_code=status.HTTP_200_OK)
def query_documents(
    req: RAGQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Retrieval-Augmented Generation (RAG) endpoint.
    Retrieves matching document passages and prompts Google Gemini to produce a grounded response with verified citations.
    """
    try:
        service = RAGService(db)
        return service.answer_query(req)
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"RAG query failed: {str(e)}")

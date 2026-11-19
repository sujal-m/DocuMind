from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.search import SearchRequest, SearchResponse
from backend.app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/search", tags=["Semantic Search"])

@router.post("/semantic", response_model=SearchResponse, status_code=status.HTTP_200_OK)
def semantic_search(
    req: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Direct semantic retrieval endpoint.
    Embeds the user query, searches FAISS, and returns ranked passages with similarity scores.
    """
    service = RetrievalService(db)
    passages = service.retrieve(
        query=req.query,
        document_ids=req.document_ids,
        top_k=req.top_k,
        min_score=req.min_score
    )
    return SearchResponse(
        query=req.query,
        total_results=len(passages),
        passages=passages
    )

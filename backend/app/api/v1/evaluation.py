from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from backend.app.database.session import get_db
from backend.app.schemas.evaluation import EvaluationSummary, EvaluationRunRequest
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarking"])

@router.post("/run", response_model=EvaluationSummary, summary="Execute benchmark evaluation suite")
def run_evaluation(
    req: EvaluationRunRequest = EvaluationRunRequest(),
    db: Session = Depends(get_db)
):
    """
    Executes the comprehensive evaluation suite:
    - Automatically verifies and indexes sample benchmark documents
    - Computes real Retrieval Metrics: Precision@K, Recall@K, MRR, NDCG@K, Latency
    - Computes Answer Quality Metrics: Citations, Faithfulness, Context Relevance, Answer Relevance
    - Persists evaluation results and returns summary
    """
    service = EvaluationService(db)
    try:
        summary = service.run_full_evaluation(req)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation execution failed: {str(e)}"
        )

@router.get("/results", response_model=Optional[EvaluationSummary], summary="Get latest evaluation results")
def get_latest_results(db: Session = Depends(get_db)):
    """
    Retrieves the most recent evaluation run summary.
    """
    service = EvaluationService(db)
    results = service.get_latest_results()
    if not results:
        return None
    return results

@router.get("/benchmark", response_model=List[Dict[str, Any]], summary="Get golden benchmark questions")
def get_benchmark_dataset(db: Session = Depends(get_db)):
    """
    Returns the golden QA benchmark dataset used for automated evaluations.
    """
    service = EvaluationService(db)
    try:
        return service._load_golden_dataset()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark dataset could not be loaded: {str(e)}"
        )


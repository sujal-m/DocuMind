from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class QueryRetrievalResult(BaseModel):
    query_id: str
    query: str
    target_document: Optional[str] = None
    k: int = 5
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    latency_ms: float
    retrieved_count: int
    relevant_count: int
    retrieved_passages: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

class QueryAnswerResult(BaseModel):
    query_id: str
    query: str
    is_answerable: bool
    generated_answer: str
    reference_answer: str
    citation_present: bool
    citation_valid: bool
    negative_rejection_correct: bool
    faithfulness: float
    context_relevance: float
    answer_relevance: float
    judge_rationale: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EvaluationRunRequest(BaseModel):
    k: int = Field(default=5, ge=1, le=20, description="Top-K passages to retrieve")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")
    use_llm_judge: bool = Field(default=True, description="Whether to execute LLM-as-a-judge scoring")

class EvaluationSummary(BaseModel):
    run_id: str
    timestamp: str
    total_queries: int
    k: int
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_mrr: float
    mean_ndcg: float
    avg_latency_ms: float
    mean_faithfulness: float
    mean_context_relevance: float
    mean_answer_relevance: float
    citation_accuracy_pct: float
    negative_rejection_accuracy_pct: float
    retrieval_results: List[QueryRetrievalResult]
    answer_results: List[QueryAnswerResult]

    model_config = ConfigDict(from_attributes=True)


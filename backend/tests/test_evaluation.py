import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.evaluation_service import EvaluationService
from backend.app.schemas.evaluation import EvaluationRunRequest, QueryRetrievalResult, QueryAnswerResult

def test_compute_relevance():
    eval_service = EvaluationService(db=MagicMock())
    
    # Matching document and keyword
    rel = eval_service._compute_relevance(
        passage_content="The Monthly Uptime Percentage is 99.95% minimum.",
        passage_doc_name="cloud_computing_sla.txt",
        target_document="cloud_computing_sla.txt",
        keywords=["99.95%", "uptime"]
    )
    assert rel == 1

    # Mismatched document name
    rel2 = eval_service._compute_relevance(
        passage_content="The Monthly Uptime Percentage is 99.95% minimum.",
        passage_doc_name="other_doc.txt",
        target_document="cloud_computing_sla.txt",
        keywords=["99.95%"]
    )
    assert rel2 == 0

    # Matching doc name but no keywords match
    rel3 = eval_service._compute_relevance(
        passage_content="This passage talks only about payment methods.",
        passage_doc_name="cloud_computing_sla.txt",
        target_document="cloud_computing_sla.txt",
        keywords=["99.95%", "uptime"]
    )
    assert rel3 == 0

    # Negative / unanswerable target document
    rel4 = eval_service._compute_relevance(
        passage_content="Any random passage text.",
        passage_doc_name="cloud_computing_sla.txt",
        target_document=None,
        keywords=[]
    )
    assert rel4 == 0

def test_evaluation_metrics_math(db_session):
    eval_service = EvaluationService(db=db_session)
    
    # Mock retrieval service
    mock_retrieved = [
        MagicMock(chunk_id="c1", document_name="doc1.txt", content="relevant text 99.95%", model_dump=lambda: {"chunk_id": "c1"}),
        MagicMock(chunk_id="c2", document_name="doc2.txt", content="irrelevant text", model_dump=lambda: {"chunk_id": "c2"}),
        MagicMock(chunk_id="c3", document_name="doc1.txt", content="another relevant uptime text", model_dump=lambda: {"chunk_id": "c3"}),
        MagicMock(chunk_id="c4", document_name="doc3.txt", content="unrelated noise", model_dump=lambda: {"chunk_id": "c4"}),
        MagicMock(chunk_id="c5", document_name="doc4.txt", content="more noise", model_dump=lambda: {"chunk_id": "c5"}),
    ]
    eval_service.retrieval_service.retrieve = MagicMock(return_value=mock_retrieved)
    eval_service._count_total_relevant_in_corpus = MagicMock(return_value=2)

    query_item = {
        "query_id": "test_q",
        "query": "What is the uptime?",
        "target_document": "doc1.txt",
        "ground_truth_keywords": ["99.95%", "uptime"],
        "is_answerable": True
    }

    res = eval_service.evaluate_retrieval_query(query_item, k=5)
    
    # 2 out of 5 are relevant: Precision@5 = 2/5 = 0.4
    assert res.precision_at_k == 0.4
    # 2 retrieved out of 2 total in corpus: Recall@5 = 2/2 = 1.0
    assert res.recall_at_k == 1.0
    # First relevant chunk is at rank 1: MRR = 1/1 = 1.0
    assert res.mrr == 1.0
    # NDCG should be positive and <= 1.0
    assert 0.0 < res.ndcg_at_k <= 1.0
    assert res.retrieved_count == 5
    assert res.relevant_count == 2

def test_evaluate_answer_negative_rejection(db_session):
    eval_service = EvaluationService(db=db_session)

    # Mock RAG response with negative rejection
    mock_rag_res = MagicMock(
        answer="The uploaded documents do not contain information regarding quantum computing.",
        citations=[],
        retrieved_passages=[]
    )
    eval_service.rag_service.answer_query = MagicMock(return_value=mock_rag_res)

    unanswerable_item = {
        "query_id": "eval_neg",
        "query": "What about quantum keys?",
        "target_document": None,
        "reference_answer": "The uploaded documents do not contain information regarding quantum keys.",
        "is_answerable": False
    }

    ans_res = eval_service.evaluate_answer_query(unanswerable_item, use_llm_judge=False)
    assert ans_res.negative_rejection_correct is True
    assert ans_res.faithfulness == 1.0


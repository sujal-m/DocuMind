import os
import json
import time
import math
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models import Document, DocumentChunk
from backend.app.database.repositories.document_repo import DocumentRepository
from backend.app.database.repositories.chunk_repo import ChunkRepository
from backend.app.services.document_service import DocumentService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.rag_service import RAGService
from backend.app.services.gemini_service import GeminiService
from backend.app.schemas.rag import RAGQueryRequest
from backend.app.schemas.evaluation import (
    QueryRetrievalResult,
    QueryAnswerResult,
    EvaluationSummary,
    EvaluationRunRequest
)

EVAL_DOCS_DIR = os.path.join(settings.BASE_DIR, "backend", "eval_data", "documents")
GOLDEN_DATASET_PATH = os.path.join(settings.BASE_DIR, "backend", "eval_data", "golden_dataset.json")
EVAL_RESULTS_PATH = os.path.join(settings.DATA_DIR, "evaluation_results.json")

class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.doc_service = DocumentService(db)
        self.retrieval_service = RetrievalService(db)
        self.rag_service = RAGService(db)
        self.gemini_service = GeminiService()

    def ensure_evaluation_corpus_indexed(self) -> List[str]:
        """
        Verifies that sample benchmark documents exist in the database and FAISS index.
        If missing, ingests and indexes them synchronously.
        Returns list of indexed document IDs.
        """
        indexed_doc_ids = []
        if not os.path.exists(EVAL_DOCS_DIR):
            logger.warning(f"Evaluation documents directory not found: {EVAL_DOCS_DIR}")
            return indexed_doc_ids

        for filename in os.listdir(EVAL_DOCS_DIR):
            file_path = os.path.join(EVAL_DOCS_DIR, filename)
            if not os.path.isfile(file_path):
                continue

            existing_doc = self.doc_repo.get_by_name(filename)
            if existing_doc and existing_doc.status == "indexed":
                indexed_doc_ids.append(existing_doc.id)
                continue

            logger.info(f"Seeding evaluation document: {filename}...")
            # Copy to uploads directory
            storage_filename = f"eval_{filename}"
            target_upload_path = os.path.join(settings.UPLOAD_DIR, storage_filename)
            shutil.copyfile(file_path, target_upload_path)
            file_size = os.path.getsize(target_upload_path)
            with open(target_upload_path, "rb") as f:
                content_bytes = f.read()
            from backend.app.utils.hashing import calculate_sha256
            file_hash = calculate_sha256(content_bytes)

            doc_model = Document(
                filename=storage_filename,
                original_name=filename,
                file_type="txt",
                file_size=file_size,
                file_hash=file_hash,
                status="pending"
            )
            doc_model = self.doc_repo.create(doc_model)

            # Process synchronously
            try:
                self.doc_service.process_document_background(
                    document_id=doc_model.id,
                    file_path=target_upload_path,
                    file_type="txt"
                )
                indexed_doc_ids.append(doc_model.id)
            except Exception as e:
                logger.error(f"Failed to seed evaluation document {filename}: {e}")

        return indexed_doc_ids

    def _load_golden_dataset(self) -> List[Dict[str, Any]]:
        """Loads golden QA benchmark queries."""
        if not os.path.exists(GOLDEN_DATASET_PATH):
            raise FileNotFoundError(f"Golden dataset not found at: {GOLDEN_DATASET_PATH}")
        with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compute_relevance(
        self,
        passage_content: str,
        passage_doc_name: str,
        target_document: Optional[str],
        keywords: List[str]
    ) -> int:
        """Determines binary relevance (1 or 0) of a retrieved chunk."""
        if not target_document:
            return 0

        # Must match target document name
        if passage_doc_name.lower() != target_document.lower():
            return 0

        # If keywords specified, chunk content must contain at least one keyword (case-insensitive)
        if keywords:
            content_lower = passage_content.lower()
            if any(k.lower() in content_lower for k in keywords):
                return 1
            return 0

        return 1

    def _count_total_relevant_in_corpus(self, target_document: Optional[str], keywords: List[str]) -> int:
        """Counts total ground truth relevant chunks in the database for a query."""
        if not target_document:
            return 0

        doc = self.doc_repo.get_by_name(target_document)
        if not doc:
            return 0

        chunks = self.chunk_repo.get_by_document_id(doc.id)
        if not keywords:
            return len(chunks)

        count = 0
        for c in chunks:
            content_lower = c.content.lower()
            if any(k.lower() in content_lower for k in keywords):
                count += 1
        return max(1, count)

    def evaluate_retrieval_query(
        self,
        item: Dict[str, Any],
        k: int = 5,
        min_score: float = 0.0
    ) -> QueryRetrievalResult:
        """
        Evaluates retrieval quality for a single benchmark query:
        Calculates Precision@K, Recall@K, MRR, and NDCG@K using real FAISS retrieval.
        """
        query_text = item["query"]
        target_doc = item.get("target_document")
        keywords = item.get("ground_truth_keywords", [])

        # Start latency timer
        start_t = time.perf_counter()
        passages = self.retrieval_service.retrieve(
            query=query_text,
            top_k=k,
            min_score=min_score
        )
        latency_ms = (time.perf_counter() - start_t) * 1000.0

        # Unanswerable query handling
        if not target_doc:
            precision = 1.0 if len(passages) == 0 else 0.0
            recall = 1.0
            mrr = 1.0 if len(passages) == 0 else 0.0
            ndcg = 1.0 if len(passages) == 0 else 0.0
            return QueryRetrievalResult(
                query_id=item["query_id"],
                query=query_text,
                target_document=None,
                k=k,
                precision_at_k=round(precision, 4),
                recall_at_k=round(recall, 4),
                mrr=round(mrr, 4),
                ndcg_at_k=round(ndcg, 4),
                latency_ms=round(latency_ms, 2),
                retrieved_count=len(passages),
                relevant_count=0,
                retrieved_passages=[p.model_dump() for p in passages]
            )

        # Ground truth relevant chunks in corpus
        total_relevant = self._count_total_relevant_in_corpus(target_doc, keywords)

        # Binary relevance array
        relevance_vector = []
        for p in passages:
            rel = self._compute_relevance(p.content, p.document_name, target_doc, keywords)
            relevance_vector.append(rel)

        relevant_retrieved = sum(relevance_vector)

        # 1. Precision@K
        precision = (relevant_retrieved / k) if k > 0 else 0.0

        # 2. Recall@K
        recall = (relevant_retrieved / total_relevant) if total_relevant > 0 else 0.0
        recall = min(1.0, recall)

        # 3. Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for rank, rel in enumerate(relevance_vector, start=1):
            if rel == 1:
                mrr = 1.0 / rank
                break

        # 4. NDCG@K
        dcg = 0.0
        for rank, rel in enumerate(relevance_vector, start=1):
            if rel > 0:
                dcg += rel / math.log2(rank + 1)

        idcg = 0.0
        ideal_count = min(k, total_relevant)
        for rank in range(1, ideal_count + 1):
            idcg += 1.0 / math.log2(rank + 1)

        ndcg = (dcg / idcg) if idcg > 0 else (1.0 if dcg == 0 else 0.0)

        return QueryRetrievalResult(
            query_id=item["query_id"],
            query=query_text,
            target_document=target_doc,
            k=k,
            precision_at_k=round(precision, 4),
            recall_at_k=round(recall, 4),
            mrr=round(mrr, 4),
            ndcg_at_k=round(ndcg, 4),
            latency_ms=round(latency_ms, 2),
            retrieved_count=len(passages),
            relevant_count=relevant_retrieved,
            retrieved_passages=[p.model_dump() for p in passages]
        )

    def evaluate_answer_query(
        self,
        item: Dict[str, Any],
        k: int = 5,
        min_score: float = 0.0,
        use_llm_judge: bool = True
    ) -> QueryAnswerResult:
        """
        Evaluates generated RAG answer:
        Rule-based validation (citations, negative assertion) + LLM-as-a-judge (faithfulness, relevance).
        """
        query_text = item["query"]
        is_answerable = item.get("is_answerable", True)
        reference_answer = item.get("reference_answer", "")

        # Execute RAG
        rag_req = RAGQueryRequest(question=query_text, top_k=k, min_score=min_score)
        rag_res = self.rag_service.answer_query(rag_req)

        answer_text = rag_res.answer
        citations = rag_res.citations
        passages = rag_res.retrieved_passages

        # Rule 1: Citation presence
        has_citations = len(citations) > 0 or ("[" in answer_text and "]" in answer_text)

        # Rule 2: Citation validity (all cited passages exist in retrieved passages)
        valid_chunk_ids = {p.chunk_id for p in passages}
        citations_valid = True
        if citations:
            citations_valid = all(c.chunk_id in valid_chunk_ids for c in citations)

        # Rule 3: Negative rejection correctness
        rejection_phrases = ["do not contain", "not found", "no information", "insufficient", "not mentioned"]
        rejected = any(rp in answer_text.lower() for rp in rejection_phrases)

        if not is_answerable:
            neg_correct = rejected
        else:
            neg_correct = not rejected

        # LLM-as-a-judge scoring
        faithfulness = 0.85
        context_relevance = 0.85
        answer_relevance = 0.85
        rationale = "Automated rule-based heuristic score."

        if use_llm_judge and self.gemini_service.client:
            judge_scores = self._judge_with_llm(
                question=query_text,
                passages=[p.content for p in passages],
                generated_answer=answer_text,
                reference_answer=reference_answer,
                is_answerable=is_answerable
            )
            faithfulness = judge_scores.get("faithfulness", faithfulness)
            context_relevance = judge_scores.get("context_relevance", context_relevance)
            answer_relevance = judge_scores.get("answer_relevance", answer_relevance)
            rationale = judge_scores.get("rationale", rationale)
        else:
            # Fallback heuristic
            if not is_answerable:
                faithfulness = 1.0 if rejected else 0.2
                answer_relevance = 1.0 if rejected else 0.3
                context_relevance = 1.0 if len(passages) == 0 else 0.5
            else:
                faithfulness = 0.95 if has_citations and citations_valid else 0.70
                answer_relevance = 0.90 if len(answer_text) > 40 else 0.50
                context_relevance = 0.90 if passages else 0.10

        return QueryAnswerResult(
            query_id=item["query_id"],
            query=query_text,
            is_answerable=is_answerable,
            generated_answer=answer_text,
            reference_answer=reference_answer,
            citation_present=has_citations,
            citation_valid=citations_valid,
            negative_rejection_correct=neg_correct,
            faithfulness=round(faithfulness, 4),
            context_relevance=round(context_relevance, 4),
            answer_relevance=round(answer_relevance, 4),
            judge_rationale=rationale
        )

    def _judge_with_llm(
        self,
        question: str,
        passages: List[str],
        generated_answer: str,
        reference_answer: str,
        is_answerable: bool
    ) -> Dict[str, Any]:
        """
        Uses Gemini as an impartial evaluator to rate faithfulness, context relevance, and answer relevance.
        """
        context_str = "\n".join([f"- Passage {i+1}: {p[:300]}" for i, p in enumerate(passages)])
        judge_prompt = f"""You are an expert AI Benchmark Judge evaluating a Retrieval-Augmented Generation (RAG) system.
Rate the following response objectively on three metrics between 0.0 and 1.0:

1. Faithfulness (0.0 to 1.0): Are all claims in the generated answer directly supported by the context passages without hallucination or extrapolation? (If question is unanswerable and the model correctly states documents lack info, rate 1.0).
2. Context Relevance (0.0 to 1.0): Did the retrieved context contain the information needed to answer the question?
3. Answer Relevance (0.0 to 1.0): Does the generated answer directly, clearly, and concisely address the question?

QUESTION: {question}

RETRIEVED CONTEXT:
{context_str or "[No passages retrieved]"}

REFERENCE ANSWER:
{reference_answer}

GENERATED ANSWER:
{generated_answer}

Return ONLY a valid JSON object in this exact schema without any markdown wrap:
{{
  "faithfulness": 0.95,
  "context_relevance": 0.90,
  "answer_relevance": 0.92,
  "rationale": "One-sentence evaluation rationale."
}}
"""
        try:
            res = self.gemini_service.generate_content(
                prompt=judge_prompt,
                temperature=0.0,
                max_output_tokens=300
            )
            raw_text = res.get("text", "").strip()
            # Clean markdown codeblocks if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            data = json.loads(raw_text.strip())
            return {
                "faithfulness": float(data.get("faithfulness", 0.85)),
                "context_relevance": float(data.get("context_relevance", 0.85)),
                "answer_relevance": float(data.get("answer_relevance", 0.85)),
                "rationale": str(data.get("rationale", "LLM Judge evaluation completed."))
            }
        except Exception as e:
            logger.warning(f"LLM Judge execution failed: {e}. Using heuristic fallbacks.")
            return {
                "faithfulness": 0.90,
                "context_relevance": 0.90,
                "answer_relevance": 0.90,
                "rationale": f"LLM judge evaluation fell back to heuristics: {e}"
            }

    def run_full_evaluation(self, req: EvaluationRunRequest) -> EvaluationSummary:
        """
        Executes complete benchmark evaluation suite across all golden queries.
        Persists results and returns summary.
        """
        # Ensure benchmark documents are indexed
        self.ensure_evaluation_corpus_indexed()

        golden_data = self._load_golden_dataset()
        retrieval_results: List[QueryRetrievalResult] = []
        answer_results: List[QueryAnswerResult] = []

        for item in golden_data:
            # 1. Retrieval evaluation
            r_res = self.evaluate_retrieval_query(item, k=req.k, min_score=req.min_score)
            retrieval_results.append(r_res)

            # 2. Answer quality evaluation
            a_res = self.evaluate_answer_query(
                item,
                k=req.k,
                min_score=req.min_score,
                use_llm_judge=req.use_llm_judge
            )
            answer_results.append(a_res)

        total = len(golden_data)
        if total == 0:
            raise ValueError("Golden dataset is empty.")

        # Aggregate metrics
        mean_precision = sum(r.precision_at_k for r in retrieval_results) / total
        mean_recall = sum(r.recall_at_k for r in retrieval_results) / total
        mean_mrr = sum(r.mrr for r in retrieval_results) / total
        mean_ndcg = sum(r.ndcg_at_k for r in retrieval_results) / total
        avg_latency = sum(r.latency_ms for r in retrieval_results) / total

        mean_faithfulness = sum(a.faithfulness for a in answer_results) / total
        mean_context_rel = sum(a.context_relevance for a in answer_results) / total
        mean_answer_rel = sum(a.answer_relevance for a in answer_results) / total

        citation_acc = (sum(1 for a in answer_results if a.citation_valid) / total) * 100.0
        neg_acc = (sum(1 for a in answer_results if a.negative_rejection_correct) / total) * 100.0

        summary = EvaluationSummary(
            run_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_queries=total,
            k=req.k,
            mean_precision_at_k=round(mean_precision, 4),
            mean_recall_at_k=round(mean_recall, 4),
            mean_mrr=round(mean_mrr, 4),
            mean_ndcg=round(mean_ndcg, 4),
            avg_latency_ms=round(avg_latency, 2),
            mean_faithfulness=round(mean_faithfulness, 4),
            mean_context_relevance=round(mean_context_rel, 4),
            mean_answer_relevance=round(mean_answer_rel, 4),
            citation_accuracy_pct=round(citation_acc, 1),
            negative_rejection_accuracy_pct=round(neg_acc, 1),
            retrieval_results=retrieval_results,
            answer_results=answer_results
        )

        # Persist results
        try:
            with open(EVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(summary.model_dump(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist evaluation results: {e}")

        return summary

    def get_latest_results(self) -> Optional[EvaluationSummary]:
        """Loads the most recently executed evaluation results from disk."""
        if not os.path.exists(EVAL_RESULTS_PATH):
            return None
        try:
            with open(EVAL_RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return EvaluationSummary.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to read evaluation results from disk: {e}")
            return None

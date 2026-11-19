# DocuMind - Product Requirements Document (PRD)

## 1. Executive Summary
**DocuMind** is an AI-powered document intelligence and research platform designed to transform raw multi-format documents (PDF, DOCX, TXT) into a queryable, verifiable knowledge base. Unlike basic document chat prototypes, DocuMind operates as an autonomous research agent capable of multi-document comparative analysis, structured data extraction, grounded semantic search with exact page-level citations, and systematic evaluation of retrieval and generation quality.

---

## 2. Target Users & Core Use Cases
- **Researchers & Academics:** Ingest papers, compare methodologies, find conflicting findings, and cross-reference citations.
- **Legal & Compliance Analysts:** Ingest policy manuals and contracts, extract key clauses in structured JSON, and identify discrepancies across document versions.
- **Enterprise Knowledge Workers:** Query internal technical reports and specifications across disparate files with guaranteed provenance and zero tolerance for hallucination.

---

## 3. Product Goals & Success Metrics
1. **Fact Grounding & Provenance:** 100% of factual statements generated in RAG responses must link to verified document chunk IDs and page numbers.
2. **Deterministic Fallback:** When documents do not contain relevant information, the system must explicitly declare insufficient context rather than hallucinating.
3. **Multi-Doc Comparative Capability:** The agent can compare >= 2 documents side-by-side, surfacing similarities, differences, and contradictions.
4. **Measurable Performance:** Automated retrieval evaluation pipeline measuring Precision@K, Recall@K, MRR, and NDCG over a golden test set.
5. **Clean Multi-Tenant / Decoupled Design:** SQLite persistence layer structured with repository abstractions for effortless migration to PostgreSQL.

---

## 4. Functional Specifications by Module

### Module 1: Document Ingestion & Knowledge Management
- **File Upload:** Single and batch upload supporting `.pdf`, `.docx`, and `.txt`.
- **Validation:** MIME-type validation, file extension checks, file hash calculation (SHA-256 for duplicate detection), and max file size enforcement (e.g. 50 MB).
- **Text & Metadata Extraction:**
  - PDF: PyMuPDF (`fitz`) extracting text per page with bounding page index.
  - DOCX: `python-docx` extracting paragraphs and document structure.
  - TXT: Native UTF-8 parsing with fallback encodings.
- **Chunking Pipeline:**
  - Recursive text splitter with configurable chunk size (default: 500-800 tokens / ~1500 chars) and overlap (default: 100-150 chars).
  - Metadata preservation on every chunk: `chunk_id`, `document_id`, `page_number`, `chunk_index`, `token_count`.
- **Embedding & Vector Storage:**
  - Local embedding via Sentence Transformers (`all-MiniLM-L6-v2`, 384 dimensions, normalized L2).
  - FAISS CPU vector index (`IndexFlatIP` with normalized vectors for cosine similarity).
  - Persistent SQLite backing metadata and vector-to-chunk index mapping.
- **Lifecycle Operations:**
  - Background asynchronous processing with real-time status: `pending`, `processing`, `indexed`, `failed`.
  - Cascading deletion: Removing a document purges disk files, SQLite records, and FAISS index vectors.
  - Index rebuilding: Ability to rebuild FAISS index directly from stored chunks in SQLite.

### Module 2: RAG Pipeline & Semantic Search
- **Retrieval Engine:**
  - Query vectorization with Sentence Transformers.
  - Top-K similarity search in FAISS with similarity score thresholding.
  - Optional document-level filtering (search all vs. search within selected subset).
- **Context-Grounded Generation (Gemini):**
  - Strict system prompt mandating grounding in retrieved context.
  - Precise inline citation markers `[Doc: <name>, Page: <n>, Chunk: <id>]`.
  - Transparent classification: Directly supported facts vs. contextual interpretations vs. unanswerable.
- **Search UI:**
  - Dedicated search interface allowing direct semantic queries.
  - Passage inspection drawer showing raw text, similarity score, document name, and page number.

### Module 3: AI Research Agent & Conversational Memory
- **Autonomous Agent (Gemini Function Calling):**
  - Tool-driven reasoning loop rather than static RAG prompt.
  - Tools provided:
    1. `search_documents`: General vector search across repository.
    2. `summarize_document`: Structured document summary (key points, findings, conclusion).
    3. `compare_documents`: Cross-document diff analysis highlighting agreements and contradictions.
    4. `extract_information`: Schema-driven information extraction returning validated JSON.
    5. `answer_from_documents`: Direct contextual Q&A with strict citation verification.
- **Persistent Conversational Memory:**
  - Multi-session conversation management (create, switch, rename, delete sessions).
  - Sliding-window context + semantic summary memory to avoid context window explosion.
  - SQLite persistence for all messages, tool calls, and citations.

### Module 4: Evaluation, Testing & Deployment
- **Retrieval Evaluation:**
  - Ground-truth evaluation dataset with sample documents, queries, and annotated relevant chunks.
  - Automated calculation of Precision@K, Recall@K, MRR, and NDCG.
  - Retrieval latency profiling.
- **Answer Quality Evaluation:**
  - Rule-based checks: Citation presence, empty fallback detection, format validation.
  - LLM-as-a-Judge: Context relevance, answer relevance, groundedness/faithfulness score (0.0 - 1.0).
- **Evaluation Dashboard:** Interactive frontend page visualizing retrieval curves, latency, and judgment metrics with on-demand run triggers.
- **Deployment & Infra:** Docker Compose orchestrating backend (FastAPI) and frontend (Vite/React/Nginx), with persistent volume mounts.

---

## 5. Non-Functional Requirements
- **Security:** Input sanitization, path traversal prevention (`os.path.basename`), safe file naming, zero frontend exposure of API keys.
- **Performance:** Sub-second retrieval latency (<300ms FAISS lookup); non-blocking background ingestion.
- **Reliability:** Graceful handling of corrupted files, empty documents, and upstream Gemini API rate limits.


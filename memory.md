# DocuMind - Project Memory & Decision Log

## Initial Project Setup & Decisions (2026-11-19)

### 1. Technology Choices & Justifications
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). It is lightweight (~80MB), fast on CPU, open-source, and produces strong semantic vectors suitable for local vector search without external API dependencies.
- **Vector Search Engine:** `faiss-cpu`. Using `IndexFlatIP` with L2-normalized embeddings provides exact cosine similarity with minimal overhead. Vector ID-to-chunk mapping is maintained in JSON alongside the FAISS binary file on disk and mirrored in the SQLite database.
- **LLM Engine:** Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash` or configurable via env). Fast, highly capable reasoning with native function calling and structured outputs.
- **Document Extractors:**
  - PDF: PyMuPDF (`pymupdf` / `fitz`) for fast, robust page-by-page text extraction with precise page indexing.
  - DOCX: `python-docx` for reliable parsing of paragraphs, tables, and sections.
  - TXT: Python native standard library with UTF-8 / latin-1 fallback.
- **Persistence:** SQLite managed via SQLAlchemy 2.0 with a repository abstraction layer. Primary keys use UUIDs so the schema can migrate to PostgreSQL by simply updating the database connection URL in `.env`.
- **Frontend Stack:** React 18 / Vite with Tailwind CSS, Axios, React Router v6, and Lucide React icons. Clean 3-panel layout designed for enterprise research workspaces.

### 2. Guardrails & Safety Policy
- Document text is strictly parsed as untrusted context data. System instructions explicitly prohibit executing instructions found inside documents (indirect prompt injection defense).
- File uploads are validated by MIME type, extension, and content hashing (SHA-256) to detect duplicates and prevent directory traversal (`secure_filename`).
- API keys are strictly server-side environment variables; never exposed to the frontend.

### 3. Current State
- Documentation created: `PRD.md`, `ARCHITECTURE.md`, `AGENTS.md`, `TASKS.md`, `memory.md`, `README.md`.
- Waiting for user approval on proposed architecture and four-phase plan before generating code.



## Phase 1 Implementation Summary (2026-11-19)

### 1. Completed Deliverables
- **Extraction Pipeline:** Built `ExtractionService` supporting PyMuPDF (PDF page-by-page text), `python-docx` (Word paragraphs and tables), and multi-encoding UTF-8/Latin-1/CP1252 TXT parsing. Added defensive error handling for empty or malformed files.
- **Recursive Chunking:** Built `ChunkingService` preserving document IDs, page numbers, and chunk indices, using hierarchical delimiters with configurable overlap.
- **Local Embedding & FAISS Vector Indexing:** 
  - Sentence Transformers `all-MiniLM-L6-v2` (384 dimensions) pre-cached directly in `backend/data/models/` for 100% offline, self-contained execution.
  - Built `VectorStore` using `faiss.IndexIDMap2(faiss.IndexFlatIP)` with unit-normalized vectors (cosine similarity) and bidirectional `faiss_id <-> chunk_id` mapping.
  - Implemented reentrant lock (`threading.RLock`) to guarantee thread safety during atomic vector mutations and disk persistence.
- **Document Management & Persistence:**
  - Implemented SQLAlchemy 2.0 ORM models (`Document`, `DocumentChunk`) and repository classes (`DocumentRepository`, `ChunkRepository`).
  - Implemented `DocumentService` with SHA-256 deduplication, background task ingestion, and cascading deletion (removing file, DB records, and FAISS vectors).
  - Built FastAPI endpoints: `POST /api/v1/documents/upload`, `GET /api/v1/documents`, `GET /api/v1/documents/{id}`, `GET /api/v1/documents/{id}/status`, `DELETE /api/v1/documents/{id}`, `POST /api/v1/documents/{id}/reindex`.
- **Frontend SaaS UI:**
  - Initialized React/Vite/Tailwind CSS workspace with three-part layout (Sidebar, Header, Main).
  - Built interactive `UploadDropzone` (drag & drop, progress bar, format validation), `DocumentList` (search, filtering, live polling for processing states, cascading deletion, re-indexing), and `DocumentDetailModal` (chunk provenance and SHA-256 inspection).
  - Verified production build (`npm run build`) succeeded with 0 errors.
- **Testing & Verification:**
  - 11 unit & integration tests passing in `backend/tests/` (PDF extraction, DOCX extraction, TXT extraction, chunking, embeddings, FAISS vector store, API endpoints).
  - End-to-end lifecycle verification test (`test_e2e_phase1.py`) passing with 100% success rate.


## Phase 2 Implementation Summary (2026-11-19)

### 1. Completed Deliverables
- **Semantic Retrieval Service:** Built `RetrievalService` providing cosine similarity search against FAISS `IndexFlatIP`, configurable $K$ and thresholding, and document subset filtering.
- **Gemini Service:** Implemented `GeminiService` using official `google-genai` SDK with model fallback logic (`gemini-3.1-flash-lite`, `gemini-3.8-flash`, `gemini-flash-latest`) to withstand upstream demand spikes.
- **Grounded RAG Engine:** Built `RAGService` with prompt templating, strict grounding rules, automatic numbered citation parsing (`[1]`, `[2]`), provenance mapping to chunk and page numbers, and explicit negative fallback assertion for queries lacking context.
- **REST Endpoints:** Added `POST /api/v1/search/semantic` and `POST /api/v1/rag/query`.
- **Frontend Research Workspace:**
  - Built interactive 3-panel Research Workspace ([WorkspacePage.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/pages/WorkspacePage.jsx)).
  - Built [MessageItem.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/components/chat/MessageItem.jsx) with clickable citation chips, confidence indicator, and source badges.
  - Built [PassageInspector.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/components/chat/PassageInspector.jsx) showing chunk text, match percentage, page numbers, and chunk IDs with interactive highlight sync.
  - Added document scope filter to toggle between corpus-wide search and targeted document search.
- **Verification:** All 16 automated tests passed, including `test_live_rag.py` verifying real retrieval and response generation via Google Gemini API.


## Phase 3 Implementation Summary (2026-11-19)

### 1. Completed Deliverables
- **Specialized Agent Tools:** Built 5 autonomous tools under `backend/app/tools/`:
  1. `search_documents`: Corpus-wide vector retrieval returning passages and metadata.
  2. `summarize_document`: Structured executive summary (`executive_summary`, `key_findings`, `methodology_or_structure`, `conclusions`).
  3. `compare_documents`: Cross-document diff analysis highlighting agreements, differences, and contradictions.
  4. `extract_information`: Schema-driven structured JSON extractor with evidence provenance.
  5. `answer_from_documents`: Targeted grounded Q&A with exact page citations.
- **Gemini Function Calling Loop:**
  - Implemented `AgentService` mapping tools to Gemini's native `FunctionDeclaration` specs.
  - Multi-hop agent loop (capped at max 5 iterations for safety) dynamically executing local tools and returning `function_response` payloads to Gemini until a grounded answer is produced.
  - Anti-hallucination guardrails and passive document data treatment.
- **Persistent Conversational Memory:**
  - Implemented `ConversationRepository` managing SQLite sessions and messages.
  - Implemented `MemoryService` with sliding-window history (last 6 turns retained in raw format) and asynchronous summary compression of older turns.
  - Endpoints: `POST /api/v1/agent/chat`, `GET /api/v1/conversations`, `POST /api/v1/conversations`, `GET /api/v1/conversations/{id}`, `PATCH /api/v1/conversations/{id}`, `DELETE /api/v1/conversations/{id}`.
- **UI Enhancements:**
  - Built [ToolExecutionBadge.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/components/agent/ToolExecutionBadge.jsx) to display autonomous tool executions with collapsible parameter inspection.
  - Built [SidebarConversations.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/components/chat/SidebarConversations.jsx) for session switching, renaming, and deleting directly in the sidebar.
  - Updated [WorkspacePage.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/pages/WorkspacePage.jsx) with agent tool calling execution indicators and multi-turn context retention.
- **Verification:**
  - 21 passing automated tests in `backend/tests/` including `test_agent_tools.py` and `test_live_agent.py` exercising real Gemini tool calling and follow-up conversational memory.


## Phase 4 Implementation Summary (2026-11-19)

### 1. Completed Deliverables
- **Benchmark Evaluation Dataset:**
  - Seeded 3 representative domain documents in `backend/eval_data/documents/`: `cloud_computing_sla.txt` (SLA commitments, maintenance windows, credit tiers), `ai_ethics_guidelines.txt` (AI governance, HITL oversight, fairness audits), and `employee_travel_policy.txt` (meal per diem, flight booking standards, receipt thresholds).
  - Designed golden QA dataset in `backend/eval_data/golden_dataset.json` covering answerable queries, grounded keyword verification, and negative fallback rejection cases.
- **Retrieval Evaluation Engine:**
  - Implemented `EvaluationService.evaluate_retrieval_query()` calculating real retrieval metrics:
    - **Precision@K**: $\frac{|Retrieved \cap Relevant|}{K}$
    - **Recall@K**: $\frac{|Retrieved \cap Relevant|}{|Total\ Relevant\ in\ Corpus|}$
    - **Mean Reciprocal Rank (MRR)**: Reciprocal rank of first relevant retrieved chunk.
    - **NDCG@K**: Normalized Discounted Cumulative Gain against ideal ranking.
    - **Latency Profiling**: Microsecond-accurate retrieval latency benchmarking.
- **Answer Quality Evaluation Engine:**
  - Rule-based evaluation: Citation presence, citation provenance validity, length validation, and negative rejection correctness for out-of-domain/unanswerable queries.
  - LLM-as-a-judge: Impartial Gemini evaluation measuring Faithfulness (0-1), Context Relevance (0-1), and Answer Relevance (0-1) with structured rationale.
  - Resilience: Automatic heuristic fallback ensures evaluation continues even during external rate limits.
- **Evaluation REST Endpoints:**
  - `POST /api/v1/evaluation/run`: Runs full benchmark suite across all test cases and persists summary.
  - `GET /api/v1/evaluation/results`: Retrieves latest evaluation run metrics from disk.
  - `GET /api/v1/evaluation/benchmark`: Returns golden QA test questions.
- **Evaluation Dashboard UI:**
  - Built interactive benchmark dashboard ([EvaluationPage.jsx](file:///c:/Users/meshr/Documents/1.%20SPIT/Projects/DocuMind/frontend/src/pages/EvaluationPage.jsx)).
  - Metric summary cards: Precision@K, Recall@K, MRR, NDCG, Average Latency, Faithfulness, Answer Relevance, and Citation Integrity.
  - Interactive tabs: Detailed retrieval breakdown table with collapsible passage inspection, answer/LLM judge scorecard with rationale, and golden dataset explorer.
  - Live execution controls: Top-K selector, LLM Judge toggle, and run button with animated progress.
- **Production Packaging & Dockerization:**
  - `backend/Dockerfile`: Python 3.12-slim container with health check and directory layout.
  - `frontend/Dockerfile`: Multi-stage build (Node 20 build stage -> Nginx Alpine runtime) with client-side SPA routing and backend proxying.
  - `docker-compose.yml`: Multi-container orchestration with persistent volume bindings and dependent service health checks.
  - Updated `.env.example` and healthcheck endpoints (`/health` and `/api/v1/health`).
- **Comprehensive Testing & Verification:**
  - 26 passing automated pytest tests in `backend/tests/` with 100% pass rate.
  - Production frontend build (`npm run build`) passing with 0 warnings.


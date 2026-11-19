# DocuMind - Implementation Task Breakdown

This document tracks progress across the four development phases. Each phase must be completed and tested before moving to the next.

---

## Phase 1: Foundation and Document Management
- [x] **Task 1.1: Project Setup & Repository Scaffolding**
  - [x] Initialize Python backend with virtual environment, `requirements.txt`, and FastAPI structure.
  - [x] Initialize React frontend using Vite, Tailwind CSS, Axios, and React Router.
  - [x] Configure environment variables (`.env.example`, `.env`).
- [x] **Task 1.2: Database Persistence & Storage Setup**
  - [x] Configure SQLite with SQLAlchemy ORM and repository pattern (`DocumentRepository`, `ChunkRepository`).
  - [x] Create models: `Document`, `DocumentChunk`.
  - [x] Create storage directories for uploads (`backend/data/uploads`) and vector index (`backend/data/vector`).
- [x] **Task 1.3: Document Extraction Service**
  - [x] Implement `ExtractionService` with PyMuPDF for PDF (page-aware text extraction).
  - [x] Implement DOCX extraction using `python-docx`.
  - [x] Implement TXT extraction with encoding fallback.
  - [x] Add unit tests for extraction with sample files.
- [x] **Task 1.4: Chunking Service**
  - [x] Implement `ChunkingService` with recursive splitting, configurable token size and overlap.
  - [x] Preserve chunk metadata (page number, chunk index, parent document ID).
  - [x] Add unit tests for chunking edge cases (small files, large paragraphs).
- [x] **Task 1.5: Embedding & FAISS Vector Store**
  - [x] Implement `EmbeddingService` using `SentenceTransformers('all-MiniLM-L6-v2')` with L2 normalization.
  - [x] Implement `VectorStore` using `faiss.IndexFlatIP` with disk persistence and chunk ID mapping.
  - [x] Support vector addition, deletion, and index rebuilding from database.
- [x] **Task 1.6: Document Service & Ingestion API**
  - [x] Implement `DocumentService` coordinating upload, SHA-256 deduplication, background ingestion, and cascading deletion.
  - [x] Build FastAPI endpoints: `POST /api/v1/documents/upload`, `GET /api/v1/documents`, `GET /api/v1/documents/{id}`, `DELETE /api/v1/documents/{id}`, `POST /api/v1/documents/{id}/reindex`.
- [x] **Task 1.7: Frontend Document Management UI**
  - [x] Build responsive three-part layout (Sidebar, Main Workspace, Right Inspector).
  - [x] Build Document Library page with drag-and-drop upload, processing badges, and delete actions.
  - [x] Verify end-to-end upload, extraction, chunking, and FAISS indexing with test files.

---

## Phase 2: RAG Pipeline and Research Workspace
- [ ] **Task 2.1: Semantic Retrieval Engine**
  - [ ] Implement `RetrievalService` with query embedding, FAISS top-K lookup, score thresholding, and document-level filtering.
  - [ ] Add unit tests for retrieval scoring and metadata filtering.
- [ ] **Task 2.2: Gemini LLM Integration**
  - [ ] Implement `GeminiService` integrating Google Gemini API via official SDK.
  - [ ] Handle API key validation, timeouts, retries, and rate limit handling.
- [ ] **Task 2.3: Grounded RAG Pipeline**
  - [ ] Implement `RAGService` with prompt assembly, strict evidence grounding, and negative assertion fallback when context is absent.
  - [ ] Implement citation extraction and verification linking chunk IDs to document page numbers.
  - [ ] Build FastAPI endpoint: `POST /api/v1/rag/query`.
- [ ] **Task 2.4: Research Workspace UI**
  - [ ] Build conversational interface with chat messages, user/assistant bubbles, and typing states.
  - [ ] Build interactive citation cards and right-panel source passage inspector.
  - [ ] Implement document selection filter for targeted search.
  - [ ] Verify end-to-end RAG question answering with citations.

---

## Phase 3: AI Research Agent and Conversational Memory
- [ ] **Task 3.1: Agent Tool Implementation**
  - [ ] Implement `search_documents` tool.
  - [ ] Implement `summarize_document` tool (structured multi-section summary).
  - [ ] Implement `compare_documents` tool (agreements, differences, contradictions).
  - [ ] Implement `extract_information` tool (schema-driven structured JSON extraction).
  - [ ] Implement `answer_from_documents` tool.
- [ ] **Task 3.2: Gemini Function Calling Agent Loop**
  - [ ] Implement `AgentService` managing multi-turn tool calling orchestration loop.
  - [ ] Add safety bounds (max tool hops, error trapping, sanitization).
  - [ ] Build FastAPI endpoint: `POST /api/v1/agent/chat`.
- [ ] **Task 3.3: Persistent Conversational Memory**
  - [ ] Implement `ConversationRepository` and models (`Conversation`, `Message`).
  - [ ] Implement `MemoryService` with sliding window history and session summary compression.
  - [ ] Build conversation endpoints: `POST /api/v1/conversations`, `GET /api/v1/conversations`, `GET /api/v1/conversations/{id}`, `DELETE /api/v1/conversations/{id}`.
- [ ] **Task 3.4: Agent Workspace Frontend**
  - [ ] Add conversation list and session switcher in sidebar.
  - [ ] Display agent tool activity indicators (e.g. "Searching documents...", "Comparing doc A and doc B").
  - [ ] Display structured JSON extraction tables and comparative diff views in chat.
  - [ ] Verify multi-turn conversational memory with follow-up questions.

---

## Phase 4: Evaluation, Testing and Deployment
- [ ] **Task 4.1: Benchmark Evaluation Dataset**
  - [ ] Create reproducible golden evaluation dataset (`backend/eval_data/`): sample documents, benchmark queries, expected relevant chunk IDs, and reference answers.
- [ ] **Task 4.2: Retrieval Evaluation Engine**
  - [ ] Implement automated calculation of Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and NDCG.
  - [ ] Measure retrieval latency profiling.
- [ ] **Task 4.3: Answer Quality Evaluation Engine**
  - [ ] Implement rule-based evaluation (citation verification, hallucination red flags).
  - [ ] Implement LLM-as-a-judge evaluation for faithfulness, context relevance, and answer relevance.
  - [ ] Build evaluation endpoints: `POST /api/v1/evaluation/run`, `GET /api/v1/evaluation/results`.
- [ ] **Task 4.4: Evaluation Dashboard UI**
  - [ ] Build frontend Evaluation page with metric summary cards, latency charts, and evaluation run trigger.
  - [ ] Display detailed per-query evaluation breakdown table.
- [ ] **Task 4.5: Automated Testing Suite**
  - [ ] Write unit tests for extraction, chunking, embeddings, vector store, and RAG.
  - [ ] Write integration tests for API endpoints with mock Gemini calls and real-key toggle.
  - [ ] Run test suite and ensure 100% passing tests.
- [ ] **Task 4.6: Dockerization & Production Packaging**
  - [ ] Create production backend `Dockerfile`.
  - [ ] Create production frontend `Dockerfile` (multi-stage build with Nginx).
  - [ ] Create `docker-compose.yml` with persistent storage volumes and healthcheck endpoints.
  - [ ] Verify end-to-end startup via Docker Compose.
- [ ] **Task 4.7: Documentation & Final Verification**
  - [ ] Complete comprehensive `README.md` with architectural diagrams, API docs, and step-by-step setup guide.
  - [ ] Review against all 15 acceptance criteria.


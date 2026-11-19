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

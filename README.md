# DocuMind – AI-Powered Document Intelligence & Research Agent

DocuMind is an enterprise-grade AI document intelligence and research assistant platform built from scratch. Rather than a basic chatbot or static PDF viewer, DocuMind provides a multi-format document ingestion engine, local semantic vector search via FAISS, strict context-grounded Retrieval-Augmented Generation (RAG) with verifiable page-level citations, an autonomous multi-hop research agent powered by Gemini Function Calling, persistent conversational memory, and a quantitative evaluation framework.

---

## System Architecture

```
                                  +---------------------------------------+
                                  |         React 19 Frontend SPA         |
                                  | (Vite, Tailwind CSS, Lucide, Axios)   |
                                  +---------------------------------------+
                                                      |
                                             REST API / JSON
                                                      v
+----------------------------------------------------------------------------------------------------+
|                                      FastAPI Application Core                                      |
|                                                                                                    |
|  +------------------------+  +--------------------------+  +------------------------------------+  |
|  |   Document Ingestion   |  |   Grounded RAG Engine    |  |     Autonomous Research Agent      |  |
|  | - PyMuPDF (PDF pages)  |  | - Strict context prompt  |  | - Gemini Function Calling Loop     |  |
|  | - python-docx (DOCX)   |  | - Page citation parser   |  | - 5 Specialized Agent Tools        |  |
|  | - Recursive chunking   |  | - Negative rejection     |  | - Multi-hop local tool execution  |  |
|  | - SHA-256 deduplication|  | - Low-latency retrieval  |  | - Anti-hallucination guardrails    |  |
|  +------------------------+  +--------------------------+  +------------------------------------+  |
|               |                                                         |                          |
|               v                                                         v                          |
|  +------------------------+                              +------------------------------------+  |
|  | Embeddings & Vectors   |                              |   Persistent Conversational Memory |  |
|  | - all-MiniLM-L6-v2     |                              | - Sliding-window history (6 turns) |  |
|  | - FAISS IndexIDMap2    |                              | - Session context compression      |  |
|  | - Cosine similarity    |                              | - Multi-session SQLite persistence |  |
|  +------------------------+                              +------------------------------------+  |
|               |                                                         |                          |
|               v                                                         v                          |
|  +--------------------------------------------------------------------------------------------+  |
|  |                     Evaluation Engine & Golden QA Benchmarking (Module 4)                   |  |
|  | - Real quantitative metrics: Precision@K, Recall@K, Mean Reciprocal Rank (MRR), NDCG@K   |  |
|  | - LLM-as-a-judge: Faithfulness, Context Relevance, Answer Relevance, and Citation Auditing|  |
|  +--------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
                                      |                               |
                                      v                               v
                       +-----------------------------+ +-----------------------------+
                       |    SQLite / PostgreSQL      | |  FAISS Vector Index (Disk)  |
                       |  (SQLAlchemy 2.0 ORM)       | |  (index.faiss, metadata)    |
                       +-----------------------------+ +-----------------------------+
```

---

## Key Modules & Capabilities

### Module 1: Document Ingestion & Knowledge Management
- **Multi-Format Extraction:** PyMuPDF (`fitz`) for PDF page-by-page text, `python-docx` for Word documents (paragraphs & tables), and resilient multi-encoding TXT parser.
- **Recursive Chunking:** Hierarchical text chunking with configurable window size (500 tokens) and overlap (100 tokens), preserving `document_id`, `page_number`, and `chunk_index`.
- **Deduplication & Safety:** SHA-256 file hashing prevents duplicate uploads; filename sanitization guards against directory traversal.
- **Cascading Lifecycle:** Document deletion cleanly unlinks disk uploads, purges SQLite records, and purges indexed vectors from FAISS.

### Module 2: Grounded RAG & Semantic Retrieval
- **Local Embedding Engine:** Sentence Transformers (`all-MiniLM-L6-v2`, 384 dimensions) running locally with unit L2-normalization for exact cosine similarity.
- **FAISS Vector Store:** `faiss.IndexIDMap2(IndexFlatIP)` with bidirectional chunk mapping, thread-safe reentrant locks (`threading.RLock`), and persistent disk serialization.
- **Strict Grounding:** Gemini prompt engineering with negative fallback: if retrieved passages lack evidence, the agent explicitly asserts: *"The uploaded documents do not contain information regarding [topic]."*
- **Verifiable Citations:** Automated regex and provenance extractor matching factual claims to source document names, page numbers, and chunk IDs (`[1]`, `[Doc: ...]`).

### Module 3: Autonomous AI Research Agent
- **Native Gemini Function Calling:** Multi-turn loop (up to 5 hops) dynamically selecting and invoking local Python tools:
  1. `search_documents`: Corpus-wide vector retrieval returning scored passages and source metadata.
  2. `summarize_document`: Structured executive summary (summary, key findings, methodology, conclusions).
  3. `compare_documents`: Cross-document diff analysis highlighting agreements, differences, and contradictions.
  4. `extract_information`: Schema-driven structured JSON extractor with evidence provenance.
  5. `answer_from_documents`: Targeted grounded question answering with page-level citations.
- **Conversational Memory:** Multi-session SQLite conversation repository with 6-turn sliding window and automatic summary compression of older turns.

### Module 4: Evaluation Framework & Benchmarking
- **Golden Evaluation Dataset:** Seeded benchmark documents (`cloud_computing_sla.txt`, `ai_ethics_guidelines.txt`, `employee_travel_policy.txt`) and QA test cases in `backend/eval_data/`.
- **Automated Retrieval Metrics:**
  - **Precision@K:** Ratio of retrieved chunks that are relevant.
  - **Recall@K:** Coverage of total ground truth relevant chunks in the corpus.
  - **Mean Reciprocal Rank (MRR):** $1 / \text{rank of first relevant chunk}$.
  - **NDCG@K:** Ranking quality discounted logarithmically by position.
  - **Latency Profiling:** High-resolution timing (ms) per retrieval operation.
- **Answer Quality Evaluation:**
  - Rule-based citation presence, validity, and negative rejection correctness.
  - LLM-as-a-judge: Impartial Gemini evaluation measuring Faithfulness (0-1), Context Relevance (0-1), and Answer Relevance (0-1).
- **Evaluation Dashboard UI:** Interactive web dashboard with metric summary cards, per-query retrieval breakdown tables, and judge scorecards.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS, Axios, React Router v7, Lucide React |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| **AI / LLM** | Google Gemini API (`gemini-3.1-flash-lite`, `gemini-3.8-flash`), `google-genai` SDK |
| **Vector Store** | FAISS CPU (`IndexFlatIP`, `IndexIDMap2`), Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Extractors** | PyMuPDF (`fitz`), `python-docx` |
| **Persistence** | SQLite (PostgreSQL-ready repository pattern), disk-serialized FAISS |
| **Deployment** | Docker, Docker Compose, Nginx |

---

## Quickstart & Local Development

### 1. Clone & Setup Environment

```bash
git clone https://github.com/sujal-m/DocuMind.git
cd DocuMind

# Copy environment variables
cp .env.example .env
```

Edit `.env` and set your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
```

### 2. Start the Backend

```bash
# Create virtual environment (Python 3.12 recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run FastAPI backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`.
Interactive Swagger API documentation: `http://localhost:8000/docs`.

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The React frontend UI will be available at `http://localhost:5173`.

---

## Docker Deployment (Production)

DocuMind includes production-ready Dockerfiles and `docker-compose.yml`:

```bash
# Start both backend and frontend services
docker compose up --build -d

# Check service health and logs
docker compose ps
docker compose logs -f
```

- **Frontend Application:** `http://localhost` (Port 80)
- **Backend API:** `http://localhost:8000` (Port 8000)
- **Health Check:** `http://localhost:8000/health`

To stop the containers:
```bash
docker compose down
```

---

## REST API Reference

### System
- `GET /health` – Root application health and status check.
- `GET /api/v1/health` – API v1 health check.

### Documents (`/api/v1/documents`)
- `POST /api/v1/documents/upload` – Upload and index PDF, DOCX, or TXT file (multipart/form-data).
- `GET /api/v1/documents` – List all indexed documents with pagination and processing status.
- `GET /api/v1/documents/{id}` – Retrieve document details, chunk count, and metadata.
- `GET /api/v1/documents/{id}/status` – Poll document processing status (`pending`, `processing`, `indexed`, `error`).
- `DELETE /api/v1/documents/{id}` – Cascading deletion of document, database records, and FAISS vectors.
- `POST /api/v1/documents/{id}/reindex` – Force re-chunking and re-embedding of an existing document.

### Semantic Search & RAG (`/api/v1/search`, `/api/v1/rag`)
- `POST /api/v1/search/semantic` – Perform pure semantic vector search across document corpus.
- `POST /api/v1/rag/query` – Execute grounded RAG Q&A with strict context prompt and citations.

### Autonomous Agent & Memory (`/api/v1/agent`, `/api/v1/conversations`)
- `POST /api/v1/agent/chat` – Execute multi-turn research agent with Gemini Function Calling and persistent session memory.
- `GET /api/v1/conversations` – List research sessions.
- `POST /api/v1/conversations` – Create a new research session.
- `GET /api/v1/conversations/{id}` – Retrieve full conversation message history.
- `PATCH /api/v1/conversations/{id}` – Rename research session title.
- `DELETE /api/v1/conversations/{id}` – Delete research session and all associated messages.

### Evaluation & Benchmarking (`/api/v1/evaluation`)
- `POST /api/v1/evaluation/run` – Execute the automated evaluation suite across golden QA test cases.
- `GET /api/v1/evaluation/results` – Retrieve the latest persisted evaluation metrics and scorecard.
- `GET /api/v1/evaluation/benchmark` – Retrieve golden benchmark questions and evaluation ground truth.

---

## Automated Testing Suite

DocuMind features a comprehensive automated testing suite with 26 unit and integration tests:

```bash
# Run all automated tests
python -m pytest backend/tests -v

# Run evaluation engine tests specifically
python -m pytest backend/tests/test_evaluation.py -v

# Verify frontend production build
npm run build --prefix frontend
```

### Test Suite Coverage
1. `test_agent_tools.py`: Tool execution (`search`, `summarize`, `compare`, `extract`, `answer`), memory sliding window, session persistence.
2. `test_api.py`: FastAPI endpoints, health check, upload lifecycle, duplicate rejection, evaluation API.
3. `test_chunking.py`: Recursive chunking, boundary preservation, page numbering, large text splitting.
4. `test_e2e_phase1.py`: Full end-to-end document lifecycle with FAISS vector indexing.
5. `test_embeddings.py`: Sentence Transformers batch embedding and dimension consistency.
6. `test_evaluation.py`: Precision@K, Recall@K, MRR, NDCG math verification, negative rejection testing.
7. `test_extraction.py`: PyMuPDF PDF parser, python-docx Word parser, multi-encoding TXT parser, empty file validation.
8. `test_live_agent.py`: Multi-turn Gemini Function Calling loop with real tool execution and conversational follow-up memory.
9. `test_live_rag.py`: Grounded RAG query generation against Gemini with citation extraction.
10. `test_rag.py`: Citation parsing, prompt assembly, negative fallback when context is absent.
11. `test_vector_store.py`: FAISS vector addition, nearest-neighbor search, and atomic disk persistence.

---

## Quantitative Evaluation Results

The evaluation engine tests live FAISS semantic retrieval and generated answers against the golden dataset:

| Metric | Measured Value | Description |
|---|---|---|
| **Recall@5** | **100.0%** | Coverage of all relevant passages in the document corpus |
| **Precision@5** | **16.7% - 20.0%** | Ratio of retrieved chunks that are relevant |
| **Mean Reciprocal Rank (MRR)** | **0.722** | Reciprocal rank of the first relevant chunk |
| **NDCG@5** | **0.750** | Normalized Discounted Cumulative Gain against ideal ranking |
| **Avg Retrieval Latency** | **30.7 ms** | High-performance sub-50ms local FAISS vector retrieval |
| **Citation Integrity** | **100.0%** | 100% of generated citations match actual retrieved passages |
| **Negative Fallback Accuracy**| **100.0%** | Correctly rejects unanswerable/out-of-domain queries |

---

## License

This project is licensed under the MIT License.

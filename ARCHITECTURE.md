# DocuMind - System Architecture & Technical Design

## 1. Architectural Overview

DocuMind follows a clean, decoupled, layered micro-architecture separating API delivery, business logic, vector indexing, persistence, and external AI services.

```
+-------------------------------------------------------------------------------+
|                               Frontend (SPA)                                  |
|   React (Vite) + Tailwind CSS + Axios + React Router + Lucide Icons           |
|                                                                               |
|   [Dashboard]  [Document Library]  [Research Workspace]  [Eval Dashboard]     |
|         |                |                  |                    |            |
+---------+----------------+------------------+--------------------+------------+
                                   | REST API (JSON / FormData)
                                   v
+-------------------------------------------------------------------------------+
|                            Backend (FastAPI)                                  |
|                                                                               |
|   +-----------------------------------------------------------------------+   |
|   | API Router Layer (`app/api/v1/`)                                      |   |
|   | /documents | /search | /rag | /agent | /conversations | /eval | health |   |
|   +-----------------------------------------------------------------------+   |
|                                   |                                           |
|   +-----------------------------------------------------------------------+   |
|   | Service Layer (`app/services/`)                                       |   |
|   | - DocumentService (Upload, validation, SHA-256 deduplication)          |   |
|   | - ExtractionService (PyMuPDF, python-docx, text parsers)              |   |
|   | - ChunkingService (Recursive character text splitter with overlap)    |   |
|   | - EmbeddingService (SentenceTransformers all-MiniLM-L6-v2, 384d)      |   |
|   | - VectorStore (FAISS IndexFlatIP + ID mapping + disk persistence)     |   |
|   | - RetrievalService (Top-K similarity, filtering, score ranking)       |   |
|   | - RAGService (Grounded prompt assembly, citation resolution)          |   |
|   | - AgentService (Gemini Function Calling orchestration loop)           |   |
|   | - MemoryService (Sliding-window + SQLite conversation retention)      |   |
|   | - EvaluationService (Precision@K, Recall@K, MRR, NDCG, LLM Judge)     |   |
|   +-----------------------------------------------------------------------+   |
|             |                     |                      |                    |
|             v                     v                      v                    v
|     [SQLite Database]     [Local File Store]     [FAISS Index]     [Google Gemini]
|      (SQLAlchemy/DAO)      (/data/uploads/)     (/data/vector/)     (Gemini 2.5/Flash)
+-------------------------------------------------------------------------------+
```

---

## 2. Directory Structure

```
DocuMind/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entrypoint & lifespan
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api_router.py    # Master router
│   │   │       ├── documents.py     # Upload, list, delete, status, reindex
│   │   │       ├── search.py        # Semantic search endpoints
│   │   │       ├── rag.py           # Standard grounded RAG Q&A
│   │   │       ├── agent.py         # Multi-turn agent with function calling
│   │   │       ├── conversations.py # Session management
│   │   │       └── evaluation.py    # Retrieval & answer quality eval
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic BaseSettings & env vars
│   │   │   ├── logging.py           # Structured logger configuration
│   │   │   └── security.py          # Path validation & sanitize utils
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── session.py           # SQLite engine & session factory
│   │   │   ├── base.py              # Declarative base
│   │   │   └── repositories/        # Repository pattern for DB operations
│   │   │       ├── document_repo.py
│   │   │       ├── chunk_repo.py
│   │   │       └── conversation_repo.py
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   └── evaluation.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── search.py
│   │   │   ├── rag.py
│   │   │   ├── agent.py
│   │   │   ├── conversation.py
│   │   │   └── evaluation.py
│   │   ├── services/                # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── chunking_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_store.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── agent_service.py
│   │   │   ├── memory_service.py
│   │   │   └── evaluation_service.py
│   │   ├── tools/                   # Agent tool definitions & executors
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── search_tool.py
│   │   │   ├── summarize_tool.py
│   │   │   ├── compare_tool.py
│   │   │   ├── extract_tool.py
│   │   │   └── answer_tool.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── hashing.py
│   │       └── text.py
│   ├── data/                        # Persistent volume mount
│   │   ├── uploads/
│   │   ├── vector/
│   │   └── documind.db
│   ├── eval_data/                   # Golden benchmark test dataset
│   │   ├── test_documents/
│   │   └── golden_qa.json
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_extraction.py
│   │   ├── test_chunking.py
│   │   ├── test_embeddings.py
│   │   ├── test_vector_store.py
│   │   ├── test_rag.py
│   │   ├── test_agent_tools.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/              # Navbar, Sidebar, Modal, Badge, Toast
│   │   │   ├── documents/           # UploadDropzone, DocList, DocStatus
│   │   │   ├── chat/                # ChatWindow, MessageItem, CitationCard
│   │   │   ├── search/              # SearchBar, PassageResultCard
│   │   │   ├── agent/               # ToolExecutionBadge, AgentThought
│   │   │   └── evaluation/          # MetricsCard, BenchmarkTable, RunModal
│   │   ├── layouts/
│   │   │   └── AppLayout.jsx        # Three-panel responsive layout
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── DocumentsPage.jsx
│   │   │   ├── WorkspacePage.jsx
│   │   │   ├── EvaluationPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── services/                # Axios API client modules
│   │   │   ├── api.js
│   │   │   ├── documentService.js
│   │   │   ├── searchService.js
│   │   │   ├── chatService.js
│   │   │   └── evalService.js
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── context/                 # Global state (Active Conversation, Docs)
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── infra/
│   └── docker-compose.yml
├── docs/
├── .env.example
├── AGENTS.md
├── PRD.md
├── ARCHITECTURE.md
├── TASKS.md
├── README.md
└── memory.md
```

---

## 3. Data Models & Entity-Relationship Design

```
+---------------------------------------------------------+
|                      Document                           |
+---------------------------------------------------------+
| id: String (UUID, PK)                                   |
| filename: String                                        |
| original_name: String                                   |
| file_type: String ("pdf" | "docx" | "txt")              |
| file_size: Integer (bytes)                              |
| file_hash: String (SHA-256 for duplicate detection)     |
| page_count: Integer (nullable for TXT)                  |
| status: String ("pending"|"processing"|"indexed"|"error")|
| error_message: Text (nullable)                          |
| created_at: DateTime                                    |
| updated_at: DateTime                                    |
+---------------------------------------------------------+
                           | 1
                           |
                           | N
+---------------------------------------------------------+
|                    DocumentChunk                        |
+---------------------------------------------------------+
| id: String (UUID, PK)                                   |
| document_id: String (FK -> Document.id)                 |
| chunk_index: Integer                                    |
| page_number: Integer                                    |
| content: Text                                           |
| token_count: Integer                                    |
| faiss_id: Integer (Index identifier in FAISS)           |
| created_at: DateTime                                    |
+---------------------------------------------------------+

+---------------------------------------------------------+
|                      Conversation                       |
+---------------------------------------------------------+
| id: String (UUID, PK)                                   |
| title: String                                           |
| model_name: String                                      |
| created_at: DateTime                                    |
| updated_at: DateTime                                    |
+---------------------------------------------------------+
                           | 1
                           |
                           | N
+---------------------------------------------------------+
|                        Message                          |
+---------------------------------------------------------+
| id: String (UUID, PK)                                   |
| conversation_id: String (FK -> Conversation.id)         |
| sender: String ("user" | "assistant" | "system")        |
| content: Text                                           |
| tool_calls_json: JSON/Text (Agent steps & tool payloads)|
| citations_json: JSON/Text (Document & page references)  |
| created_at: DateTime                                    |
+---------------------------------------------------------+
```

---

## 4. RAG & Vector Retrieval Pipeline

1. **Ingestion & Indexing:**
   - Document raw bytes are streamed to disk (`/data/uploads/<hash>.<ext>`).
   - `ExtractionService` parses text structure per page.
   - `ChunkingService` applies character/token recursion with overlap.
   - Chunks are saved to SQLite and passed to `EmbeddingService`.
   - Embeddings are computed with `SentenceTransformer('all-MiniLM-L6-v2')`, normalized to unit length ($L_2$).
   - Normalized vectors are added to `faiss.IndexFlatIP` (inner product = cosine similarity on normalized vectors).
   - The mapping `faiss_id -> chunk_id` is persisted to disk alongside the index.

2. **Query Retrieval Flow:**
   - Query text is embedded using the identical normalized model.
   - Vector store queries FAISS for top-$K$ chunks.
   - Chunk records are hydrated from SQLite using the mapped `chunk_id`s.
   - Metadata filters (e.g. `document_id in [selected_docs]`) are applied if specified.
   - Chunks are assembled into a grounded prompt context with strict citation headers.

3. **Grounded Generation (Gemini):**
   - Context is injected into a system prompt that mandates strict provenance.
   - The model answers the query and annotates references with `[Doc: <name>, Page: <page>, Chunk: <id>]`.
   - If the context does not contain sufficient factual evidence, the model emits an explicit negative assertion.

---

## 5. Agent Architecture & Function Calling

The AI Research Agent uses Gemini with tool/function calling:
- **Reasoning Loop:**
  1. The user request and conversation history are sent to Gemini with function declarations (`search_documents`, `summarize_document`, `compare_documents`, `extract_information`, `answer_from_documents`).
  2. If Gemini generates a `function_call`, the backend intercepts it, validates arguments, invokes the local service tool, and formats the tool output.
  3. The tool output is appended to the message sequence as a `function_response` and sent back to Gemini.
  4. The loop continues until Gemini produces the final user-facing response with full citations, or until safety depth (max 5 iterations) is reached.
- **Safety & Sandbox:** Tools only read pre-indexed document chunks or run pure deterministic aggregations. No arbitrary shell execution or SQL execution is permitted.

---

## 6. Evaluation Framework

1. **Retrieval Metrics:**
   - **Precision@K:** Proportion of retrieved top-K chunks that are relevant.
   - **Recall@K:** Proportion of all golden relevant chunks that appear in the top-K.
   - **MRR (Mean Reciprocal Rank):** Reciprocal rank of the first relevant chunk ($1/\text{rank}$).
   - **NDCG@K:** Normalized Discounted Cumulative Gain accounting for rank position.
2. **Answer Quality Metrics:**
   - **Faithfulness / Groundedness:** Verifies all claims against the retrieved chunk context.
   - **Answer Relevance:** Checks whether the response answers the actual user query.
   - **Citation Precision:** Verifies whether cited chunks actually support the claimed facts.
   - **Evaluation Dataset:** Provided in `eval_data/golden_qa.json` for deterministic, reproducible test runs.

---

## 7. Migration Readiness (SQLite to PostgreSQL)
- All database interactions use SQLAlchemy ORM with repository classes (`DocumentRepository`, `ChunkRepository`, etc.).
- UUID strings are used as primary keys instead of SQLite autoincrement integers.
- Switching to PostgreSQL requires only updating the `DATABASE_URL` environment variable and providing `asyncpg` or `psycopg2`.


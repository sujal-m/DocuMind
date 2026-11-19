# DocuMind – AI-Powered Document Intelligence & Research Agent

DocuMind is an enterprise-grade AI document intelligence and research platform. It transforms collections of PDF, DOCX, and TXT documents into an interactive knowledge base with grounded semantic retrieval, verifiable citations, autonomous multi-hop research tools, persistent conversational memory, and an evaluation framework.

---

## Architecture Highlights
- **Document Ingestion:** Multi-format extraction (PyMuPDF, python-docx), recursive chunking with page tracking, and SHA-256 deduplication.
- **Vector Search:** Local semantic embeddings using Sentence Transformers (`all-MiniLM-L6-v2`) and persistent FAISS vector indexing.
- **RAG & Grounding:** Strict context-grounded response generation via Google Gemini API with exact page-level citations and fallback when context is absent.
- **Autonomous Research Agent:** Multi-turn Gemini Function Calling orchestrating 5 specialized tools: `search_documents`, `summarize_document`, `compare_documents`, `extract_information`, and `answer_from_documents`.
- **Persistent Memory:** Multi-session conversation management with sliding-window history and SQLite persistence.
- **Evaluation Suite:** Measurable retrieval metrics (Precision@K, Recall@K, MRR, NDCG) and LLM-as-a-judge answer quality evaluation against a golden benchmark.
- **Production Ready:** Decoupled FastAPI backend and React/Vite/Tailwind frontend containerized with Docker Compose.

---

## Project Structure
```
DocuMind/
├── backend/            # FastAPI backend application
│   ├── app/            # Source code (API, core, database, models, schemas, services, tools)
│   ├── data/           # Persistent uploads, vector indexes, and SQLite DB
│   ├── eval_data/      # Golden benchmark dataset for retrieval evaluation
│   ├── tests/          # Unit and integration test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React + Vite + Tailwind CSS SPA
│   ├── src/            # Components, layouts, pages, services, hooks
│   ├── package.json
│   └── Dockerfile
├── infra/              # Docker Compose deployment configs
├── PRD.md              # Product Requirements Document
├── ARCHITECTURE.md     # System Architecture & Technical Specifications
├── AGENTS.md           # Agent & Tool Specifications
├── TASKS.md            # Implementation Task Tracker
├── memory.md           # Project Decision Log
└── README.md           # Getting Started & System Guide
```

---

## Development Roadmap
- **Phase 1:** Foundation and Document Management (Extraction, Chunking, Embeddings, FAISS, Document API & UI)
- **Phase 2:** RAG Pipeline and Research Workspace (Semantic Search, Gemini RAG, Citations, Research UI)
- **Phase 3:** AI Research Agent and Conversational Memory (Function Calling, Tools, Multi-turn Memory)
- **Phase 4:** Evaluation, Testing and Deployment (Retrieval & Answer Eval, Tests, Docker Compose)

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Google Gemini API Key
- Docker and Docker Compose (optional for containerized deployment)

### Setup Instructions
Detailed setup and run instructions will be updated as Phase 1 commences.


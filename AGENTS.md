# AGENTS.md - Developer & AI Agent Guidelines

Welcome to the **VMS_Help_Menu** (VAPSAI) repository. This document serves as the primary technical specification, operational guide, and rulebook for AI coding agents and developers working on this codebase.

---

## 1. Project Overview & Core Mission

**VMS_Help_Menu** is a specialized, production-ready **Pure Retrieval-Augmented Generation (RAG) Chatbot** designed to answer questions strictly from the VMS IssueManager knowledge base (`KB_PDF/VMS_IssueManager_Chatbot_KnowledgeBase.pdf`).

### Non-Negotiable Invariants
- **Pure RAG Focus**: This system is dedicated exclusively to accurate, grounded question-answering. Do **NOT** add lead collection forms, contact collection funnels, sales qualification gates, or marketing prompts.
- **Strict Grounding**: The LLM must answer questions using retrieved context from the knowledge base. If context is missing or irrelevant, it must gracefully inform the user rather than hallucinating.
- **Centralized Configuration**: All thresholds, model identifiers, API keys, paths, and limits **must** reside in `src/config.py`. Never hardcode magic numbers or environment variables in submodules.

---

## 2. System Architecture & Directory Structure

The project follows a clean, modular architecture separating retrieval, API handling, storage, and utility scripts:

```
VMS_Help_Menu/
├── src/                                # Main application package
│   ├── __init__.py                     # Package init
│   ├── config.py                       # Single source of truth for configuration & constants
│   ├── core/                           # Core RAG engine
│   │   ├── __init__.py
│   │   ├── rag.py                      # Main pipeline (answer_question, hybrid_search, chat)
│   │   ├── retrievers.py               # BM25Index, VectorRetriever, BM25Retriever
│   │   └── prompts.py                  # Prompt templates, formatting, query classification
│   ├── api/                            # REST API service layer
│   │   ├── __init__.py
│   │   ├── app.py                      # FastAPI app initialization, middleware, routes
│   │   └── schemas.py                  # Pydantic schemas (ChatRequest, ChatResponse)
│   ├── storage/                        # Persistence & external data integrations
│   │   ├── __init__.py
│   │   ├── cache.py                    # Exact & semantic response caching
│   │   ├── vector_db.py                # Chroma vector store loading and persistence
│   │   └── datastore.py                # External VMS conversation logger (HTTP API)
│   └── utils/                          # Cross-cutting utilities
│       ├── __init__.py
│       └── logging.py                  # Structured console and file logger
├── scripts/                            # Operational & CLI scripts
│   ├── __init__.py
│   ├── build_kb.py                     # Ingests PDF and generates Chroma vector DB
│   └── cli_chat.py                     # Interactive terminal chat interface
├── data/                               # Data persistence (ignored or runtime managed)
│   ├── chroma_db/                      # Chroma persistent SQLite & parquet files
│   ├── cache/                          # Exact/semantic cache (`chat_cache.json`, `bm25_index.pkl`)
│   └── logs/                           # System and conversation logs (`chat.log`)
├── KB_PDF/                             # Raw knowledge base PDF documentation
├── app.py                              # Root backward-compatible FastAPI entry point
├── main.py                             # Root backward-compatible CLI chat entry point
├── requirements.txt                    # Project Python dependencies
├── Dockerfile                          # Container specification
├── docker-compose.yml                  # Service orchestration (app + optional services)
├── .env                                # Local environment secrets (e.g. GROQ_API_KEY)
└── README.md                           # User-facing documentation
```

---

## 3. Technology Stack & External Services

| Component | Technology | Details |
|---|---|---|
| **Language** | Python 3.10+ | Strict type hints, modern syntax |
| **API Framework** | FastAPI + Uvicorn | Asynchronous background tasks, CORS enabled |
| **Data Validation** | Pydantic v2 | Request/Response payload validation |
| **LLM Inference** | Groq API (`langchain-groq`) | Model: `llama-3.1-8b-instant` |
| **Embeddings** | Ollama (`langchain-ollama`) | Model: `embeddinggemma:latest` |
| **Vector Store** | ChromaDB (`langchain-chroma`) | Persisted in `data/chroma_db/` |
| **Keyword Search** | Custom BM25 (`rank-bm25` / in-memory) | Persisted in `data/cache/bm25_index.pkl` |
| **Document Processing** | PyMuPDF (`fitz`), LangChain Splitters | RecursiveCharacterTextSplitter |
| **Datastore Logging** | Requests / FastAPI BackgroundTasks | Non-blocking async webhook to VMS staging |

---

## 4. Environment Setup & Configuration

### Prerequisites
- Python 3.10+ installed.
- Ollama service running locally with model `embeddinggemma:latest` pulled (`ollama pull embeddinggemma:latest`).
- A valid Groq API key set in `.env`.

### Environment Variables (`.env`)
```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Virtual Environment Activation (Windows)
```powershell
# PowerShell
.venv\Scripts\Activate.ps1

# Install / update dependencies
pip install -r requirements.txt
```

---

## 5. Development & Operational Workflows

### 1. Ingest Knowledge Base & Build Vector DB
Whenever the PDF documentation in `KB_PDF/` is updated or when initializing the database for the first time:
```powershell
python scripts/build_kb.py
```
*Note: This parses `KB_PDF/VMS_IssueManager_Chatbot_KnowledgeBase.pdf`, chunks text, computes embeddings using Ollama, and rebuilds `data/chroma_db`.*

### 2. Run the REST API Server
```powershell
# Using the root launcher
python app.py

# Or directly with Uvicorn (supports live reload during development)
uvicorn src.api.app:app --host 0.0.0.0 --port 5008 --reload
```
- Health Check: `GET http://localhost:5008/`
- Chat Webhook: `POST http://localhost:5008/webhook/chat`
  ```json
  {
    "user_id": "user123",
    "session_id": "session-xyz",
    "question": "How do I create a ticket in VMS?"
  }
  ```

### 3. Interactive CLI Chat
For fast debugging and testing retrieval loops in the console:
```powershell
python main.py
# or
python scripts/cli_chat.py
```

### 4. Docker Deployment
```powershell
docker compose up -d --build
```

---

## 6. Code Style & Engineering Standards

### Absolute Imports
Always use absolute imports rooted at `src.`:
```python
# CORRECT
from src.config import PERSIST_DIRECTORY, CHAT_MODEL
from src.core.rag import answer_question
from src.utils.logging import log_step, log_error

# INCORRECT
from ..config import PERSIST_DIRECTORY
from core.rag import answer_question
```

### Pathlib for Filesystem Operations
This project runs across Windows, macOS, and Linux containers. Always use `pathlib.Path` for path manipulations to prevent platform-specific slash bugs:
```python
# CORRECT
target_file = BASE_DIR / "data" / "cache" / "chat_cache.json"

# INCORRECT
target_file = str(BASE_DIR) + "\\data\\cache\\chat_cache.json"
```

### Type Annotations
All new functions and methods must include Python 3.10+ type hints:
```python
def answer_question(
    question: str,
    llm: Any,
    vector_db: Any,
    bm25_index: Any,
    chat_history: list[dict[str, str]] | None = None,
    cache: dict[str, Any] | None = None,
) -> tuple[str, bool]:
```

### Structured Logging
Do not use raw `print()` statements in core library or API modules (`src/core/`, `src/api/`, `src/storage/`). Use the centralized logger:
```python
from src.utils.logging import log_step, log_error

log_step("Executing hybrid search", query=question)
log_error("Failed to query datastore", exc=err)
```

---

## 7. RAG Pipeline Logic & Routing Invariants

When working with `src/core/rag.py` or modifying prompts in `src/core/prompts.py`, adhere to the four-tier routing hierarchy:

1. **Exact & Semantic Cache**: Check `src.storage.cache` first. If an exact match or semantic match above `SEMANTIC_CACHE_THRESHOLD` exists, return immediately.
2. **Small Talk / Greeting Route**: If `classify_query()` detects a greeting or non-technical pleasantry, respond with standard greeting instructions without querying vector or BM25 stores.
3. **Direct Content Route**: If query includes instructions with explicit embedded content (`DIRECT_CONTENT_HINTS`), use direct context prompt generation.
4. **Hybrid Retrieval (Vector + BM25)**:
   - Vector retriever fetches `VECTOR_TOP_K` semantic chunks.
   - BM25 retriever fetches `BM25_TOP_K` lexical matches.
   - Results are deduplicated and merged up to `FINAL_TOP_K`.
   - Prompt is generated and streamed/executed via Groq LLM.

---

## 8. Rules for AI Agents

When implementing changes or debugging issues in this repository:
1. **Never break backward compatibility** with `app.py` and `main.py` entry points.
2. **Do not remove or alter** the pure RAG nature of the assistant. Do not add sales pitches or lead capture hooks.
3. **Check configuration in `src/config.py`** before introducing new parameters or environment keys.
4. **Preserve docstrings and comments** in existing modules unless refactoring specifically demands an update.
5. **Verify file existence and directory paths** before file I/O operations (use `.mkdir(parents=True, exist_ok=True)`).

# VMS_Help_Menu - Pure RAG Chatbot

This is a **pure Retrieval Augmented Generation (RAG) chatbot** designed to answer questions from the VMS IssueManager knowledge base. It combines vector similarity search, keyword-based retrieval (BM25), and LLM-generated responses to provide accurate answers grounded in real documentation.

## System Overview

**Core Features:**
- ✅ **Pure RAG**: No lead capture, no sales funnel - focused entirely on question answering
- ✅ **Hybrid Search**: Combines vector search (semantic) + BM25 (keyword) for better recall
- ✅ **Intelligent Routing**: Automatically routes queries to cache, small talk handler, or RAG pipeline
- ✅ **Multi-turn Chat**: Maintains conversation history across sessions
- ✅ **Smart Caching**: Exact and semantic cache lookup for instant responses
- ✅ **REST API**: FastAPI endpoint for easy integration
- ✅ **Docker Ready**: Complete Docker Compose setup with Ollama support

## Project Structure

```
VMS_Help_Menu/
├── src/                                # Main application source code
│   ├── __init__.py
│   ├── config.py                       # All configuration constants
│   ├── core/                           # Core RAG logic
│   │   ├── __init__.py
│   │   ├── rag.py                      # Main RAG pipeline and chat loop
│   │   ├── retrievers.py               # BM25Index, VectorRetriever, BM25Retriever
│   │   └── prompts.py                  # Prompt construction functions
│   ├── api/                            # REST API layer
│   │   ├── __init__.py
│   │   ├── app.py                      # FastAPI application
│   │   └── schemas.py                  # Pydantic request/response models
│   ├── storage/                        # Data persistence layer
│   │   ├── __init__.py
│   │   ├── cache.py                    # Cache management (semantic + exact)
│   │   ├── vector_db.py                # Chroma vector database utilities
│   │   └── datastore.py                # External datastore API integration
│   └── utils/                          # Utility modules
│       ├── __init__.py
│       └── logging.py                  # Structured logging helpers
├── scripts/                            # Standalone utility scripts
│   ├── __init__.py
│   ├── build_kb.py                     # Build vector DB from PDF
│   └── cli_chat.py                     # Terminal-based chat interface
├── data/                               # Data and cache directories
│   ├── chroma_db/                      # Chroma vector database
│   ├── cache/                          # Response cache
│   │   └── chat_cache.json
│   └── logs/                           # Application logs
│       └── chat.log
├── app.py                              # API entry point (backward compatible)
├── main.py                             # CLI chat entry point (backward compatible)
├── .env                                # Environment variables
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Docker Compose setup
├── README.md                           # Project README
├── KB_PDF/    
│   └── VMS_IssueManager_Chatbot_KnowledgeBase.pdf  # Knowledge base PDF
└── DOCKER.md                           # Docker setup guide
```

## Module Organization

### `src/config.py`
**Centralized configuration management**
- All constants: paths, model names, parameters
- Regex patterns for query classification
- LLM and retrieval hyperparameters
- Helper function: `normalize_question()`

### `src/core/`
**Core RAG (Retrieval Augmented Generation) logic**

**`rag.py`**
- `answer_question()` - Main RAG pipeline with multi-route logic
- `chat()` - CLI chat loop
- `hybrid_search()` - Combines vector and BM25 results
- Router logic: cache → small talk → direct context → retrieval

**`retrievers.py`**
- `BM25Index` - Keyword-based search with BM25 scoring
- `VectorRetriever` - Semantic similarity search via Chroma
- `BM25Retriever` - BM25 wrapper interface
- `load_bm25_index()` - Loads or builds BM25 cache

**`prompts.py`**
- `build_prompt()` - Standard Q&A prompt with context
- `build_direct_context_prompt()` - For structured/direct requests
- `format_history()` - Conversation history formatting
- `classify_query()` - Routes query to appropriate handler

### `src/api/`
**REST API layer**

**`schemas.py`**
- `ChatRequest` - Pydantic model for chat endpoint
- `ChatResponse` - Response model with session_id and answer

**`app.py`**
- FastAPI application initialization
- CORS middleware configuration
- `GET /` - Health check endpoint
- `POST /webhook/chat` - Main chat endpoint
- Session management
- Background task integration with datastore

### `src/storage/`
**Data persistence layer**

**`vector_db.py`**
- `load_vector_store()` - Initialize Chroma from disk
- `load_all_documents()` - Retrieve all indexed documents

**`cache.py`**
- `load_cache()` / `save_cache()` - JSON cache persistence
- `get_cached_answer()` - Exact and semantic cache lookup
- `update_cache()` - Add/update cache entries
- `make_cache_key()` - Key generation with SHA256 hashing
- Semantic similarity matching with cosine distance (threshold: 0.90)

**`datastore.py`**
- `save_conversation()` - Background task for external API integration
- Sends chat to configured external datastore

### `src/utils/`
**Utility modules**

**`logging.py`**
- `log_step()` - Structured logging for processing steps
- `log_error()` - Error logging with traceback
- Re-exports Python's standard `logging` module

### `scripts/`
**Standalone utility scripts**

**`build_kb.py`**
- `load_pdf_documents()` - Extract text from PDF
- `build_vector_store()` - Create Chroma vector database
- Run: `python scripts/build_kb.py`

**`cli_chat.py`**
- Terminal-based chat interface
- Run: `python scripts/cli_chat.py` or `python main.py`

## Entry Points

### Backward Compatible (Root Level)

**`app.py`** - API Server
```bash
python app.py
# or
uvicorn src.api.app:app --host 0.0.0.0 --port 5008 --reload
```

**`main.py`** - CLI Chat
```bash
python main.py
```

### New Structure (Recommended)

**API Server:**
```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 5008 --reload
```

**CLI Chat:**
```bash
python scripts/cli_chat.py
```

**Build Knowledge Base:**
```bash
python scripts/build_kb.py
```

## API Endpoints

### Health Check
```http
GET /
```

Response:
```json
{
  "status": "ok"
}
```

### Chat Webhook
```http
POST /webhook/chat
Content-Type: application/json

{
  "message": "What is VAPS?",
  "session_id": "user-123"
}
```

Response:
```json
{
  "session_id": "user-123",
  "answer": "VAPS is..."
}
```

## Configuration

### Environment Variables (`.env`)
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Application Configuration (`src/config.py`)
**Embedding & LLM:**
- `EMBEDDING_MODEL`: Ollama embedding model (default: `embeddinggemma:300m`)
- `CHAT_MODEL`: LLM model (default: `llama-3.1-8b-instant`)
- `LLM_TEMPERATURE`: Creativity level (default: 0.3 for API, 0.7 for CLI)
- `LLM_MAX_TOKENS`: Max response length (default: 160)

**Retrieval Parameters:**
- `VECTOR_TOP_K`: Vector search results (default: 2)
- `BM25_TOP_K`: BM25 search results (default: 2)
- `FINAL_TOP_K`: Final merged results (default: 3)
- `MAX_CONTEXT_CHARS`: Context window size (default: 1800)

**Cache & History:**
- `MAX_HISTORY_MESSAGES`: Conversation history window (default: 6)
- `MAX_CACHE_ENTRIES`: Maximum cached responses (default: 200)
- `SEMANTIC_CACHE_THRESHOLD`: Cache semantic match threshold (default: 0.90)

**Data Paths:**
- `PERSIST_DIRECTORY`: Chroma DB location (`data/chroma_db/`)
- `CACHE_FILE`: Cache storage (`data/cache/chat_cache.json`)
- `PDF_PATH`: Knowledge base PDF (`KB_PDF/VMS_IssueManager_Chatbot_KnowledgeBase.pdf`)

## Setup Instructions

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Ollama (running with `embeddinggemma:300m` model)
- Groq API key (get from https://console.groq.com)

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### 4. Build Knowledge Base
```bash
# Requires Ollama running
python scripts/build_kb.py
# This creates data/chroma_db/ with vector embeddings
```

### 5. Run Application

**Option A: FastAPI Server**
```bash
python app.py
# Runs on http://localhost:5008
# POST http://localhost:5008/webhook/chat with {"message": "...", "session_id": "..."}
```

**Option B: CLI Chat**
```bash
python main.py
# Interactive terminal chat interface
```

### 6. Docker Deployment

**Build and Run with Docker Compose:**
```bash
# Build images and start all services
docker compose up --build

# Services started:
# - vapshelp-api: Main API on port 5008
# - vapshelp-kb-builder: One-time KB builder
# - vapshelp-ollama: Ollama service
# - vapshelp-ollama-model: Model downloader
```

**Rebuild Knowledge Base (Docker):**
```bash
# Stop and remove the builder container
docker compose rm -f vapshelp-kb

# Rebuild everything
docker compose up --build
```

**Access API:**
```bash
# Health check
curl http://localhost:5008/

# Chat endpoint
curl -X POST http://localhost:5008/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is VAPS?", "session_id": "user-1"}'
```

## Data Flow

### Query Processing - Pure RAG Pipeline
1. **Input**: User message via API or CLI
2. **Classification**: Route query into one of three paths:
   - **Small Talk** (greeting): Return friendly response immediately
   - **Direct Context** (user provides content): Process with LLM only (no retrieval)
   - **Standard Query** (information request): Full RAG pipeline
3. **Cache Check**: Look for exact or semantic match in cache
4. **Retrieval** (if needed): Perform hybrid search (vector + BM25)
5. **Context Building**: Prepare context window from retrieved documents
6. **LLM Processing**: Generate response using Groq LLM
7. **Cache Update**: Store answer with embedding for future hits
8. **Background Task**: Send conversation to external datastore (optional)
9. **Output**: Return response to user

### Hybrid Search Algorithm
- **Vector Search**: Semantic similarity via Chroma + Ollama embeddings (~50-100ms)
- **BM25 Search**: Keyword-based ranking via BM25 (~10-20ms)
- **Fusion**: Reciprocal rank fusion combines both result sets
- **Final Results**: Top K documents ranked by fused score
- **Ranking Formula**: RRF score = 1/(60 + rank)

### Cache System
- **Exact Match**: Direct lookup by normalized question hash
- **Semantic Match**: Cosine similarity with threshold of 0.90
- **Persistence**: JSON file in `data/cache/chat_cache.json`
- **Size Limit**: Max 200 entries, oldest entries removed when exceeded
- **Embeddings**: Questions stored with their embeddings for semantic lookup
- **Low-Confidence Bypass**: Cached answers with low confidence bypass retrieval

## Requirements

- Python 3.10+
- Ollama (with `embeddinggemma:300m` model)
- Groq API key
- See `requirements.txt` for Python dependencies

## Performance Notes

- Vector search: ~50-100ms
- BM25 search: ~10-20ms
- LLM inference: ~500-1500ms
- Cache hits: <1ms
- Typical total latency: 1-2 seconds

## Troubleshooting

### Vector DB not found
**Problem**: `data/chroma_db/` doesn't exist or is empty
```bash
# Solution: Rebuild from PDF
python scripts/build_kb.py
```

### Ollama connection error
**Problem**: Cannot connect to Ollama service
```bash
# Solution: Ensure Ollama is running
ollama serve

# Check if embeddinggemma model is downloaded
ollama list
```

### API won't start
**Problem**: `Address already in use` or API fails to start
```bash
# Check port 5008 is available
netstat -ano | findstr :5008  # Windows
lsof -i :5008  # macOS/Linux

# Verify GROQ_API_KEY is set
python -c "import os; print(os.getenv('GROQ_API_KEY'))"

# Check logs
tail -f data/logs/chat.log
```

### Knowledge Base is outdated
**Problem**: Want to rebuild with new/updated PDF
```bash
# Delete old vector DB
rm -rf data/chroma_db

# Rebuild
python scripts/build_kb.py
```

### Cache issues
**Problem**: Getting stale/incorrect cached responses
```bash
# Clear cache
rm data/cache/chat_cache.json

# Cache will rebuild automatically on next queries
```


"""FastAPI application and endpoints."""

import os
import threading
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq

load_dotenv()

from src.api.schemas import ChatRequest, ChatResponse
from src.api.admin import require_admin_access, router as admin_router
from src.admin.config_service import load_config
from src.admin.config_service import default_config
from src.config import (
    API_HOST,
    API_PORT,
    API_TITLE,
    CHAT_MODEL,
    ENABLE_DATASTORE_LOGGING,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    MAX_HISTORY_MESSAGES,
    MAX_SESSION_ENTRIES,
)
from src.core.rag import answer_question
from src.core.retrievers import load_bm25_index
from src.storage.cache import load_cache
from src.storage.datastore import save_conversation
from src.storage.vector_db import load_vector_store
from src.utils.logging import log_error, log_step

class BoundedSessionStore:
    """Thread-safe bounded in-memory session history store with LRU eviction."""

    def __init__(self, max_entries: int = MAX_SESSION_ENTRIES) -> None:
        self.max_entries = max_entries
        self._store: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
        self._lock = threading.Lock()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Retrieve a copy of conversation history for a given session."""
        with self._lock:
            if session_id in self._store:
                self._store.move_to_end(session_id)
                return list(self._store[session_id])
            return []

    def append_messages(self, session_id: str, user_message: str, ai_response: str) -> None:
        """Append messages to session history and enforce capacity limits."""
        with self._lock:
            history = self._store.get(session_id, [])
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": ai_response})
            if len(history) > MAX_HISTORY_MESSAGES:
                history = history[-MAX_HISTORY_MESSAGES:]
            self._store[session_id] = history
            self._store.move_to_end(session_id)
            if len(self._store) > self.max_entries:
                self._store.popitem(last=False)


session_store = BoundedSessionStore()


def _runtime_config():
    """Load admin settings while retaining startup safety if the file is invalid."""
    try:
        return load_config()
    except ValueError as exc:
        log_error("ADMIN_CONFIG_LOAD_FAILED", exc)
        return default_config()


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    log_step("SERVER_STARTING")
    app_instance.state.vector_db = load_vector_store()
    app_instance.state.bm25_index = load_bm25_index(app_instance.state.vector_db)
    from src.core.retrievers import create_ensemble_retriever
    runtime_config = _runtime_config()
    app_instance.state.ensemble_retriever = create_ensemble_retriever(
        app_instance.state.vector_db,
        app_instance.state.bm25_index,
        vector_top_k=runtime_config.rag.vector_top_k,
        bm25_top_k=runtime_config.rag.bm25_top_k,
        final_top_k=runtime_config.rag.final_top_k,
    )
    app_instance.state.llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model=runtime_config.models.primary_model,
        temperature=runtime_config.models.temperature,
        max_tokens=runtime_config.models.max_tokens,
        timeout=runtime_config.models.request_timeout,
    )
    app_instance.state.cache = load_cache()
    log_step("SERVER_READY", model=runtime_config.models.primary_model)
    yield
    log_step("SERVER_STOPPED")


# Initialize FastAPI app with lifespan
app = FastAPI(title=API_TITLE, lifespan=lifespan)
app.include_router(admin_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the chat UI static files
_STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


def _get_resources():
    """Ensure runtime resources are initialized even if lifespan wasn't triggered."""
    from src.core.retrievers import create_ensemble_retriever
    runtime_config = _runtime_config()

    if not hasattr(app.state, "vector_db") or app.state.vector_db is None:
        app.state.vector_db = load_vector_store()
    if not hasattr(app.state, "bm25_index") or app.state.bm25_index is None:
        app.state.bm25_index = load_bm25_index(app.state.vector_db)
    if not hasattr(app.state, "ensemble_retriever") or app.state.ensemble_retriever is None:
        app.state.ensemble_retriever = create_ensemble_retriever(
            app.state.vector_db,
            app.state.bm25_index,
            vector_top_k=runtime_config.rag.vector_top_k,
            bm25_top_k=runtime_config.rag.bm25_top_k,
            final_top_k=runtime_config.rag.final_top_k,
        )
    if not hasattr(app.state, "llm") or app.state.llm is None:
        app.state.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model=runtime_config.models.primary_model,
            temperature=runtime_config.models.temperature,
            max_tokens=runtime_config.models.max_tokens,
            timeout=runtime_config.models.request_timeout,
        )
    if not hasattr(app.state, "cache") or app.state.cache is None:
        app.state.cache = load_cache()
    return (
        app.state.vector_db,
        app.state.bm25_index,
        app.state.llm,
        app.state.cache,
        app.state.ensemble_retriever,
    )


@app.get("/")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/chat", include_in_schema=False)
def chat_ui() -> FileResponse:
    """Serve the chat UI HTML page."""
    return FileResponse(str(_STATIC_DIR / "index.html"))


@app.get("/admin", include_in_schema=False, dependencies=[Depends(require_admin_access)])
def admin_ui() -> FileResponse:
    """Serve the internal AI Control Center UI."""
    return FileResponse(str(_STATIC_DIR / "admin.html"))


@app.post("/webhook/chat", response_model=ChatResponse)
def webhook_chat(payload: ChatRequest, background_tasks: BackgroundTasks) -> ChatResponse:
    """
    Main chat webhook endpoint.

    Args:
        payload: Chat request with message and optional session_id
        background_tasks: Background task queue

    Returns:
        Chat response with session_id and answer

    Raises:
        HTTPException: If message is empty or processing fails
    """
    message = payload.message.strip()
    session_id = payload.session_id.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    vector_db, bm25_index, llm, cache, ensemble_retriever = _get_resources()
    chat_history = session_store.get_history(session_id)

    try:
        total_start = time.perf_counter()
        log_step("QUERY_START", query=message, session_id=session_id)
        log_step("USER_MESSAGE", text=message, session_id=session_id)

        answer = answer_question(
            vector_db=vector_db,
            bm25_index=bm25_index,
            llm=llm,
            cache=cache,
            chat_history=chat_history,
            question=message,
            ensemble_retriever=ensemble_retriever,
        )
        session_store.append_messages(session_id, message, answer)

        log_step("BOT_MESSAGE", text=answer, session_id=session_id)

        if ENABLE_DATASTORE_LOGGING:
            background_tasks.add_task(save_conversation, session_id, message, answer)

        total_latency_ms = int((time.perf_counter() - total_start) * 1000)
        log_step("TOTAL", latency=f"{total_latency_ms}ms", session_id=session_id)
        return ChatResponse(session_id=session_id, answer=answer)
    except HTTPException:
        raise
    except Exception as exc:
        log_error("API_ERROR", exc, session_id=session_id, message=message)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request.",
        ) from exc


def run(host: str = API_HOST, port: int = API_PORT, reload: bool = True) -> None:
    """
    Run the FastAPI server.

    Args:
        host: Server host
        port: Server port
        reload: Enable auto-reload
    """
    import uvicorn
    uvicorn.run("src.api.app:app", host=host, port=port, reload=reload)

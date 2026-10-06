"""Configuration and constants for VAPSAI chatbot."""

import os
import re
from pathlib import Path

# ============================================================================
# Directory and File Paths
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIRECTORY = BASE_DIR / "data/chroma_db"
CACHE_FILE = BASE_DIR / "data/cache/chat_cache.json"
BM25_CACHE_FILE = BASE_DIR / "data/cache/bm25_index.pkl"
LOG_DIR = BASE_DIR / "data/logs"
LOG_FILE = LOG_DIR / "chat.log"
ADMIN_CONFIG_FILE = BASE_DIR / "data/admin_config.json"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_SESSION_TTL_SECONDS = 300
ADMIN_COOKIE_SECURE = os.getenv("ADMIN_COOKIE_SECURE", "false").lower() == "true"

# ============================================================================
# Model and Embedding Configuration
# ============================================================================

EMBEDDING_MODEL = "embeddinggemma:latest"
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
COLLECTION_NAME = "VAPS_Group_KB"
CHAT_MODEL = "openai/gpt-oss-20b"
# ============================================================================
# Retrieval Parameters
# ============================================================================

VECTOR_TOP_K = 4
BM25_TOP_K = 4
FINAL_TOP_K = 6
MAX_CONTEXT_CHARS = 3500

# ============================================================================
# Chat and Cache Configuration
# ============================================================================

MAX_HISTORY_MESSAGES = 6
MAX_HISTORY_CHARS = 4000
MAX_HISTORY_MESSAGE_CHARS = 1600
MAX_SESSION_ENTRIES = 1000
CACHE_VERSION = 2
MAX_CACHE_ENTRIES = 200
SEMANTIC_CACHE_THRESHOLD = 0.82

# ============================================================================
# Regex Patterns
# ============================================================================

TOKEN_PATTERN = re.compile(r"\b\w+\b")
GREETING_PATTERN = re.compile(r"^(hi|hello|hey|good morning|good afternoon|good evening)\b")
TIME_QUERY_PATTERN = re.compile(
    r"\b(what(?:'s| is)? the time|what time is it|current time|time now|tell me the time)\b"
)
CHAT_TIMEZONE = os.getenv("CHAT_TIMEZONE", "Asia/Kolkata")
TIME_DISPLAY_FORMAT = "%A, %d %B %Y at %I:%M:%S %p"

# ============================================================================
# Prompt Hints
# ============================================================================

DIRECT_CONTENT_HINTS = (
    "base the questions on the following content",
    "return only the json",
    "use this exact json structure",
    "following content:",
)

# ============================================================================
# Helper Functions
# ============================================================================

def normalize_question(question: str) -> str:
    """Normalize a question by lowercasing and collapsing whitespace."""
    return " ".join(question.lower().split())

# ============================================================================
# API Configuration
# ============================================================================

API_HOST = "0.0.0.0"
API_PORT = 5008
API_TITLE = "AI Chatbot API"

# ============================================================================
# LLM Configuration
# ============================================================================

LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE_CHAT = 0.7

# ============================================================================
# External Datastore Configuration
# ============================================================================

ENABLE_DATASTORE_LOGGING = os.getenv("ENABLE_DATASTORE_LOGGING", "false").lower() == "true"
DATASTORE_URL = "https://vmsstaging.vapssmartecampus.com:40015/api/ISMDashboardFacade/Save_AI_ChatBot_Conversation/"
DATASTORE_TIMEOUT = 10
DATASTORE_WEBSITE_NAME = "Vaps"
DATASTORE_WEBSITE_URL = "https://vapstech.com/"
DATASTORE_USER_AGENT = "VAPSChatbot/1.0"
DATASTORE_VERIFY_SSL = os.getenv("DATASTORE_VERIFY_SSL", "false").lower() == "true"

# ============================================================================
# PDF Configuration
# ============================================================================

PDF_PATH = BASE_DIR / "KB_PDF/VMS_IssueManager_Chatbot_KnowledgeBase.pdf"
PDF_CHUNK_SIZE = 500
PDF_CHUNK_OVERLAP = 80

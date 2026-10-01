"""Configuration and constants for VAPSAI chatbot."""

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

# ============================================================================
# Model and Embedding Configuration
# ============================================================================

EMBEDDING_MODEL = "embeddinggemma:300m"
COLLECTION_NAME = "VAPS_Group_KB"
CHAT_MODEL = "meta-llama/llama-prompt-guard-2-86m"

# ============================================================================
# Retrieval Parameters
# ============================================================================

VECTOR_TOP_K = 2
BM25_TOP_K = 2
FINAL_TOP_K = 3
MAX_CONTEXT_CHARS = 1800

# ============================================================================
# Chat and Cache Configuration
# ============================================================================

MAX_HISTORY_MESSAGES = 6
CACHE_VERSION = 2
MAX_CACHE_ENTRIES = 200
SEMANTIC_CACHE_THRESHOLD = 0.90

# ============================================================================
# Regex Patterns
# ============================================================================

TOKEN_PATTERN = re.compile(r"\b\w+\b")
GREETING_PATTERN = re.compile(r"^(hi|hello|hey|good morning|good afternoon|good evening)\b")

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
LLM_MAX_TOKENS = 160
LLM_TEMPERATURE_CHAT = 0.7

# ============================================================================
# External Datastore Configuration
# ============================================================================

DATASTORE_URL = "https://vmsstaging.vapssmartecampus.com:40015/api/ISMDashboardFacade/Save_AI_ChatBot_Conversation/"
DATASTORE_TIMEOUT = 10
DATASTORE_WEBSITE_NAME = "Vaps"
DATASTORE_WEBSITE_URL = "https://vapstech.com/"
DATASTORE_USER_AGENT = "VAPSChatbot/1.0"

# ============================================================================
# PDF Configuration
# ============================================================================

PDF_PATH = BASE_DIR / "KB_PDF/VMS_IssueManager_Chatbot_KnowledgeBase.pdf"
PDF_CHUNK_SIZE = 500
PDF_CHUNK_OVERLAP = 80

# Contact information (update with real VAPS contact number)
VAPS_CONTACT_NUMBER = "08068112975"
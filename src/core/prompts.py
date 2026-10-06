"""Prompt building utilities for the chatbot using LangChain templates."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from src.config import (
    DIRECT_CONTENT_HINTS,
    GREETING_PATTERN,
    MAX_HISTORY_MESSAGES,
    normalize_question,
)


def to_langchain_messages(chat_history: list[dict[str, str]] | None) -> list[BaseMessage]:
    """
    Convert a list of role/content dictionaries into native LangChain BaseMessage objects.

    Args:
        chat_history: List of message dictionaries with 'role' and 'content'

    Returns:
        List of HumanMessage and AIMessage objects
    """
    if not chat_history:
        return []

    messages: list[BaseMessage] = []
    for item in chat_history[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role", "").lower()
        content = item.get("content", "")
        if role in ("user", "human"):
            messages.append(HumanMessage(content=content))
        elif role in ("assistant", "ai", "bot"):
            messages.append(AIMessage(content=content))
    return messages


def format_history(chat_history: list[dict[str, str]]) -> str:
    """
    Format chat history for legacy string-based inclusion in prompts.

    Args:
        chat_history: List of message dictionaries with 'role' and 'content'

    Returns:
        Formatted conversation string
    """
    if not chat_history:
        return "No prior conversation."

    lines = []
    for message in chat_history[-MAX_HISTORY_MESSAGES:]:
        role = message.get("role", "User").capitalize()
        lines.append(f"{role}: {message.get('content', '')}")
    return "\n".join(lines)


def classify_query(question: str) -> str:
    """
    Classify a query into one of three categories:
    - small_talk: Greeting or casual message
    - direct_context: User provides content or asks for structured output
    - retrieval: Standard question requiring knowledge base lookup

    Args:
        question: User question

    Returns:
        Query classification string
    """
    normalized_question = normalize_question(question)
    if GREETING_PATTERN.match(normalized_question):
        return "small_talk"
    if any(hint in normalized_question for hint in DIRECT_CONTENT_HINTS):
        return "direct_context"
    if len(question) > 1200:
        return "direct_context"
    return "retrieval"


# System instructions for VMS IssueManager RAG assistant
SYSTEM_RAG_INSTRUCTIONS = (
    "You are a knowledgeable and helpful assistant for the VMS IssueManager platform.\n"
    "Your role is to answer user questions accurately and comprehensively using the provided knowledge base.\n"
    "Use the conversation history to understand follow-up questions and maintain context.\n\n"
    "Rules:\n"
    "- Answer ONLY from the provided Context. Be thorough — if the context has troubleshooting steps, features, configuration details, or best practices, share them fully.\n"
    "- If the user has a technical issue, provide clear step-by-step guidance using the context.\n"
    "- Be helpful and professional when responding to all queries.\n"
    "- If the question is casual or a greeting, respond in a friendly manner.\n"
    '- If the answer is not in the context, simply state: "I don\'t have information about that in the VMS knowledge base. Please provide more details or rephrase your question."\n'
    "- Just focus on answering the question."
)

SYSTEM_DIRECT_INSTRUCTIONS = (
    "You are a helpful assistant for the VMS IssueManager platform.\n"
    "The user may provide full technical details, error messages, or documentation directly inside the request.\n"
    "When that happens, answer from the user-provided content to help resolve their issue or answer their question.\n\n"
    "Rules:\n"
    "- Answer the user's question fully and clearly first.\n"
    "- Provide step-by-step solutions for technical issues when applicable.\n"
    "- Be professional and helpful in your responses.\n"
    "- Do not ask for contact information - just focus on answering the question.\n"
    "- If you cannot fully answer from the provided information, suggest what additional details would help you assist better."
)

# LangChain ChatPromptTemplates
QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(SYSTEM_RAG_INSTRUCTIONS),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate.from_template("Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"),
    ]
)

DIRECT_CONTEXT_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(SYSTEM_DIRECT_INSTRUCTIONS),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate.from_template("User request:\n{question}\n\nAnswer:"),
    ]
)


def build_prompt(question: str, context: str, history: str) -> str:
    """Backward-compatible helper returning a raw formatted prompt string."""
    return f"""{SYSTEM_RAG_INSTRUCTIONS}

Conversation:
{history}
Context:
{context}
Question:
{question}
Answer:"""


def build_direct_context_prompt(question: str, history: str) -> str:
    """Backward-compatible helper returning a raw formatted direct prompt string."""
    return f"""{SYSTEM_DIRECT_INSTRUCTIONS}

Conversation:
{history}
User request:
{question}
Answer:"""

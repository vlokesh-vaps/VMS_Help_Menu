"""Prompt building utilities for the chatbot."""

from src.config import (DIRECT_CONTENT_HINTS,GREETING_PATTERN,MAX_HISTORY_MESSAGES,VAPS_CONTACT_NUMBER,normalize_question)

# Removed lead capture - this is a pure RAG bot focused on answering questions


def format_history(chat_history: list[dict[str, str]]) -> str:
    """
    Format chat history for inclusion in prompts.
    
    Args:
        chat_history: List of message dictionaries with 'role' and 'content'
        
    Returns:
        Formatted conversation string
    """
    if not chat_history:
        return "No prior conversation."

    lines = []
    for message in chat_history[-MAX_HISTORY_MESSAGES:]:
        role = message["role"].capitalize()
        lines.append(f"{role}: {message['content']}")
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


def build_prompt(question: str, context: str, history: str) -> str:
    """
    Build the main Q&A prompt for the LLM.
    
    Args:
        question: User question
        context: Retrieved context from knowledge base
        history: Formatted chat history
        
    Returns:
        Complete prompt for the LLM
    """
    return f"""You are a knowledgeable and helpful assistant for the VMS IssueManager platform.
Your role is to answer user questions accurately and comprehensively using the provided knowledge base.
Use the conversation history to understand follow-up questions and maintain context.

Your primary job is to answer questions accurately using the provided Context.
Always answer the user's question first and completely before anything else.

Rules:
- Answer ONLY from the provided Context. Be thorough — if the context has troubleshooting steps, features, configuration details, or best practices, share them fully.
- If the user has a technical issue, provide clear step-by-step guidance using the context.
- Be helpful and professional when responding to all queries.
- If the question is casual or a greeting, respond in a friendly manner.
- If the answer is not in the context, simply state: "I don't have information about that in the VMS IssueManager knowledge base. Please provide more details or rephrase your question."
- Do not ask for name, phone number, or contact information - just focus on answering the question.

Conversation:
{history}
Context:
{context}
Question:
{question}
Answer:"""


def build_direct_context_prompt(question: str, history: str) -> str:
    """
    Build a specialized prompt for direct context or structured output requests.

    Args:
        question: User question
        history: Formatted chat history

    Returns:
        Complete prompt for the LLM
    """
    return f"""You are a helpful assistant for the VMS IssueManager platform.
The user may provide full technical details, error messages, or documentation directly inside the request.
When that happens, answer from the user-provided content to help resolve their issue or answer their question.

Rules:
- Answer the user's question fully and clearly first.
- Provide step-by-step solutions for technical issues when applicable.
- Be professional and helpful in your responses.
- Do not ask for name, phone number, or contact information - just focus on answering the question.
- If you cannot fully answer from the provided information, suggest what additional details would help you assist better.

Conversation:
{history}
User request:
{question}
Answer:"""

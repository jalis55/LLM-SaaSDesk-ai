
from langchain_groq import ChatGroq

from app.core.config import AI_MODEL


def get_llm() -> ChatGroq:
    """Initialize the Groq language model."""

    return ChatGroq(
        model=AI_MODEL,
        temperature=0,
        max_retries=2,
    )

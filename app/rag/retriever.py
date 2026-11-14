
from langchain_core.documents import Document

from app.vectorstore.chroma_store import get_vector_store


def retrieve_documents(
    query: str,
    k: int = 3,
) -> list[Document]:
    """Retrieve the k most relevant chunks for a query."""

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query=query,
        k=k,
    )

def retrieve_documents_with_scores(
    query: str,
    k: int = 3,
) -> list[tuple[Document, float]]:
    """Retrieve relevant chunks with ChromaDB distance scores."""

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    vector_store = get_vector_store()

    return vector_store.similarity_search_with_score(
        query=query,
        k=k,
    )

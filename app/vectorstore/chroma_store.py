
from langchain_chroma import Chroma
import hashlib

from langchain_core.documents import Document

from app.ingestion.loader import clean_metadata

from app.core.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
)
from app.embeddings.model import get_embedding_model
from functools import lru_cache



@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """Initialize a persistent ChromaDB vector store."""

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DIR),
    )

    return vector_store







def generate_chunk_id(chunk: Document) -> str:
    """Generate a deterministic ID for a document chunk."""

    source = chunk.metadata.get("source", "")
    page = chunk.metadata.get("page", "")
    content = chunk.page_content

    raw_id = f"{source}:{page}:{content}"

    return hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()


def add_documents_to_store(
    vector_store: Chroma,
    chunks: list[Document],
) -> list[str]:
    """Insert chunks with stable IDs into ChromaDB."""

    cleaned_chunks = clean_metadata(chunks)

    ids = [
        generate_chunk_id(chunk)
        for chunk in cleaned_chunks
    ]

    if cleaned_chunks:
        vector_store.add_documents(
            documents=cleaned_chunks,
            ids=ids,
        )

    return ids

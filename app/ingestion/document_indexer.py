
from pathlib import Path

from app.core.config import DOCS_DIR
from app.ingestion.chunker import split_documents
from app.ingestion.loader import clean_metadata, load_document
from app.vectorstore.chroma_store import (
    add_documents_to_store,
    generate_chunk_id,
    get_vector_store,
)


def index_document(path: Path) -> int:
    """
    Load, chunk, and index one knowledge base document.

    Returns the number of generated chunks.
    """

    path = Path(path).resolve()
    docs_root = DOCS_DIR.resolve()

    if not path.is_relative_to(docs_root):
        raise ValueError(
            "Document must be inside the knowledge base directory."
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"Document not found: {path.name}"
        )

    documents = load_document(path)

    if not documents:
        raise ValueError(
            "The document contains no readable content."
        )

    chunks = split_documents(
        documents,
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = [
        chunk
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    if not chunks:
        raise ValueError(
            "No indexable text was found in the document."
        )

    chunks = clean_metadata(chunks)

    vector_store = get_vector_store()

    chunk_ids = [
        generate_chunk_id(chunk)
        for chunk in chunks
    ]

    existing_records = vector_store.get(
        ids=chunk_ids
    )

    existing_ids = set(existing_records["ids"])

    new_ids = [
        chunk_id
        for chunk_id in chunk_ids
        if chunk_id not in existing_ids
    ]

    try:
        add_documents_to_store(
            vector_store=vector_store,
            chunks=chunks,
        )

    except Exception:
        if new_ids:
            try:
                vector_store.delete(ids=new_ids)
            except Exception:
                pass

        raise

    return len(chunks)

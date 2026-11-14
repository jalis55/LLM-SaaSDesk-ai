
from pathlib import Path

from app.core.config import DOCS_DIR
from app.vectorstore.chroma_store import get_vector_store


class DocumentDeletionError(Exception):
    """Raised when a document cannot be deleted safely."""


def delete_document(
    path: Path,
    directory: Path = DOCS_DIR,
    vector_store=None,
) -> int:
    """
    Delete a source document and its indexed chunks.

    Returns the number of ChromaDB records removed.
    """

    directory = directory.resolve()
    path = path.resolve()

    # Prevent deletion outside the knowledge base.
    if not path.is_relative_to(directory):
        raise DocumentDeletionError(
            "Document is outside the knowledge base directory."
        )

    if not path.is_file():
        raise DocumentDeletionError(
            "Document does not exist."
        )

    if path.suffix.lower() not in {".pdf", ".md", ".txt"}:
        raise DocumentDeletionError(
            "Unsupported document type."
        )

    store = vector_store or get_vector_store()

    # Existing ingestion uses the document's source path
    # as part of its metadata.
    records = store.get(
        where={"source": str(path)}
    )

    chunk_ids = records["ids"]

    # Remove indexed chunks first.
    if chunk_ids:
        try:
            store.delete(ids=chunk_ids)
        except Exception as exc:
            raise DocumentDeletionError(
                "Failed to remove document embeddings."
            ) from exc

        # Verify that no matching records remain.
        remaining = store.get(
            where={"source": str(path)}
        )

        if remaining["ids"]:
            raise DocumentDeletionError(
                "Some indexed chunks remain. "
                "The source document was not deleted."
            )

    # Remove the original document.
    try:
        path.unlink()
    except OSError as exc:
        raise DocumentDeletionError(
            "Embeddings were removed, but the source "
            "file could not be deleted."
        ) from exc

    return len(chunk_ids)

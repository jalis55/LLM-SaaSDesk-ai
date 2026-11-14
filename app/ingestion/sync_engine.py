
import logging
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.documents import Document

from app.core.config import DOCS_DIR
from app.ingestion.chunker import split_documents
from app.ingestion.loader import clean_metadata, load_document
from app.ingestion.sync_scanner import scan_knowledge_base
from app.vectorstore.chroma_store import (
    generate_chunk_id,
    get_vector_store,
)


logger = logging.getLogger(__name__)


# ============================================================
# Synchronization Result
# ============================================================

@dataclass
class SyncResult:
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    chunks_added: int = 0
    chunks_removed: int = 0


# ============================================================
# Vector Store Helpers
# ============================================================

def get_source_records(store, source: str) -> dict:
    """
    Retrieve all indexed records for a source document.

    Include stored embeddings so rollback can restore
    existing vectors without regenerating embeddings.
    """

    return store.get(
        where={"source": source},
        include=[
            "documents",
            "metadatas",
            "embeddings",
        ],
    )


def restore_records(store, snapshot: dict) -> None:
    """
    Restore indexed records from a previous snapshot.

    Existing embeddings are reused.
    """

    ids = snapshot["ids"]

    if not ids:
        return

    store._collection.upsert(
        ids=ids,
        documents=snapshot["documents"],
        metadatas=snapshot["metadatas"],
        embeddings=snapshot["embeddings"],
    )


def verify_snapshot(
    store,
    source: str,
    snapshot: dict,
) -> bool:
    """
    Verify that the current records match the snapshot.

    Compares:
        - Record IDs
        - Document text
        - Metadata

    Embeddings are restored from the snapshot but are
    not compared element by element here.
    """

    current = get_source_records(store, source)

    expected = {
        chunk_id: (
            document,
            metadata,
        )
        for chunk_id, document, metadata in zip(
            snapshot["ids"],
            snapshot["documents"],
            snapshot["metadatas"],
        )
    }

    actual = {
        chunk_id: (
            document,
            metadata,
        )
        for chunk_id, document, metadata in zip(
            current["ids"],
            current["documents"],
            current["metadatas"],
        )
    }

    return actual == expected


# ============================================================
# Rollback
# ============================================================

def rollback_document_update(
    store,
    source: str,
    snapshot: dict,
) -> None:
    """
    Attempt to restore a document's previous indexed state.

    Recovery order:
        1. Restore original records.
        2. Remove newly created records.
        3. Verify restored content and metadata.

    Rollback is best-effort, not a database transaction.
    """

    original_ids = set(snapshot["ids"])
    rollback_errors = []

    # --------------------------------------------------------
    # Step 1: Restore original records first
    # --------------------------------------------------------

    try:
        restore_records(store, snapshot)

    except Exception as exc:
        logger.exception(
            "Failed to restore original records: %s",
            source,
        )

        rollback_errors.append(
            f"Original record restoration failed: {exc}"
        )

    # --------------------------------------------------------
    # Step 2: Remove newly added records
    # --------------------------------------------------------

    try:
        current = get_source_records(
            store,
            source,
        )

        current_ids = set(current["ids"])

        added_ids = sorted(
            current_ids - original_ids
        )

        if added_ids:
            store.delete(ids=added_ids)

    except Exception as exc:
        logger.exception(
            "Failed to remove new records during rollback: %s",
            source,
        )

        rollback_errors.append(
            f"New record cleanup failed: {exc}"
        )

    # --------------------------------------------------------
    # Step 3: Verify rollback
    # --------------------------------------------------------

    try:
        if not verify_snapshot(
            store,
            source,
            snapshot,
        ):
            rollback_errors.append(
                "Restored records do not match "
                "the original snapshot."
            )

    except Exception as exc:
        rollback_errors.append(
            f"Rollback verification failed: {exc}"
        )

    if rollback_errors:
        raise RuntimeError(
            "Rollback incomplete: "
            + "; ".join(rollback_errors)
        )


# ============================================================
# Document Processing
# ============================================================

def build_chunks(path: Path) -> dict[str, Document]:
    """
    Load and split a document into chunks.

    Returns a mapping:
        chunk_id -> Document
    """

    documents = load_document(path)

    if not documents:
        raise ValueError(
            "Document contains no readable content."
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
            "Document contains no indexable content."
        )

    chunks = clean_metadata(chunks)

    return {
        generate_chunk_id(chunk): chunk
        for chunk in chunks
    }


# ============================================================
# Synchronization Engine
# ============================================================

def sync_knowledge_base(
    directory: Path = DOCS_DIR,
    vector_store=None,
) -> SyncResult:
    """
    Synchronize knowledge base files with ChromaDB.

    Supports:
        - New documents
        - Modified documents
        - Deleted documents
        - Unchanged documents

    Uses best-effort rollback when an update fails.

    This function is not safe for concurrent execution.
    """

    directory = Path(directory).resolve()

    store = (
        vector_store
        if vector_store is not None
        else get_vector_store()
    )

    report = scan_knowledge_base(
        directory=directory,
        vector_store=store,
    )

    result = SyncResult(
        unchanged=report.unchanged_files.copy(),
        errors=report.errors.copy(),
    )

    # --------------------------------------------------------
    # Process New and Modified Documents
    # --------------------------------------------------------

    files_to_process = (
        report.new_files + report.modified_files
    )

    for filename in files_to_process:
        path = (directory / filename).resolve()

        try:
            if not path.is_relative_to(directory):
                raise ValueError(
                    "Document is outside the knowledge base."
                )

            if not path.is_file():
                raise FileNotFoundError(
                    "Source document no longer exists."
                )

            new_chunks = build_chunks(path)
            new_ids = set(new_chunks)

            source = str(path)

            # Snapshot existing indexed records.
            snapshot = get_source_records(
                store,
                source,
            )

            old_ids = set(snapshot["ids"])

            ids_to_add = sorted(
                new_ids - old_ids
            )

            ids_to_remove = sorted(
                old_ids - new_ids
            )

            # ------------------------------------------------
            # Apply changes
            # ------------------------------------------------

            try:
                if ids_to_add:
                    store.add_documents(
                        documents=[
                            new_chunks[chunk_id]
                            for chunk_id in ids_to_add
                        ],
                        ids=ids_to_add,
                    )

                # Verify new records before deleting old ones.
                if ids_to_add:
                    added_records = store.get(
                        ids=ids_to_add
                    )

                    missing_ids = (
                        set(ids_to_add)
                        - set(added_records["ids"])
                    )

                    if missing_ids:
                        raise RuntimeError(
                            "Some newly indexed chunks are missing."
                        )

                if ids_to_remove:
                    store.delete(
                        ids=ids_to_remove
                    )

                final = get_source_records(
                    store,
                    source,
                )

                if set(final["ids"]) != new_ids:
                    raise RuntimeError(
                        "Final indexed records do not match "
                        "the source document."
                    )

            except Exception as update_error:
                logger.exception(
                    "Synchronization failed; attempting "
                    "rollback: %s",
                    filename,
                )

                try:
                    rollback_document_update(
                        store,
                        source,
                        snapshot,
                    )

                except Exception as rollback_error:
                    raise RuntimeError(
                        f"Update failed: {update_error}. "
                        f"Rollback also failed: {rollback_error}"
                    ) from rollback_error

                raise

            result.chunks_added += len(ids_to_add)
            result.chunks_removed += len(ids_to_remove)

            if filename in report.new_files:
                result.added.append(filename)
            else:
                result.updated.append(filename)

        except Exception as exc:
            logger.exception(
                "Failed to synchronize document: %s",
                filename,
            )

            result.errors.append(
                f"{filename}: {exc}"
            )

    # --------------------------------------------------------
    # Remove Orphaned Indexed Documents
    # --------------------------------------------------------

    for filename in report.deleted_files:
        path = (directory / filename).resolve()

        try:
            if not path.is_relative_to(directory):
                raise ValueError(
                    "Document is outside the knowledge base."
                )

            if path.exists():
                raise RuntimeError(
                    "Source file reappeared during synchronization."
                )

            source = str(path)

            snapshot = get_source_records(
                store,
                source,
            )

            old_ids = snapshot["ids"]

            try:
                if old_ids:
                    store.delete(ids=old_ids)

                remaining = get_source_records(
                    store,
                    source,
                )

                if remaining["ids"]:
                    raise RuntimeError(
                        "Orphaned indexed chunks remain."
                    )

            except Exception as deletion_error:
                logger.exception(
                    "Orphan cleanup failed: %s",
                    filename,
                )

                try:
                    restore_records(
                        store,
                        snapshot,
                    )

                    if not verify_snapshot(
                        store,
                        source,
                        snapshot,
                    ):
                        raise RuntimeError(
                            "Restored orphan records "
                            "do not match the snapshot."
                        )

                except Exception as rollback_error:
                    raise RuntimeError(
                        f"Orphan cleanup failed: {deletion_error}. "
                        f"Recovery failed: {rollback_error}"
                    ) from rollback_error

                raise

            result.removed.append(filename)
            result.chunks_removed += len(old_ids)

        except Exception as exc:
            logger.exception(
                "Failed to remove orphaned records: %s",
                filename,
            )

            result.errors.append(
                f"{filename}: {exc}"
            )

    return result

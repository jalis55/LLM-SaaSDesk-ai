
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import DOCS_DIR
from app.ingestion.chunker import split_documents
from app.ingestion.loader import clean_metadata, load_document
from app.vectorstore.chroma_store import (
    generate_chunk_id,
    get_vector_store,
)


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


@dataclass
class SyncReport:
    new_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    unchanged_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def scan_knowledge_base(
    directory: Path = DOCS_DIR,
    vector_store=None,
) -> SyncReport:
    """
    Compare source documents against indexed ChromaDB records.

    This function is read-only.
    It does not modify files or vector records.
    """

    directory = Path(directory).resolve()

    store = (
        vector_store
        if vector_store is not None
        else get_vector_store()
    )

    report = SyncReport()

    # --------------------------------------------------------
    # Collect source documents
    # --------------------------------------------------------

    source_files = {}

    if directory.exists():
        for path in directory.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                resolved_path = path.resolve()

                # Ignore links resolving outside the directory.
                if not resolved_path.is_relative_to(directory):
                    continue

                source_files[str(resolved_path)] = resolved_path

    # --------------------------------------------------------
    # Collect indexed document records
    # --------------------------------------------------------

    records = store.get(include=["metadatas"])

    indexed_files = {}

    for chunk_id, metadata in zip(
        records["ids"],
        records["metadatas"],
    ):
        if not metadata:
            continue

        source = metadata.get("source")

        if not source:
            continue

        source_path = Path(source)

        if not source_path.is_absolute():
            source_path = directory / source_path

        source_path = source_path.resolve()

        # Only manage documents belonging to this directory.
        if not source_path.is_relative_to(directory):
            continue

        source_key = str(source_path)

        indexed_files.setdefault(
            source_key,
            set(),
        ).add(chunk_id)

    # --------------------------------------------------------
    # Compare disk files with ChromaDB
    # --------------------------------------------------------

    for source_key, path in sorted(source_files.items()):
        display_name = str(path.relative_to(directory))

        existing_ids = indexed_files.get(source_key)

        if not existing_ids:
            report.new_files.append(display_name)
            continue

        try:
            documents = load_document(path)

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

            chunks = clean_metadata(chunks)

            expected_ids = {
                generate_chunk_id(chunk)
                for chunk in chunks
            }

            if expected_ids == existing_ids:
                report.unchanged_files.append(display_name)
            else:
                report.modified_files.append(display_name)

        except Exception as exc:
            report.errors.append(
                f"{display_name}: {exc}"
            )

    # --------------------------------------------------------
    # Find orphaned indexed documents
    # --------------------------------------------------------

    for source_key in sorted(indexed_files):
        if source_key not in source_files:
            source_path = Path(source_key)

            display_name = str(
                source_path.relative_to(directory)
            )

            report.deleted_files.append(display_name)

    return report

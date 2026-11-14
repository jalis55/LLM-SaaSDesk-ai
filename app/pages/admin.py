
import logging
from pathlib import Path

import streamlit as st

from app.core.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    DOCS_DIR,
)
from app.ingestion.document_indexer import index_document
from app.ingestion.document_manager import (
    DocumentDeletionError,
    delete_document,
)
from app.ingestion.document_storage import (
    DocumentAlreadyExistsError,
    InvalidDocumentError,
    save_document,
)
from app.ingestion.sync_engine import sync_knowledge_base
from app.ingestion.sync_scanner import scan_knowledge_base
from app.ingestion.validator import validate_upload
from app.vectorstore.chroma_store import get_vector_store


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


# ============================================================
# Knowledge Base Helpers
# ============================================================

def get_source_documents() -> list[Path]:
    """Return supported source documents."""

    if not DOCS_DIR.exists():
        return []

    return sorted(
        (
            path
            for path in DOCS_DIR.rglob("*")
            if (
                path.is_file()
                and path.suffix.lower() in SUPPORTED_EXTENSIONS
                and path.resolve().is_relative_to(
                    DOCS_DIR.resolve()
                )
            )
        ),
        key=lambda path: str(path).lower(),
    )


def get_indexed_chunk_count() -> int:
    """Return the number of indexed ChromaDB chunks."""

    return get_vector_store()._collection.count()


def show_messages(messages: list[dict]) -> None:
    """Render stored success and error messages."""

    for item in messages:
        message = item["message"]

        if item["success"]:
            st.success(message)
        else:
            st.error(message)


# ============================================================
# Dashboard
# ============================================================

def render_dashboard() -> None:
    st.subheader("Knowledge Base Overview")

    documents = get_source_documents()

    try:
        chunk_count = get_indexed_chunk_count()

    except Exception:
        logger.exception(
            "Failed to read ChromaDB statistics."
        )
        chunk_count = None

    col1, col2 = st.columns(2)

    col1.metric(
        "Source Documents",
        len(documents),
    )

    col2.metric(
        "Indexed Chunks",
        (
            chunk_count
            if chunk_count is not None
            else "N/A"
        ),
    )

    st.subheader("Vector Database")

    st.write(
        "**Collection:**",
        CHROMA_COLLECTION,
    )

    st.write(
        "**Storage Directory:**",
        str(CHROMA_DIR),
    )

    if chunk_count is None:
        st.error(
            "Unable to read ChromaDB."
        )

    elif chunk_count == 0:
        st.info(
            "The vector database is empty."
        )

    else:
        st.success(
            f"ChromaDB contains "
            f"{chunk_count} indexed chunks."
        )


# ============================================================
# Upload Documents
# ============================================================

def render_upload_section() -> None:
    st.divider()

    st.subheader("Upload Documents")

    st.caption(
        "Supported formats: PDF, Markdown, TXT. "
        "Maximum size: 10 MiB per file."
    )

    if "kb_uploader_version" not in st.session_state:
        st.session_state.kb_uploader_version = 0

    upload_results = st.session_state.pop(
        "kb_upload_results",
        [],
    )

    show_messages(upload_results)

    uploaded_files = st.file_uploader(
        "Choose documents",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
        key=(
            "knowledge_base_uploader_"
            f"{st.session_state.kb_uploader_version}"
        ),
    )

    if not uploaded_files:
        return

    st.subheader(
        "Upload Validation Results"
    )

    existing_names = {
        path.name.casefold()
        for path in get_source_documents()
    }

    seen_filenames = set()

    valid_files = []
    rejected_count = 0

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        content = uploaded_file.getvalue()

        validation = validate_upload(
            filename=filename,
            content=content,
        )

        if not validation.is_valid:
            st.error(
                f"❌ {filename}: {validation.error}"
            )
            rejected_count += 1
            continue

        normalized_filename = filename.casefold()

        if normalized_filename in seen_filenames:
            st.error(
                f"❌ {filename}: Duplicate filename "
                "in upload batch."
            )
            rejected_count += 1
            continue

        seen_filenames.add(
            normalized_filename
        )

        if normalized_filename in existing_names:
            st.warning(
                f"⚠️ {filename}: A document with "
                "this filename already exists."
            )
            rejected_count += 1
            continue

        valid_files.append(
            (filename, content)
        )

        st.success(
            f"✅ {filename}: Ready to upload "
            f"({len(content) / 1024:.2f} KiB)"
        )

    col1, col2 = st.columns(2)

    col1.metric(
        "Valid Files",
        len(valid_files),
    )

    col2.metric(
        "Rejected Files",
        rejected_count,
    )

    if not valid_files:
        return

    st.info(
        "Valid documents will be saved and "
        "indexed automatically when you confirm."
    )

    if st.button(
        "Save and Index Documents",
        type="primary",
        use_container_width=True,
    ):
        results = []

        with st.spinner(
            "Processing documents..."
        ):
            for filename, content in valid_files:
                saved_path = None

                try:
                    saved_path = save_document(
                        filename=filename,
                        content=content,
                    )

                    chunk_count = index_document(
                        saved_path
                    )

                    results.append({
                        "success": True,
                        "message": (
                            f"✅ {filename}: Saved and "
                            "indexed successfully "
                            f"({chunk_count} chunks)."
                        ),
                    })

                except (
                    DocumentAlreadyExistsError,
                    InvalidDocumentError,
                ) as exc:
                    results.append({
                        "success": False,
                        "message": (
                            f"❌ {filename}: {exc}"
                        ),
                    })

                except Exception:
                    logger.exception(
                        "Document processing failed: %s",
                        filename,
                    )

                    message = (
                        f"❌ {filename}: Saved, but "
                        "indexing failed. The file "
                        "remains on disk."
                        if saved_path is not None
                        else (
                            f"❌ {filename}: "
                            "Upload failed."
                        )
                    )

                    results.append({
                        "success": False,
                        "message": message,
                    })

        st.session_state.kb_upload_results = results

        st.session_state.kb_uploader_version += 1

        st.rerun()


# ============================================================
# Document List
# ============================================================

def render_document_list() -> None:
    st.divider()

    st.subheader(
        "Available Documents"
    )

    documents = get_source_documents()

    if not documents:
        st.info(
            "No source documents found."
        )
        return

    rows = []

    for path in documents:
        relative_path = path.relative_to(
            DOCS_DIR
        )

        rows.append({
            "Filename": str(relative_path),
            "Type": (
                path.suffix.lower()
                .lstrip(".")
                .upper()
            ),
            "Size (KiB)": round(
                path.stat().st_size / 1024,
                2,
            ),
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Knowledge Base Synchronization
# ============================================================

def render_sync_section() -> None:
    st.divider()

    st.subheader(
        "Knowledge Base Synchronization"
    )

    st.caption(
        "Compare source documents with ChromaDB "
        "and synchronize detected changes."
    )

    st.info(
        "Scanning is read-only. No indexed records "
        "will be changed until you confirm."
    )

    # --------------------------------------------------------
    # Previous synchronization results
    # --------------------------------------------------------

    previous_result = st.session_state.pop(
        "kb_sync_result",
        None,
    )

    if previous_result is not None:
        st.subheader(
            "Last Synchronization Result"
        )

        if previous_result.errors:
            st.warning(
                "Synchronization completed with errors."
            )
        else:
            st.success(
                "Synchronization completed successfully."
            )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Added",
            len(previous_result.added),
        )

        col2.metric(
            "Updated",
            len(previous_result.updated),
        )

        col3.metric(
            "Removed",
            len(previous_result.removed),
        )

        col4.metric(
            "Unchanged",
            len(previous_result.unchanged),
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Chunks Added",
            previous_result.chunks_added,
        )

        col2.metric(
            "Chunks Removed",
            previous_result.chunks_removed,
        )

        if previous_result.errors:
            with st.expander(
                "Synchronization Errors",
                expanded=True,
            ):
                for error in previous_result.errors:
                    st.error(error)

    # --------------------------------------------------------
    # Scan Button
    # --------------------------------------------------------

    if st.button(
        "Scan Knowledge Base",
        key="kb_scan_button",
        use_container_width=True,
    ):
        # Invalidate any previous preview.
        st.session_state.pop(
            "kb_sync_preview",
            None,
        )

        st.session_state[
            "kb_sync_confirmed"
        ] = False

        try:
            with st.spinner(
                "Scanning source documents and "
                "indexed records..."
            ):
                report = scan_knowledge_base()

            st.session_state[
                "kb_sync_preview"
            ] = report

        except Exception:
            logger.exception(
                "Knowledge base scan failed."
            )

            st.error(
                "Unable to scan the knowledge base. "
                "Check application logs."
            )

    # --------------------------------------------------------
    # Preview
    # --------------------------------------------------------

    report = st.session_state.get(
        "kb_sync_preview"
    )

    if report is None:
        st.caption(
            "Click 'Scan Knowledge Base' "
            "to preview pending changes."
        )
        return

    st.subheader(
        "Synchronization Preview"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "New",
        len(report.new_files),
    )

    col2.metric(
        "Modified",
        len(report.modified_files),
    )

    col3.metric(
        "Deleted",
        len(report.deleted_files),
    )

    col4.metric(
        "Unchanged",
        len(report.unchanged_files),
    )

    # --------------------------------------------------------
    # Display detected files
    # --------------------------------------------------------

    if report.new_files:
        with st.expander(
            f"New Documents ({len(report.new_files)})",
            expanded=True,
        ):
            for filename in report.new_files:
                st.write(
                    f"➕ {filename}"
                )

    if report.modified_files:
        with st.expander(
            "Modified Documents "
            f"({len(report.modified_files)})",
            expanded=True,
        ):
            for filename in report.modified_files:
                st.write(
                    f"✏️ {filename}"
                )

    if report.deleted_files:
        with st.expander(
            "Deleted Source Documents "
            f"({len(report.deleted_files)})",
            expanded=True,
        ):
            for filename in report.deleted_files:
                st.write(
                    f"🗑️ {filename}"
                )

    if report.unchanged_files:
        with st.expander(
            "Unchanged Documents "
            f"({len(report.unchanged_files)})",
            expanded=False,
        ):
            for filename in report.unchanged_files:
                st.write(
                    f"✅ {filename}"
                )

    # --------------------------------------------------------
    # Scanner errors
    # --------------------------------------------------------

    if report.errors:
        st.error(
            "Some documents could not be scanned."
        )

        for error in report.errors:
            st.error(error)

        st.warning(
            "Resolve scanning errors before "
            "synchronizing the knowledge base."
        )

        return

    # --------------------------------------------------------
    # Check for pending changes
    # --------------------------------------------------------

    pending_count = (
        len(report.new_files)
        + len(report.modified_files)
        + len(report.deleted_files)
    )

    if pending_count == 0:
        st.success(
            "Knowledge base is already synchronized. "
            "No changes are required."
        )
        return

    st.warning(
        f"{pending_count} document(s) require "
        "synchronization."
    )

    if report.deleted_files:
        st.warning(
            "Deleted source documents will have "
            "their associated indexed chunks "
            "removed from ChromaDB."
        )

    # --------------------------------------------------------
    # Confirmation
    # --------------------------------------------------------

    confirmed = st.checkbox(
        "I have reviewed the detected changes "
        "and want to synchronize the knowledge base.",
        key="kb_sync_confirmed",
    )

    # --------------------------------------------------------
    # Execute Synchronization
    # --------------------------------------------------------

    if st.button(
        "Sync Knowledge Base",
        type="primary",
        disabled=not confirmed,
        use_container_width=True,
        key="kb_execute_sync",
    ):
        try:
            with st.spinner(
                "Synchronizing knowledge base..."
            ):
                result = sync_knowledge_base()

            st.session_state[
                "kb_sync_result"
            ] = result

        except Exception:
            logger.exception(
                "Knowledge base synchronization failed."
            )

            st.session_state[
                "kb_sync_result"
            ] = None

            st.error(
                "An unexpected synchronization error "
                "occurred. Check application logs."
            )

        finally:
            # Force a new scan before another operation.
            st.session_state.pop(
                "kb_sync_preview",
                None,
            )

            st.session_state[
                "kb_sync_confirmed"
            ] = False

        if result is not None if "result" in locals() else False:
            st.rerun()


# ============================================================
# Delete Document
# ============================================================

def render_delete_section() -> None:
    st.divider()

    st.subheader(
        "Delete Document"
    )

    st.warning(
        "Deleting a document permanently removes "
        "its source file and associated indexed chunks."
    )

    delete_results = st.session_state.pop(
        "kb_delete_results",
        [],
    )

    show_messages(delete_results)

    documents = get_source_documents()

    if not documents:
        st.info(
            "There are no documents to delete."
        )
        return

    document_options = {
        str(path.relative_to(DOCS_DIR)): path
        for path in documents
    }

    selected_name = st.selectbox(
        "Select a document to delete",
        options=list(document_options),
        index=None,
        placeholder="Choose a document",
        key="kb_delete_selection",
    )

    if selected_name is None:
        return

    selected_path = document_options[
        selected_name
    ]

    confirmed = st.checkbox(
        (
            "I understand that deleting "
            f"'{selected_name}' will remove "
            "its file and indexed chunks."
        ),
        key=f"kb_confirm_delete_{selected_name}",
    )

    if st.button(
        "Delete Selected Document",
        type="primary",
        disabled=not confirmed,
        use_container_width=True,
    ):
        try:
            with st.spinner(
                "Deleting document..."
            ):
                deleted_chunks = delete_document(
                    selected_path
                )

            st.session_state.kb_delete_results = [{
                "success": True,
                "message": (
                    f"✅ Deleted '{selected_name}' "
                    f"and {deleted_chunks} indexed chunks."
                ),
            }]

        except DocumentDeletionError as exc:
            st.session_state.kb_delete_results = [{
                "success": False,
                "message": f"❌ {exc}",
            }]

        except Exception:
            logger.exception(
                "Unexpected deletion failure: %s",
                selected_name,
            )

            st.session_state.kb_delete_results = [{
                "success": False,
                "message": (
                    "❌ Unexpected deletion error. "
                    "Check application logs."
                ),
            }]

        # Invalidate any existing sync preview.
        st.session_state.pop(
            "kb_sync_preview",
            None,
        )

        st.rerun()


# ============================================================
# Main Admin Page
# ============================================================

def render_admin_page() -> None:
    st.title(
        "Knowledge Base Management"
    )

    st.caption(
        "Manage and monitor FlowDesk "
        "knowledge base documents."
    )

    st.warning(
        "Development only: this page has no "
        "authentication. Do not expose it publicly."
    )

    render_dashboard()

    render_upload_section()

    render_document_list()

    render_sync_section()

    render_delete_section()


render_admin_page()

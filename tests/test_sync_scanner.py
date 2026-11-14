
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from app.ingestion.sync_scanner import scan_knowledge_base
from app.vectorstore.chroma_store import generate_chunk_id


def make_store(ids, metadatas):
    store = Mock()
    store.get.return_value = {
        "ids": ids,
        "metadatas": metadatas,
    }
    return store


def test_detect_new_document(tmp_path):
    path = tmp_path / "new.md"
    path.write_text("# New document")

    store = make_store([], [])

    report = scan_knowledge_base(
        directory=tmp_path,
        vector_store=store,
    )

    assert report.new_files == ["new.md"]
    assert report.modified_files == []
    assert report.deleted_files == []


def test_detect_deleted_document(tmp_path):
    missing_path = tmp_path / "deleted.md"

    store = make_store(
        ["chunk-1"],
        [{"source": str(missing_path)}],
    )

    report = scan_knowledge_base(
        directory=tmp_path,
        vector_store=store,
    )

    assert report.deleted_files == ["deleted.md"]


def test_detect_unchanged_document(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Policy")

    chunk = Document(
        page_content="# Policy",
        metadata={"source": str(path)},
    )

    chunk_id = generate_chunk_id(chunk)

    store = make_store(
        [chunk_id],
        [{"source": str(path)}],
    )

    with (
        patch(
            "app.ingestion.sync_scanner.load_document",
            return_value=[chunk],
        ),
        patch(
            "app.ingestion.sync_scanner.split_documents",
            return_value=[chunk],
        ),
    ):
        report = scan_knowledge_base(
            directory=tmp_path,
            vector_store=store,
        )

    assert report.unchanged_files == ["policy.md"]
    assert report.modified_files == []


def test_detect_modified_document(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Updated Policy")

    chunk = Document(
        page_content="# Updated Policy",
        metadata={"source": str(path)},
    )

    store = make_store(
        ["old-chunk-id"],
        [{"source": str(path)}],
    )

    with (
        patch(
            "app.ingestion.sync_scanner.load_document",
            return_value=[chunk],
        ),
        patch(
            "app.ingestion.sync_scanner.split_documents",
            return_value=[chunk],
        ),
    ):
        report = scan_knowledge_base(
            directory=tmp_path,
            vector_store=store,
        )

    assert report.modified_files == ["policy.md"]
    assert report.unchanged_files == []

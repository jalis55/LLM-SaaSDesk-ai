
from unittest.mock import patch

from langchain_core.documents import Document

from app.ingestion.sync_engine import sync_knowledge_base
from app.ingestion.sync_scanner import SyncReport
from app.vectorstore.chroma_store import generate_chunk_id


# ============================================================
# Fake ChromaDB Collection
# ============================================================

class FakeCollection:
    """
    Simulates ChromaDB's underlying collection.

    Supports restoring indexed records through upsert().
    """

    def __init__(self, store):
        self.store = store

    def upsert(
        self,
        ids,
        documents,
        metadatas,
        embeddings,
    ):
        for index, chunk_id in enumerate(ids):
            self.store.records[chunk_id] = Document(
                page_content=documents[index],
                metadata=metadatas[index],
            )


# ============================================================
# Fake Vector Store
# ============================================================

class FakeVectorStore:
    """
    In-memory vector store for synchronization tests.

    Failure modes:
        - Fail before adding records
        - Fail after partially adding records
        - Fail once after partially deleting records
    """

    def __init__(self):
        self.records = {}

        self.fail_add = False
        self.fail_after_partial_add = False
        self.fail_after_partial_delete = False

        self._collection = FakeCollection(self)

    def get(
        self,
        ids=None,
        where=None,
        include=None,
    ):
        if ids is not None:
            selected_ids = [
                chunk_id
                for chunk_id in ids
                if chunk_id in self.records
            ]

        elif where is not None:
            source = where["source"]

            selected_ids = [
                chunk_id
                for chunk_id, document
                in self.records.items()
                if document.metadata.get("source") == source
            ]

        else:
            selected_ids = list(self.records)

        return {
            "ids": selected_ids,
            "documents": [
                self.records[chunk_id].page_content
                for chunk_id in selected_ids
            ],
            "metadatas": [
                self.records[chunk_id].metadata
                for chunk_id in selected_ids
            ],
            "embeddings": [
                [0.1, 0.2, 0.3]
                for _ in selected_ids
            ],
        }

    def add_documents(
        self,
        documents,
        ids,
    ):
        if self.fail_add:
            raise RuntimeError(
                "Simulated embedding failure"
            )

        for index, (chunk_id, document) in enumerate(
            zip(ids, documents)
        ):
            self.records[chunk_id] = document

            if (
                self.fail_after_partial_add
                and index == 0
            ):
                raise RuntimeError(
                    "Simulated partial add failure"
                )

    def delete(self, ids):
        """
        Delete records.

        Partial deletion failure is simulated once.
        A subsequent deletion attempt can succeed.
        """

        for index, chunk_id in enumerate(ids):
            self.records.pop(
                chunk_id,
                None,
            )

            if (
                self.fail_after_partial_delete
                and index == 0
            ):
                self.fail_after_partial_delete = False

                raise RuntimeError(
                    "Simulated partial delete failure"
                )


# ============================================================
# Test Helpers
# ============================================================

def make_chunk(path, content):
    return Document(
        page_content=content,
        metadata={
            "source": str(path),
        },
    )


def run_sync_with_report(
    tmp_path,
    store,
    report,
    chunks=None,
):
    """
    Run synchronization with a mocked scanner.

    Optionally mock the generated document chunks.
    """

    with patch(
        "app.ingestion.sync_engine.scan_knowledge_base",
        return_value=report,
    ):
        if chunks is None:
            return sync_knowledge_base(
                directory=tmp_path,
                vector_store=store,
            )

        with patch(
            "app.ingestion.sync_engine.build_chunks",
            return_value=chunks,
        ):
            return sync_knowledge_base(
                directory=tmp_path,
                vector_store=store,
            )


# ============================================================
# Test 1: New Document
# ============================================================

def test_sync_new_document(tmp_path):
    path = tmp_path / "new.md"
    path.write_text("# New Policy")

    store = FakeVectorStore()

    chunk = make_chunk(
        path,
        "# New Policy",
    )

    chunk_id = generate_chunk_id(chunk)

    report = SyncReport(
        new_files=["new.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
        chunks={chunk_id: chunk},
    )

    assert result.added == ["new.md"]
    assert result.updated == []
    assert result.removed == []

    assert result.chunks_added == 1
    assert result.chunks_removed == 0

    assert chunk_id in store.records
    assert result.errors == []


# ============================================================
# Test 2: Modified Document
# ============================================================

def test_sync_modified_document(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Updated Policy")

    store = FakeVectorStore()

    old_chunk = make_chunk(
        path,
        "# Old Policy",
    )

    new_chunk = make_chunk(
        path,
        "# Updated Policy",
    )

    old_id = generate_chunk_id(old_chunk)
    new_id = generate_chunk_id(new_chunk)

    store.records[old_id] = old_chunk

    report = SyncReport(
        modified_files=["policy.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
        chunks={new_id: new_chunk},
    )

    assert result.updated == ["policy.md"]
    assert result.added == []

    assert result.chunks_added == 1
    assert result.chunks_removed == 1

    assert old_id not in store.records
    assert new_id in store.records

    assert result.errors == []


# ============================================================
# Test 3: Deleted Document
# ============================================================

def test_sync_deleted_document(tmp_path):
    path = tmp_path / "deleted.md"

    store = FakeVectorStore()

    old_chunk = make_chunk(
        path,
        "# Deleted Policy",
    )

    old_id = generate_chunk_id(old_chunk)

    store.records[old_id] = old_chunk

    report = SyncReport(
        deleted_files=["deleted.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
    )

    assert result.removed == ["deleted.md"]
    assert result.chunks_removed == 1

    assert old_id not in store.records
    assert store.records == {}

    assert result.errors == []


# ============================================================
# Test 4: Unchanged Document
# ============================================================

def test_sync_unchanged_document(tmp_path):
    store = FakeVectorStore()

    report = SyncReport(
        unchanged_files=["unchanged.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
    )

    assert result.unchanged == ["unchanged.md"]

    assert result.added == []
    assert result.updated == []
    assert result.removed == []

    assert result.chunks_added == 0
    assert result.chunks_removed == 0

    assert result.errors == []


# ============================================================
# Test 5: Embedding Failure
# ============================================================

def test_failed_update_preserves_old_chunks(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Updated Policy")

    store = FakeVectorStore()

    old_chunk = make_chunk(
        path,
        "# Old Policy",
    )

    new_chunk = make_chunk(
        path,
        "# Updated Policy",
    )

    old_id = generate_chunk_id(old_chunk)
    new_id = generate_chunk_id(new_chunk)

    store.records[old_id] = old_chunk

    store.fail_add = True

    report = SyncReport(
        modified_files=["policy.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
        chunks={new_id: new_chunk},
    )

    assert result.updated == []
    assert len(result.errors) == 1

    assert old_id in store.records
    assert new_id not in store.records

    assert result.chunks_added == 0
    assert result.chunks_removed == 0


# ============================================================
# Test 6: Partial Add Failure
# ============================================================

def test_partial_add_failure_rolls_back(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Updated Policy")

    store = FakeVectorStore()

    old_chunk = make_chunk(
        path,
        "# Old Policy",
    )

    new_chunk = make_chunk(
        path,
        "# Updated Policy",
    )

    old_id = generate_chunk_id(old_chunk)
    new_id = generate_chunk_id(new_chunk)

    store.records[old_id] = old_chunk

    store.fail_after_partial_add = True

    report = SyncReport(
        modified_files=["policy.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
        chunks={new_id: new_chunk},
    )

    assert result.updated == []
    assert len(result.errors) == 1

    assert old_id in store.records
    assert new_id not in store.records

    assert store.records[old_id].page_content == (
        "# Old Policy"
    )

    assert result.chunks_added == 0
    assert result.chunks_removed == 0


# ============================================================
# Test 7: Partial Delete Failure
# ============================================================

def test_partial_delete_failure_restores_old_records(
    tmp_path,
):
    path = tmp_path / "policy.md"
    path.write_text("# Updated Policy")

    store = FakeVectorStore()

    old_chunk = make_chunk(
        path,
        "# Old Policy",
    )

    new_chunk = make_chunk(
        path,
        "# Updated Policy",
    )

    old_id = generate_chunk_id(old_chunk)
    new_id = generate_chunk_id(new_chunk)

    store.records[old_id] = old_chunk

    # Simulate a one-time partial deletion failure.
    store.fail_after_partial_delete = True

    report = SyncReport(
        modified_files=["policy.md"]
    )

    result = run_sync_with_report(
        tmp_path,
        store,
        report,
        chunks={new_id: new_chunk},
    )

    assert result.updated == []
    assert len(result.errors) == 1

    # Original record must be restored.
    assert old_id in store.records

    # Newly added record must be removed.
    assert new_id not in store.records

    # Verify original content and metadata.
    restored_chunk = store.records[old_id]

    assert restored_chunk.page_content == (
        "# Old Policy"
    )

    assert restored_chunk.metadata == {
        "source": str(path),
    }

    assert result.chunks_added == 0
    assert result.chunks_removed == 0

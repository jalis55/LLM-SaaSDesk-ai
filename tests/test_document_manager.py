
from unittest.mock import Mock

import pytest

from app.ingestion.document_manager import (
    DocumentDeletionError,
    delete_document,
)


def test_delete_document_and_vectors(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Test Policy")

    store = Mock()

    store.get.side_effect = [
        {"ids": ["chunk-1", "chunk-2"]},
        {"ids": []},
    ]

    deleted_count = delete_document(
        path,
        directory=tmp_path,
        vector_store=store,
    )

    assert deleted_count == 2
    assert not path.exists()

    store.delete.assert_called_once_with(
        ids=["chunk-1", "chunk-2"]
    )


def test_delete_document_without_vectors(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Test Policy")

    store = Mock()
    store.get.return_value = {"ids": []}

    deleted_count = delete_document(
        path,
        directory=tmp_path,
        vector_store=store,
    )

    assert deleted_count == 0
    assert not path.exists()

    store.delete.assert_not_called()


def test_reject_path_outside_directory(tmp_path):
    directory = tmp_path / "documents"
    directory.mkdir()

    outside = tmp_path / "outside.md"
    outside.write_text("# Outside")

    with pytest.raises(DocumentDeletionError):
        delete_document(
            outside,
            directory=directory,
            vector_store=Mock(),
        )

    assert outside.exists()


def test_preserve_file_when_vector_deletion_fails(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Test Policy")

    store = Mock()
    store.get.return_value = {
        "ids": ["chunk-1"]
    }
    store.delete.side_effect = RuntimeError(
        "Database failure"
    )

    with pytest.raises(DocumentDeletionError):
        delete_document(
            path,
            directory=tmp_path,
            vector_store=store,
        )

    assert path.exists()

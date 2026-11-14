
import pytest

from app.ingestion.document_storage import (
    DocumentAlreadyExistsError,
    InvalidDocumentError,
    save_document,
)


def test_save_valid_document(tmp_path):
    content = b"# New Policy"

    saved_path = save_document(
        "new_policy.md",
        content,
        directory=tmp_path,
    )

    assert saved_path.exists()
    assert saved_path.read_bytes() == content


def test_reject_duplicate_document(tmp_path):
    save_document(
        "pricing.md",
        b"# Pricing",
        directory=tmp_path,
    )

    with pytest.raises(DocumentAlreadyExistsError):
        save_document(
            "pricing.md",
            b"# Updated Pricing",
            directory=tmp_path,
        )


def test_reject_case_insensitive_duplicate(tmp_path):
    save_document(
        "pricing.md",
        b"# Pricing",
        directory=tmp_path,
    )

    with pytest.raises(DocumentAlreadyExistsError):
        save_document(
            "Pricing.md",
            b"# Another Pricing",
            directory=tmp_path,
        )


def test_reject_invalid_document(tmp_path):
    with pytest.raises(InvalidDocumentError):
        save_document(
            "../config.md",
            b"Invalid path",
            directory=tmp_path,
        )


def test_reject_empty_document(tmp_path):
    with pytest.raises(InvalidDocumentError):
        save_document(
            "empty.txt",
            b"",
            directory=tmp_path,
        )

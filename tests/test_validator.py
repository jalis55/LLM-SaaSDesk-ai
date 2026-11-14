
from app.ingestion.validator import (
    MAX_FILE_SIZE,
    validate_upload,
)


def test_valid_markdown():
    result = validate_upload(
        "pricing.md",
        b"# FlowDesk Pricing",
    )
    assert result.is_valid


def test_valid_pdf_header():
    result = validate_upload(
        "guide.pdf",
        b"%PDF-1.7\nsample",
    )
    assert result.is_valid


def test_invalid_extension():
    result = validate_upload(
        "script.py",
        b"print('hello')",
    )
    assert not result.is_valid


def test_path_traversal():
    result = validate_upload(
        "../../config.md",
        b"malicious content",
    )
    assert not result.is_valid


def test_empty_file():
    result = validate_upload(
        "empty.txt",
        b"",
    )
    assert not result.is_valid


def test_oversized_file():
    result = validate_upload(
        "large.txt",
        b"x" * (MAX_FILE_SIZE + 1),
    )
    assert not result.is_valid


def test_invalid_utf8():
    result = validate_upload(
        "invalid.txt",
        b"\xff\xfe",
    )
    assert not result.is_valid


def test_invalid_pdf_header():
    result = validate_upload(
        "fake.pdf",
        b"not actually a PDF",
    )
    assert not result.is_valid

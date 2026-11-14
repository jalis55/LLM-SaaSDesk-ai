
from langchain_core.documents import Document

from app.ingestion.chunker import split_documents


def test_chunk_size_limit():
    document = Document(
        page_content="FlowDesk provides project management tools. " * 50,
        metadata={"filename": "features.md"},
    )

    chunks = split_documents(
        [document],
        chunk_size=500,
        chunk_overlap=100,
    )

    assert len(chunks) > 1

    assert all(
        len(chunk.page_content) <= 500
        for chunk in chunks
    )


def test_metadata_preserved():
    document = Document(
        page_content="FlowDesk pricing information. " * 50,
        metadata={
            "filename": "pricing.md",
            "file_type": ".md",
        },
    )

    chunks = split_documents(
        [document],
        chunk_size=500,
        chunk_overlap=100,
    )

    assert all(
        chunk.metadata["filename"] == "pricing.md"
        for chunk in chunks
    )

    assert all(
        chunk.metadata["file_type"] == ".md"
        for chunk in chunks
    )


def test_short_document_not_split():
    document = Document(
        page_content="FlowDesk offers a free plan.",
        metadata={"filename": "pricing.md"},
    )

    chunks = split_documents(
        [document],
        chunk_size=500,
        chunk_overlap=100,
    )

    assert len(chunks) == 1
    assert chunks[0].page_content == document.page_content

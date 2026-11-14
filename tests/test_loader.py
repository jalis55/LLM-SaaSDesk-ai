
from app.ingestion.loader import load_document
from app.ingestion.loader import clean_metadata
from langchain_core.documents import Document





def test_markdown_metadata(tmp_path):
    file = tmp_path / "pricing.md"
    file.write_text(
        "# Pricing\nPro plan costs $19/month.",
        encoding="utf-8",
    )

    documents = load_document(file)

    assert len(documents) == 1

    doc = documents[0]

    assert doc.metadata["filename"] == "pricing.md"
    assert doc.metadata["file_type"] == ".md"
    assert doc.metadata["page_number"] is None

    assert "Pro plan" in doc.page_content






def test_clean_metadata():
    documents = [
        Document(
            page_content="FlowDesk pricing.",
            metadata={
                "filename": "pricing.md",
                "page_number": None,
            },
        )
    ]

    cleaned = clean_metadata(documents)

    assert cleaned[0].metadata == {
        "filename": "pricing.md"
    }
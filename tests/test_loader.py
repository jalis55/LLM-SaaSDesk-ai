
from app.ingestion.loader import load_document


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

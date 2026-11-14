from app.core.config import AI_MODEL, DOCS_DIR


def test_sample_documents_exist():
    assert len(list(DOCS_DIR.glob("*.md"))) == 3


def test_default_model():
    assert AI_MODEL

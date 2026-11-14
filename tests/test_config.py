
from pathlib import Path

from app.core.config import (
    AI_MODEL,
    CHROMA_COLLECTION,
    CHROMA_DIR,
    DOCS_DIR,
    ROOT_DIR,
)


def test_project_root_exists():
    assert ROOT_DIR.exists()
    assert ROOT_DIR.is_dir()


def test_documents_directory_exists():
    assert DOCS_DIR.exists()
    assert DOCS_DIR.is_dir()


def test_documents_directory_inside_project():
    assert DOCS_DIR.resolve().is_relative_to(
        ROOT_DIR.resolve()
    )


def test_vector_database_directory_configured():
    assert isinstance(CHROMA_DIR, Path)
    assert CHROMA_DIR.resolve().is_relative_to(
        ROOT_DIR.resolve()
    )


def test_collection_name_configured():
    assert isinstance(CHROMA_COLLECTION, str)
    assert CHROMA_COLLECTION.strip()


def test_default_model():
    assert isinstance(AI_MODEL, str)
    assert AI_MODEL.strip()

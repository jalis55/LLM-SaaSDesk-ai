
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document


def standardize_metadata(documents: list[Document]) -> list[Document]:
    """Add consistent metadata to loaded documents."""

    for doc in documents:
        source_path = Path(doc.metadata["source"])

        doc.metadata["filename"] = source_path.name
        doc.metadata["file_type"] = source_path.suffix.lower()

        page = doc.metadata.get("page")

        if page is not None:
            doc.metadata["page_number"] = page + 1
        else:
            doc.metadata["page_number"] = None

    return documents


def load_document(file_path: str | Path) -> list[Document]:
    """Load a single Markdown, TXT, or PDF file."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in (".md", ".txt"):
        loader = TextLoader(
            file_path=str(path),
            encoding="utf-8",
        )

    elif extension == ".pdf":
        loader = PyPDFLoader(str(path))

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    documents = loader.load()

    return standardize_metadata(documents)


def load_directory(directory_path: str | Path) -> list[Document]:
    """Load supported documents recursively."""

    directory = Path(directory_path)

    loaders = [
        DirectoryLoader(
            path=str(directory),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            silent_errors=False,
        ),
        DirectoryLoader(
            path=str(directory),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            silent_errors=False,
        ),
        DirectoryLoader(
            path=str(directory),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            silent_errors=False,
        ),
    ]

    documents = []

    for loader in loaders:
        documents.extend(loader.load())

    return standardize_metadata(documents)

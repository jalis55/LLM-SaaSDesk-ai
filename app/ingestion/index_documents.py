
from app.core.config import DOCS_DIR
from app.ingestion.chunker import split_documents
from app.ingestion.loader import load_directory
from app.vectorstore.chroma_store import (
    add_documents_to_store,
    get_vector_store,
)


def main() -> None:
    documents = load_directory(DOCS_DIR)

    chunks = split_documents(
        documents,
        chunk_size=500,
        chunk_overlap=100,
    )

    vector_store = get_vector_store()

    ids = add_documents_to_store(
        vector_store,
        chunks,
    )

    print("Loaded documents:", len(documents))
    print("Generated chunks:", len(chunks))
    print("Indexed chunk IDs:", len(ids))
    print("Stored records:", vector_store._collection.count())


if __name__ == "__main__":
    main()

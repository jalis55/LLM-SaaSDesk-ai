
from app.core.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
)
from app.vectorstore.chroma_store import get_vector_store


vector_store = get_vector_store()

print("Collection:", CHROMA_COLLECTION)
print("Storage directory:", CHROMA_DIR)
print("Stored records:", vector_store._collection.count())


from app.core.config import DOCS_DIR
from app.ingestion.loader import load_directory
from app.ingestion.chunker import split_documents


documents = load_directory(DOCS_DIR)

chunks = split_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100,
)

print("Original documents:", len(documents))
print("Total chunks:", len(chunks))

# for index, chunk in enumerate(chunks[:3], start=1):
#     print(f"\n--- Chunk {index} ---")
#     print("Characters:", len(chunk.page_content))
#     print("Metadata:", chunk.metadata)
#     print("Content:", chunk.page_content[:200])



pdf_chunks = [
    chunk
    for chunk in chunks
    if chunk.metadata["filename"] == "getting_started.pdf"
    and chunk.metadata.get("page_number") == 1
]

print("PDF page 1 chunks:", len(pdf_chunks))

for index, chunk in enumerate(pdf_chunks[:2], start=1):
    print(f"\n--- PDF Chunk {index} ---")
    print("Characters:", len(chunk.page_content))
    print("Content:")
    print(chunk.page_content)

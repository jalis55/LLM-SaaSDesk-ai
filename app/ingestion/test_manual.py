
from app.core.config import DOCS_DIR
from app.ingestion.loader import load_directory


documents = load_directory(DOCS_DIR)

print("Total loaded documents:", len(documents))

for index, doc in enumerate(documents, start=1):
    print(f"\nDocument {index}")
    print("Source:", doc.metadata.get("source"))
    print("Page:", doc.metadata.get("page", "N/A"))
    print("Characters:", len(doc.page_content))

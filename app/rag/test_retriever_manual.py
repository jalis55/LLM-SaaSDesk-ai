
from app.rag.retriever import retrieve_documents


def main() -> None:
    query = "How much does FlowDesk Pro cost?"

    results = retrieve_documents(
        query=query,
        k=3,
    )

    print(f"\nQuestion: {query}")
    print(f"Retrieved chunks: {len(results)}")

    for index, doc in enumerate(results, start=1):
        print(f"\n{'=' * 60}")
        print(f"RESULT {index}")
        print(f"{'=' * 60}")

        print("Filename:", doc.metadata.get("filename"))
        print("Page:", doc.metadata.get("page_number"))
        print("Content:")
        print(doc.page_content)


if __name__ == "__main__":
    main()

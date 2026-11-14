
from app.rag.retriever import retrieve_documents_with_scores


def main() -> None:
    query = "How much does FlowDesk Pro cost?"

    results = retrieve_documents_with_scores(
        query=query,
        k=5,
    )

    print(f"\nQuestion: {query}")

    for rank, (doc, distance) in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Filename: {doc.metadata.get('filename')}")
        print(f"Distance: {distance:.4f}")
        print(f"Content: {doc.page_content[:250]}")


if __name__ == "__main__":
    main()

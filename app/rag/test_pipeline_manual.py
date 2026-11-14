
from app.rag.pipeline import ask_rag


def main() -> None:
    questions = [
        "How much does FlowDesk Pro cost?",
        "Does FlowDesk offer a free plan?",
        "Who won the FIFA World Cup in 2022?",
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print("QUESTION:", question)
        result = ask_rag(question)
        print("ANSWER:", result.answer)
        print("RETRIEVED SOURCES:", result.sources)


if __name__ == "__main__":
    main()

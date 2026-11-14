
from app.rag.llm import get_llm


def main() -> None:
    llm = get_llm()

    response = llm.invoke(
        "Reply with exactly: Groq connection successful"
    )

    print("Model response:", response.content)


if __name__ == "__main__":
    main()

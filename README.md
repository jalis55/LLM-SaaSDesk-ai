# FlowDesk AI — SaaS Product Knowledge Assistant

Phase 1 starter: Streamlit UI, fictional knowledge documents, modular RAG scaffolding. **No RAG or document upload is implemented yet.**

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run `uv sync` in this folder.
3. Copy `.env.example` to `.env` and set your Groq key (not needed for Phase 1).
4. Run `uv run streamlit run app/main.py`.
5. Run `uv run pytest -q`.

The Admin page is **not authenticated**. Keep this app local until access control is added.

## Next phases

- Phase 2: loaders, chunking, local Sentence Transformers embeddings, persistent ChromaDB.
- Phase 3: LangChain retrieval + Groq `openai/gpt-oss-120b`.
- Later: citations, evaluations, secure document administration, deployment.

# 🤖 SaaSDesk AI

### A Retrieval-Augmented Generation (RAG) SaaS Support Assistant

SaaSDesk AI is a document-grounded AI support assistant built with **Python, LangChain, ChromaDB, Hugging Face embeddings, Groq, and Streamlit**.

The application answers questions about a fictional SaaS product called **FlowDesk** by retrieving relevant information from its knowledge base and generating context-aware responses.

Unlike a general-purpose chatbot, SaaSDesk AI is designed to answer questions using retrieved documentation, identify supporting sources, and decline questions when sufficient information is unavailable.

> **Project status:** Functional RAG prototype with a working Streamlit chat interface, persistent vector database, structured LLM responses, and source attribution.

---

## ✨ Features

### Implemented

- **Document ingestion:** Load Markdown (`.md`), text (`.txt`), and PDF (`.pdf`) documents.
- **Metadata processing:** Standardize document metadata, including filenames, file types, and PDF page numbers.
- **Text chunking:** Split documents into smaller, overlapping chunks using LangChain.
- **Local embeddings:** Generate 384-dimensional embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
- **Persistent vector storage:** Store document embeddings and metadata in ChromaDB.
- **Duplicate prevention:** Generate deterministic chunk IDs to avoid duplicate records when reindexing unchanged documents.
- **Semantic search:** Retrieve relevant document chunks based on meaning rather than exact keyword matches.
- **LLM-powered responses:** Generate answers using Groq's `openai/gpt-oss-120b`.
- **Structured output:** Return answers, answerability status, and model-selected supporting chunk IDs.
- **Source attribution:** Display supporting document filenames alongside generated answers.
- **Out-of-scope handling:** Return an insufficient-information response when the model determines that retrieved documentation cannot answer a question.
- **Streamlit chat interface:** Interact with the assistant through a browser-based UI.
- **Session chat history:** Preserve and display conversation messages during the active Streamlit session.
- **Model caching:** Reuse initialized embedding-model and vector-store instances within a Python process.
- **Basic testing:** Unit tests and manual integration tests for document loading, chunking, embeddings, retrieval, and generation.

### Planned Improvements

- Knowledge base management through the Streamlit Admin page
- Document uploads, deletion, and reindexing
- Automatic synchronization of changed or removed documents
- Conversation-aware follow-up questions
- Automated RAG evaluation and regression testing
- Retrieval improvements, including reranking and hybrid search
- Citation accuracy and groundedness evaluation
- Error monitoring and application logging improvements
- Deployment and production configuration

---

## 🏗️ System Architecture

```text
                  ┌───────────────────────┐
                  │      Streamlit UI     │
                  │   SaaSDesk AI Chat    │
                  └───────────┬───────────┘
                              │
                       User Question
                              │
                              ▼
                  ┌───────────────────────┐
                  │     RAG Pipeline      │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Embedding Model     │
                  │ all-MiniLM-L6-v2      │
                  └───────────┬───────────┘
                              │
                       Query Embedding
                              │
                              ▼
                  ┌───────────────────────┐
                  │       ChromaDB        │
                  │    Semantic Search    │
                  └───────────┬───────────┘
                              │
                       Top-k Documents
                              │
                              ▼
                  ┌───────────────────────┐
                  │    Prompt Builder     │
                  │ Question + Context    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │       Groq LLM        │
                  │ openai/gpt-oss-120b   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Structured Answer   │
                  │ + Supporting Sources  │
                  └───────────────────────┘
```

### Document Ingestion Pipeline

```text
Knowledge Base Documents
          │
          ▼
    Document Loader
          │
          ▼
  Metadata Standardization
          │
          ▼
    Text Chunking
   (500 characters,
    100 overlap)
          │
          ▼
    Metadata Cleaning
          │
          ▼
    Embedding Model
          │
          ▼
   Deterministic IDs
          │
          ▼
    Persistent ChromaDB
```

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|---|---|---|
| Programming language | Python 3.11 | Core application |
| Package management | uv | Dependencies and virtual environment |
| Web interface | Streamlit | Chat UI and navigation |
| LLM framework | LangChain | Document processing and RAG orchestration |
| Language model | Groq — `openai/gpt-oss-120b` | Answer generation |
| Embeddings | Hugging Face Sentence Transformers | Text and query embeddings |
| Embedding model | `all-MiniLM-L6-v2` | 384-dimensional semantic vectors |
| Vector database | ChromaDB | Persistent vector storage and search |
| Structured validation | Pydantic | Response schemas |
| Environment configuration | python-dotenv | Load environment variables |
| Testing | pytest | Unit testing |
| Linting | Ruff | Code quality |

---

## 📁 Project Structure

```text
Saasdesk-ai/
│
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   ├── test_manual.py
│   │   └── test_similarity_manual.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── index_documents.py
│   │   ├── test_manual.py
│   │   └── test_chunker_manual.py
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   ├── chroma_store.py
│   │   └── test_manual.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   ├── llm.py
│   │   ├── pipeline.py
│   │   ├── test_retriever_manual.py
│   │   ├── test_scores_manual.py
│   │   ├── test_llm_manual.py
│   │   └── test_pipeline_manual.py
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── admin.py
│   │
│   └── main.py
│
├── data/
│   ├── documents/
│   │   ├── pricing.md
│   │   ├── features.md
│   │   ├── billing_policy.md
│   │   ├── refund_policy.md
│   │   ├── cancellation_policy.md
│   │   ├── security_privacy.md
│   │   ├── integrations.md
│   │   ├── api_documentation.md
│   │   ├── account_management.md
│   │   ├── team_management.md
│   │   ├── data_retention.md
│   │   ├── support_sla.md
│   │   ├── faq.txt
│   │   ├── troubleshooting.txt
│   │   ├── getting_started.pdf
│   │   └── admin_guide.pdf
│   │
│   └── evaluation_questions.jsonl
│
├── storage/
│   └── chroma/
│
├── tests/
│   ├── test_config.py
│   ├── test_loader.py
│   └── test_chunker.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

The structure separates document ingestion, embeddings, vector storage, retrieval, generation, and the user interface into independent modules.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- [uv](https://docs.astral.sh/uv/)
- A Groq API key
- Internet access for Groq inference and initial embedding-model download

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Saasdesk-ai
```

Replace `<YOUR_REPOSITORY_URL>` with the actual GitHub repository URL.

### 2. Install dependencies

```bash
uv sync
```

This installs the dependencies defined in `pyproject.toml` and uses the lockfile for reproducible dependency resolution.

### 3. Configure environment variables

Create a `.env` file in the project root.

You can start from the example configuration:

```bash
cp .env.example .env
```

Configure the following values:

```dotenv
GROQ_API_KEY=your_groq_api_key

AI_MODEL=openai/gpt-oss-120b

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

CHROMA_COLLECTION=saasdesk_knowledge
```

Never commit your actual `.env` file or API keys to Git.

### 4. Index the knowledge base

Run:

```bash
uv run python -m app.ingestion.index_documents
```

The indexing process:

1. Loads supported files from `data/documents/`.
2. Standardizes document metadata.
3. Splits documents into chunks.
4. Removes unsupported metadata values.
5. Generates embeddings.
6. Stores chunks in the persistent ChromaDB collection.

For the current sample dataset, the verified output is:

```text
Loaded documents: 16
Generated chunks: 67
Indexed chunk IDs: 67
Stored records: 67
```

These counts depend on the documents and chunking configuration.

Reindexing unchanged documents reuses deterministic IDs and avoids creating duplicate records.

**Limitation:** Updated documents can leave outdated chunks in the collection because full document synchronization is not yet implemented.

### 5. Start the application

Run the following command from the project root:

```bash
PYTHONPATH=. uv run streamlit run app/main.py
```

Streamlit will display a local URL, typically:

```text
http://localhost:8501
```

Open the URL in your browser.

The application includes navigation for:

- **AI Assistant:** Functional document-grounded chat interface.
- **Knowledge Base:** Admin page reserved for future management functionality.

---

## 💬 Example Questions

The assistant can answer questions based on the fictional FlowDesk documentation.

**Example 1 — Subscription pricing**

User:

> How much does FlowDesk Pro cost?

Assistant:

> FlowDesk Pro costs $12 per member per month with monthly billing. With annual billing, it costs $10 per member per month, billed as $120 per member per year.

Supporting source: `faq.txt`

**Example 2 — Free plan**

User:

> Does FlowDesk offer a free plan?

Assistant:

> Yes. FlowDesk offers a free plan that costs $0 and includes 3 members, 2 active projects, and 1 GB of storage.

Supporting source: `faq.txt`

**Example 3 — SSO**

User:

> Does FlowDesk support SSO?

Assistant:

> Yes. SAML single sign-on (SSO) is available on the Business plan.

Supporting sources: `faq.txt`, `security_privacy.md`

**Example 4 — Unsupported question**

User:

> Who won the FIFA World Cup in 2022?

Assistant:

> I don't have enough information in the FlowDesk documentation to answer that question.

Supporting sources: None

These are representative outputs from manual testing. Responses may vary between model invocations.

---

## 🧠 How the RAG Pipeline Works

### 1. Document loading

The application loads `.md`, `.txt`, and `.pdf` files from the local knowledge base.

Document metadata includes the original filename, file type, and PDF page number where applicable.

### 2. Chunking

Documents are split using `RecursiveCharacterTextSplitter`.

Current configuration:

```python
chunk_size = 500
chunk_overlap = 100
```

These values represent character-based chunk sizes and target overlap.

### 3. Embedding generation

Each document chunk is converted into a vector using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model generates 384-dimensional embeddings locally on the CPU.

Embeddings are normalized before storage and retrieval.

### 4. Vector storage

ChromaDB stores the document chunks, embeddings, and metadata.

Current configuration:

```text
Collection: saasdesk_knowledge
Storage: storage/chroma/
```

Chunk IDs are generated using SHA-256 hashes based on the source, page, and content.

This prevents duplicate insertion of unchanged chunks, although identical chunks within the same source and page can share an ID.

### 5. Semantic retrieval

When a user asks a question, the application converts the question into an embedding and retrieves the most relevant chunks from ChromaDB.

Current retrieval configuration:

```python
k = 3
```

Retrieval is based on vector similarity rather than exact keyword matching.

### 6. Context-grounded generation

The retrieved chunks are included in a prompt sent to the Groq LLM.

The model is instructed to answer only from the provided documentation and avoid unsupported claims.

These instructions reduce hallucination risk but do not guarantee factual correctness.

### 7. Structured response and source attribution

The LLM generates structured data containing:

```python
class GeneratedAnswer(BaseModel):
    answer: str
    is_answerable: bool
    supporting_chunk_ids: list[int]
```

The pipeline validates the returned chunk IDs against the retrieved documents and maps them to filenames.

The application returns:

```python
class RAGResponse(BaseModel):
    answer: str
    sources: list[str]
```

Source selection is currently performed by the LLM. Independent citation verification has not yet been implemented.

---

## 🧪 Testing

### Run unit tests

```bash
uv run pytest -v
```

Existing unit tests cover configuration, document loading, metadata cleaning, and text chunking.

### Test embeddings

```bash
uv run python -m app.embeddings.test_manual
```

### Test embedding similarity

```bash
uv run python -m app.embeddings.test_similarity_manual
```

### Test ChromaDB connection

```bash
uv run python -m app.vectorstore.test_manual
```

### Test semantic retrieval

```bash
uv run python -m app.rag.test_retriever_manual
```

### Inspect retrieval distances

```bash
uv run python -m app.rag.test_scores_manual
```

### Test Groq connectivity

```bash
uv run python -m app.rag.test_llm_manual
```

### Test the complete RAG pipeline

```bash
uv run python -m app.rag.test_pipeline_manual
```

The end-to-end pipeline has been manually verified with questions about pricing, free-plan availability, and unsupported topics.

Automated retrieval and answer-quality evaluation are planned.

---

## ⚡ Performance Optimization

The project uses Python's `functools.lru_cache` to reuse initialized resources.

```python
@lru_cache(maxsize=1)
def get_embedding_model():
    ...
```

```python
@lru_cache(maxsize=1)
def get_vector_store():
    ...
```

This prevents unnecessary model and vector-store initialization during repeated queries within the same Python process.

Caching does not persist across application restarts, and embedding computation is still performed for each new query.

---

## ⚠️ Current Limitations

This project is under active development.

- No authentication or role-based access control.
- No completed document-upload management workflow.
- No automatic removal of outdated vector records.
- No conversation-aware retrieval for follow-up questions.
- No independent citation or factual-grounding verification.
- No automated RAG benchmark results yet.
- No production deployment or monitoring setup.
- Chat history is limited to the active Streamlit session.
- Some document loaders currently use `langchain-community`, which has emitted a deprecation warning and may require migration.

The current implementation is intended as a development and portfolio project, not a production-ready customer support service.

---

## 🗺️ Development Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Project setup and configuration | Completed |
| 2 | Document ingestion and vector storage | Completed — basic indexing |
| 3 | Semantic retrieval and Groq RAG pipeline | Completed — baseline |
| 4 | Streamlit AI chat interface | Completed |
| 5 | Knowledge base management | Planned |
| 6 | Automated RAG evaluation | Planned |
| 7 | Production improvements and deployment | Planned |

---

## 📚 Sample Dataset

The project uses a fictional SaaS company named **FlowDesk**.

Its sample knowledge base contains documentation covering pricing, subscriptions, billing, refunds, cancellations, features, security, integrations, API usage, account management, team management, retention, troubleshooting, and support policies.

**All FlowDesk company information, pricing, policies, and product details are fictional and intended for demonstration and testing purposes only.**

---

## 🔒 Security Considerations

- API credentials are loaded from environment variables.
- Secrets should never be committed to source control.
- Retrieved document content is treated as untrusted reference data in the system prompt.
- Application errors are not directly exposed to users through the chat interface.

Prompt injection, access control, document trust boundaries, and operational security require further work before production deployment.

---

## 📄 License

A license has not yet been specified for this project.

Add a `LICENSE` file before distributing the project under an open-source license.

---

**SaaSDesk AI — Building a document-grounded SaaS support assistant with Retrieval-Augmented Generation.**
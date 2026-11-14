import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")
DOCS_DIR = ROOT_DIR / "data" / "documents"
CHROMA_DIR = ROOT_DIR / "storage" / "chroma"
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "flowdesk_knowledge")

import streamlit as st
from app.core.config import DOCS_DIR

st.title("Knowledge Base Management")
st.warning("Development only: this page has no authentication.")
st.info("Document upload and indexing will be implemented in later phases.")
st.file_uploader("Upload documents (coming soon)", type=["pdf", "md", "txt"], accept_multiple_files=True, disabled=True)
st.subheader("Available sample documents")
for path in sorted(DOCS_DIR.glob("*.md")):
    st.write(f"• {path.name}")

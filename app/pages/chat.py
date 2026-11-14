
import logging

import streamlit as st

from app.rag.pipeline import ask_rag


logger = logging.getLogger(__name__)


def render_chat_page() -> None:
    """Render the FlowDesk AI support chat interface."""

    # -----------------------------------------
    # Page Header
    # -----------------------------------------

    st.title("🤖 SassDesk AI Assistant")

    st.caption(
        "Ask questions about FlowDesk pricing, features, "
        "billing, security, integrations, and support."
    )

    # -----------------------------------------
    # Initialize Chat History
    # -----------------------------------------

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -----------------------------------------
    # Display Chat History
    # -----------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            sources = message.get("sources", [])

            if sources:
                st.caption(
                    "📚 Sources: " + ", ".join(sources)
                )

    # -----------------------------------------
    # User Input
    # -----------------------------------------

    question = st.chat_input(
        "Ask anything about FlowDesk..."
    )

    if not question:
        return

    # -----------------------------------------
    # Save and Display User Message
    # -----------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # -----------------------------------------
    # Generate RAG Response
    # -----------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Searching knowledge base..."):

            try:
                result = ask_rag(question)

            except Exception:
                logger.exception(
                    "RAG pipeline failed while answering a question."
                )

                st.error(
                    "Something went wrong while generating "
                    "the answer. Please try again."
                )

                return

        # -------------------------------------
        # Display Answer
        # -------------------------------------

        st.markdown(result.answer)

        # -------------------------------------
        # Display Supporting Sources
        # -------------------------------------

        if result.sources:
            st.caption(
                "📚 Sources: " + ", ".join(result.sources)
            )

        # -------------------------------------
        # Save Assistant Response
        # -------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": result.sources,
            }
        )


# ---------------------------------------------
# Streamlit Page Entry Point
# ---------------------------------------------

render_chat_page()

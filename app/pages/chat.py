import streamlit as st

st.title("FlowDesk AI Assistant")
st.caption("Ask about FlowDesk pricing, features, and policies.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about FlowDesk..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    response = "RAG is not connected yet. We'll implement retrieval and answers in Phase 3."
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

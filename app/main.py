import streamlit as st

st.set_page_config(page_title="SaaSDesk AI", page_icon="🤖", layout="wide")

navigation = st.navigation({
    "Workspace": [st.Page("pages/chat.py", title="AI Assistant", icon=":material/chat:", default=True)],
    "Management": [st.Page("pages/admin.py", title="Knowledge Base", icon=":material/folder:")],
})
navigation.run()

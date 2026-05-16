import streamlit as st
import os

# Set env vars from Streamlit secrets BEFORE importing agent
if hasattr(st, 'secrets'):
    os.environ["GOgsk_VHmTUE1BfABo1K2b4Xj5WGdyb3FY2v2AyEjbW0JEBhsMaiV8ezQ8"] = st.secrets.get("GOgsk_VHmTUE1BfABo1K2b4Xj5WGdyb3FY2v2AyEjbW0JEBhsMaiV8ezQ8", "")
    os.environ["FOLDER_ID"] = st.secrets.get("FOLDER_ID", "")
    os.environ["SERVICE_ACCOUNT_FILE"] = st.secrets.get("SERVICE_ACCOUNT_FILE", "service_account.json")

from agent import chat  # import AFTER env vars are set

st.set_page_config(page_title="Drive Agent", page_icon="📁", layout="centered")
st.title("📁 Google Drive AI Assistant")
st.caption("Apni Drive files natural language mein search karo!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Koi bhi file dhundo... jaise 'show me all PDFs'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Searching your Drive..."):
            bot_reply = chat(user_input, st.session_state.messages[:-1])
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
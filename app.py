import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load secrets from Streamlit if available
try:
    if hasattr(st, 'secrets'):
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        if "MODEL_NAME" in st.secrets:
            os.environ["MODEL_NAME"] = st.secrets["MODEL_NAME"]
        if "FOLDER_ID" in st.secrets:
            os.environ["FOLDER_ID"] = st.secrets["FOLDER_ID"]
        if "SERVICE_ACCOUNT_FILE" in st.secrets:
            os.environ["SERVICE_ACCOUNT_FILE"] = st.secrets["SERVICE_ACCOUNT_FILE"]
except Exception:
    pass

from agent import chat

st.set_page_config(page_title="Drive Agent", page_icon="📁", layout="centered")
st.title("📁 Google Drive AI Assistant")
st.caption("Search your Drive files using natural language!")


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me to find files... e.g., 'show me all PDFs'")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching your Drive..."):
            try:
                bot_reply = chat(user_input, st.session_state.messages[:-1])
            except Exception as e:
                bot_reply = f"Sorry, I encountered an error. Please try again."
        
        st.markdown(bot_reply)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
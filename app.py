
import streamlit as st
import requests

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
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"message": user_input, "history": st.session_state.messages[:-1]},
                    timeout=60
                )
                bot_reply = response.json().get("response", "Kuch error aaya!")
            except Exception as e:
                bot_reply = f"❌ Backend connect nahi hua: {str(e)}"
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
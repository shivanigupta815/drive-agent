import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Drive Agent 🗂️",
    page_icon="🗂️",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 12px; }
    h1 { color: #1a73e8; }
    .subtitle { color: #666; font-size: 14px; margin-top: -15px; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🗂️ Google Drive Agent")
st.markdown('<p class="subtitle">Search your Google Drive files using natural language</p>', 
            unsafe_allow_html=True)
st.divider()

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Greeting message
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "👋 Hi! I'm your **Google Drive Assistant**.\n\n"
            "I can help you find files in your Drive. Try asking me:\n"
            "- 📄 *\"Find all PDF files\"*\n"
            "- 📊 *\"Show me spreadsheets about budget\"*\n"
            "- 🔍 *\"Search for files containing 'invoice'\"*\n"
            "- 📅 *\"Find documents modified recently\"*\n\n"
            "What are you looking for?"
        ),
    })

# ── Render Chat History ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask me to find files... e.g., 'show me all PDFs'")

if user_input:
    # Add user message to session
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get response from backend
    with st.chat_message("assistant"):
        try:
            with st.spinner("🔍 Searching your Drive..."):
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "message": user_input,
                        "history": st.session_state.messages[:-1]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        bot_reply = data.get("response", "No response received")
                    else:
                        bot_reply = data.get("error", "An error occurred")
                else:
                    bot_reply = "Error: Could not reach the backend server"
            
            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Request timed out. Please try again."
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to backend. Make sure the API server is running."
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        except Exception as e:
            error_msg = f"❌ An error occurred: Please try again."
            st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ── Chat Input ─────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask me to find files in your Drive..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build history for API (exclude the greeting)
    api_history = [
        m for m in st.session_state.messages[:-1]  # exclude current user message
        if m["role"] in ("user", "assistant")
    ]

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Searching your Drive... 🔍"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": user_input, "history": api_history},
                    timeout=120,
                )
                response.raise_for_status()
                reply = response.json().get("response", "Sorry, I couldn't process that.")
            except requests.exceptions.ConnectionError:
                reply = "⚠️ Cannot connect to backend. Make sure FastAPI is running on port 8000."
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("💡 Search Tips")
    st.markdown("""
    **By file type:**
    - "Find all PDFs"
    - "Show me Google Sheets"
    - "List all images"
    
    **By name:**
    - "Find file named report"
    - "Show files with 'budget' in name"
    
    **By content:**
    - "Files containing 'invoice'"
    - "Documents about sales"
    
    **By date:**
    - "Files modified last week"
    - "Recent documents"
    """)

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
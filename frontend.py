import streamlit as st
import requests
import os

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
            "- 📅 *\"Find documents modified this month\"*\n\n"
            "What are you looking for?"
        ),
    })

# ── Render Chat History ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
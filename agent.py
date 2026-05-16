import os

# ── Keys ─────────────────────────────────────────────
GOOGLE_API_KEY = "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"
FOLDER_ID = "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt"
SERVICE_ACCOUNT_FILE = "service_account.json"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["FOLDER_ID"] = FOLDER_ID
os.environ["SERVICE_ACCOUNT_FILE"] = SERVICE_ACCOUNT_FILE


# ── Imports ──────────────────────────────────────────
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from drive_tool import search_drive_files


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


# ── Tool ─────────────────────────────────────────────
@tool
def DriveSearchTool(query: str) -> str:
    """
    Search Google Drive files using a query string.
    Examples:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'invoice'
    """
    return search_drive_files(query)


# ── Agent ────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Google Drive file search assistant.

IMPORTANT: You MUST always call the DriveSearchTool when user asks about files.

Rules for query parameter:
- Show all files: use query = "name contains ''"  
- PDF files: mimeType = 'application/pdf'
- Images: mimeType contains 'image'
- By name: name contains 'report'
- Google Sheets: mimeType = 'application/vnd.google-apps.spreadsheet'
- Google Docs: mimeType = 'application/vnd.google-apps.document'

NEVER say "here are results" without actually calling DriveSearchTool first.
Always call the tool, then show the results to user."""

agent = create_react_agent(
    model=llm,
    tools=[DriveSearchTool]
)


# ── Chat Function (FIXED) ────────────────────────────
def chat(message: str, history: list = []) -> str:
    try:
        lc_messages = []

        for msg in history:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        lc_messages.append(HumanMessage(content=message))

        result = agent.invoke({"messages": lc_messages})

        print("AGENT RESULT:", result)

        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "No response generated."

    except Exception as e:
        print("CHAT ERROR:", str(e))
        return f"Error: {str(e)}"
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

    Example:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'invoice'
    """

    results = search_drive_files(query)

    if not results:
        return "No files found matching your search."

    if isinstance(results, list) and "error" in results[0]:
        return f"Error: {results[0]['error']}"

    output = f"Found {len(results)} file(s):\n\n"

    for i, f in enumerate(results, 1):
        output += (
            f"{i}. {f.get('name','Unknown')}\n"
            f"   Type: {f.get('type','Unknown')}\n"
            f"   Modified: {f.get('modified','Unknown')[:10] if f.get('modified') else 'Unknown'}\n"
            f"   Link: {f.get('link','N/A')}\n\n"
        )

    return output


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
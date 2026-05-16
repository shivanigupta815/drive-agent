import os

# ── Imports ──────────────────────────────────────────
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from drive_tool import search_drive_files

# ── LLM ──────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GOgsk_VHmTUE1BfABo1K2b4Xj5WGdyb3FY2v2AyEjbW0JEBhsMaiV8ezQ8") or os.getenv("Ogsk_VHmTUE1BfABo1K2b4Xj5WGdyb3FY2v2AyEjbW0JEBhsMaiV8ezQ8"),
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

# ── System Prompt ─────────────────────────────────────
SYSTEM_PROMPT = """You are a Google Drive file search assistant.

IMPORTANT: You MUST always call the DriveSearchTool when user asks about files.

Rules for query parameter:
- Show all files: use query = "name contains ''"
- PDF files: mimeType = 'application/pdf'
- Images: mimeType contains 'image'
- By name: name contains 'report'
- Google Sheets: mimeType = 'application/vnd.google-apps.spreadsheet'
- Google Docs: mimeType = 'application/vnd.google-apps.document'

NEVER say you cannot do this. Always call the tool, then show results to user."""

# ── Agent ─────────────────────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=[DriveSearchTool]
)

# ── Chat Function ─────────────────────────────────────
def chat(message: str, history: list = []) -> str:
    try:
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]  # always first

        for msg in history:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        lc_messages.append(HumanMessage(content=message))
        result = agent.invoke({"messages": lc_messages})

        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "No response generated."

    except Exception as e:
        print("CHAT ERROR:", str(e))
        return f"Error: {str(e)}"
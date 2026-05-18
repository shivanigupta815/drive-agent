import os
from typing import Optional

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from drive_tool import search_drive_files

SYSTEM_PROMPT = """You are a Google Drive file search assistant.

Your only job is to translate user requests into a Google Drive files.list q parameter
and use DriveSearchTool to get results.

Rules:
1. ALWAYS call DriveSearchTool.
2. Do not answer without calling the tool.
3. Use the q parameter syntax from the Drive API.
4. Example q strings:
   - name contains 'invoice'
   - mimeType = 'application/pdf'
   - fullText contains 'budget'
   - name contains 'report' and mimeType = 'application/pdf'
   - modifiedTime > '2024-01-01T00:00:00'
5. If the user asks for all files, use an empty query string.
"""


def get_llm() -> Optional[object]:
    model_name = os.getenv("MODEL_NAME", "openai:gpt-4o-mini")

    if model_name.startswith("openai:"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return init_chat_model(model_name, temperature=0, openai_api_key=api_key)

    if model_name.startswith("groq:"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return init_chat_model(model_name, temperature=0, api_key=api_key)

    try:
        return init_chat_model(model_name, temperature=0)
    except Exception:
        return None


@tool
def DriveSearchTool(query: str) -> str:
    """Search Google Drive files with the given Drive API q query."""
    return search_drive_files(query or "")


def get_agent():
    llm = get_llm()
    if llm is None:
        raise ValueError(
            "LLM provider not configured. Set OPENAI_API_KEY or GROQ_API_KEY and MODEL_NAME."
        )

    return create_agent(
        model=llm,
        tools=[DriveSearchTool],
        system_prompt=SYSTEM_PROMPT,
    )


def convert_query_to_drive_format(user_query: str) -> str:
    """Convert natural language query to Google Drive API query format"""
    query_lower = user_query.lower()

    if "pdf" in query_lower:
        return "mimeType = 'application/pdf'"
    elif "sheet" in query_lower or "spreadsheet" in query_lower or "excel" in query_lower:
        return "mimeType = 'application/vnd.google-apps.spreadsheet'"
    elif "doc" in query_lower or "word" in query_lower or "document" in query_lower:
        return "mimeType = 'application/vnd.google-apps.document'"
    elif "image" in query_lower or "jpg" in query_lower or "png" in query_lower:
        return "mimeType contains 'image'"
    elif "video" in query_lower or "mp4" in query_lower:
        return "mimeType contains 'video'"
    elif "all" in query_lower or "show" in query_lower:
        return ""
    else:
        return f"name contains '{user_query}'"


def direct_search(message: str) -> str:
    drive_query = convert_query_to_drive_format(message)
    return search_drive_files(drive_query)


def chat(message: str, history: list = []) -> str:
    try:
        agent = get_agent()
        if hasattr(agent, "invoke"):
            result = agent.invoke({"input": message})
        else:
            result = agent.run(message)
        if isinstance(result, dict):
            return result.get("output", str(result))
        return str(result)
    except ValueError:
        return direct_search(message)
    except Exception:
        return "I couldn't search your Drive. Please try again."
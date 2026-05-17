import os
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from drive_tool import search_drive_files, build_drive_query

def get_api_key():
    """Safely retrieve API key without exposing it"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except:
            pass
    return api_key

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

SYSTEM_PROMPT = """You are a Google Drive file search assistant.

Your task: Use the DriveSearchTool to search for files based on user queries.
Then return the results directly to the user.

Guidelines:
1. Call DriveSearchTool with appropriate query
2. Return the tool results as-is
3. If no files found, inform the user clearly
4. Be concise and helpful"""

def convert_query_to_drive_format(user_query: str) -> str:
    """Convert natural language query to Google Drive API query format"""
    query_lower = user_query.lower()
    
    # File type mappings
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
        return ""  # Empty = show all files
    else:
        # Default: search by name
        return f"name contains '{user_query}'"

def get_agent():
    api_key = get_api_key()
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment or secrets")
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0,
        max_tokens=1024  # Limit response length for faster processing
    )
    return create_react_agent(model=llm, tools=[DriveSearchTool])

def chat(message: str, history: list = []) -> str:
    """Process chat message and return response"""
    try:
        # Convert user query to Drive API format directly
        drive_query = convert_query_to_drive_format(message)
        
        # Call DriveSearchTool directly for faster, more reliable results
        result = search_drive_files(drive_query)
        
        return result
    
    except Exception as e:
        # Don't expose internal errors to user, log safely
        return f"I couldn't search your Drive. Please try again."
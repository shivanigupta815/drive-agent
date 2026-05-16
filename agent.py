import os
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from drive_tool import search_drive_files

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

SYSTEM_PROMPT = """You are a Google Drive file search assistant. You have access to DriveSearchTool.

RULES:
1. ALWAYS call DriveSearchTool first before responding
2. NEVER make up or guess file names
3. NEVER say results are fictional
4. After tool returns results, show them to user

Query examples:
- All files: name contains ''
- PDFs: mimeType = 'application/pdf'
- Images: mimeType contains 'image'
- By name: name contains 'report'
- Sheets: mimeType = 'application/vnd.google-apps.spreadsheet'"""
def get_agent():
    import streamlit as st
    
    api_key = os.getenv("GROQ_API_KEY")
    print(f"API KEY: {api_key[:10] if api_key else 'NONE'}")
    
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            print("Got key from secrets")
        except Exception as e:
            print(f"Secrets error: {e}")
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",  # chhota model, zyada tokens
        api_key=api_key,
        temperature=0
    )
    return create_react_agent(model=llm, tools=[DriveSearchTool])

def chat(message: str, history: list = []) -> str:
    print("CHAT CALLED:", message)  # ADD
    try:
        agent = get_agent()
        print("AGENT CREATED")  # ADD
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in history:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        lc_messages.append(HumanMessage(content=message))
        print("INVOKING AGENT")  # ADD
        result = agent.invoke({"messages": lc_messages})
        print("AGENT DONE")  # ADD
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content
        return "No response generated."
    except Exception as e:
        print("CHAT ERROR:", str(e))
        return f"Error: {str(e)}"
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import json

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud"""
    return os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"

def get_drive_service():
    """Get authenticated Google Drive service - works on both localhost and Streamlit Cloud"""
    
    try:
        import streamlit as st
        is_cloud = is_streamlit_cloud()
    except:
        is_cloud = False
        st = None
    
    # Try to get credentials from Streamlit secrets (Streamlit Cloud)
    if is_cloud and st:
        try:
            # On Streamlit Cloud: credentials are in st.secrets
            service_account_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            pass
    
    # Fallback: Try local service_account.json (localhost)
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
    
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            raise FileNotFoundError(f"Error reading service account from {SERVICE_ACCOUNT_FILE}: {str(e)}")
    
    raise FileNotFoundError(
        "Service account credentials not found. "
        "On Streamlit Cloud: add 'gcp_service_account' to .streamlit/secrets.toml. "
        "On localhost: place service_account.json in project root."
    )

def get_folder_id():
    """Get folder ID from environment or Streamlit secrets - works on both platforms"""
    
    # Try Streamlit secrets first (Streamlit Cloud)
    try:
        import streamlit as st
        folder_id = st.secrets.get("FOLDER_ID")
        if folder_id:
            return folder_id
    except:
        pass
    
    # Fallback to environment variable (localhost)
    folder_id = os.getenv("FOLDER_ID")
    if folder_id:
        return folder_id
    
    raise ValueError(
        "FOLDER_ID not found. "
        "On Streamlit Cloud: add 'FOLDER_ID' to .streamlit/secrets.toml. "
        "On localhost: add FOLDER_ID to .env file."
    )

def build_drive_query(query: str) -> str:
    """Build Google Drive API query string"""
    folder_id = get_folder_id()
    
    if not query.strip():
        return f"'{folder_id}' in parents and trashed=false"
    else:
        return f"'{folder_id}' in parents and ({query}) and trashed=false"

def search_drive_files(query: str) -> str:
    """Search Google Drive files and return formatted results"""
    try:
        service = get_drive_service()
        full_query = build_drive_query(query)

        results = service.files().list(
            q=full_query,
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get("files", [])

        if not files:
            return "❌ No files found matching your search."

        # Format output with clear file names
        output = f"✅ Found **{len(files)}** file(s):\n\n"
        for idx, f in enumerate(files, 1):
            name = f.get("name", "Unknown")
            mime_type = f.get("mimeType", "")
            modified = f.get("modifiedTime", "")[:10] if f.get("modifiedTime") else "N/A"
            link = f.get("webViewLink", "#")
            
            # Get file type icon
            icon = get_file_icon(mime_type)
            file_type = get_file_type_name(mime_type)
            
            output += f"{idx}. {icon} **{name}**\n"
            output += f"   📋 Type: {file_type} | 📅 Modified: {modified}\n\n"

        return output

    except FileNotFoundError as e:
        return f"❌ Configuration error: {str(e)}"
    except ValueError as e:
        return f"❌ Configuration error: {str(e)}"
    except Exception as e:
        return f"❌ Error searching Drive: Please check your configuration."

def get_file_icon(mime_type: str) -> str:
    """Get appropriate icon for file type"""
    if "pdf" in mime_type:
        return "📕"
    elif "spreadsheet" in mime_type or "sheet" in mime_type:
        return "📊"
    elif "document" in mime_type or "word" in mime_type:
        return "📄"
    elif "image" in mime_type:
        return "🖼️"
    elif "video" in mime_type:
        return "🎬"
    elif "audio" in mime_type:
        return "🎵"
    elif "folder" in mime_type:
        return "📁"
    else:
        return "📎"

def get_file_type_name(mime_type: str) -> str:
    """Get human-readable file type name"""
    if not mime_type:
        return "Unknown"
    
    if "pdf" in mime_type:
        return "PDF"
    elif "spreadsheet" in mime_type:
        return "Google Sheet"
    elif "document" in mime_type:
        return "Google Doc"
    elif "presentation" in mime_type:
        return "Google Slides"
    elif "image" in mime_type:
        return "Image"
    elif "video" in mime_type:
        return "Video"
    elif "audio" in mime_type:
        return "Audio"
    elif "text" in mime_type:
        return "Text File"
    elif "folder" in mime_type:
        return "Folder"
    else:
        return mime_type.split("/")[-1].title()
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    # Streamlit Cloud pe secrets se credentials lo
    if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
    else:
        # Local pe file se lo
        SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    return build("drive", "v3", credentials=creds)

def get_folder_id():
    if hasattr(st, 'secrets') and 'FOLDER_ID' in st.secrets:
        return st.secrets["FOLDER_ID"]
    return os.getenv("FOLDER_ID")

def search_drive_files(query: str) -> str:
    try:
        service = get_drive_service()
        FOLDER_ID = get_folder_id()

        if query.strip() == "" or query.strip() == "*":
            full_query = f"'{FOLDER_ID}' in parents and trashed=false"
        else:
            full_query = f"'{FOLDER_ID}' in parents and ({query}) and trashed=false"

        results = service.files().list(
            q=full_query,
            pageSize=50,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)"
        ).execute()

        files = results.get("files", [])

        if not files:
            return "Koi file nahi mili."

        output = f"Mujhe {len(files)} file(s) mili:\n\n"
        for f in files:
            name = f.get("name", "Unknown")
            mime = f.get("mimeType", "")
            modified = f.get("modifiedTime", "")[:10]
            link = f.get("webViewLink", "#")
            output += f"📄 {name} | {mime} | {modified} | {link}\n"

        return output

    except Exception as e:
        return f"Drive Error: {str(e)}"
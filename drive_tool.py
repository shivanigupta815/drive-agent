from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "service_account.json"
DRIVE_FOLDER_ID = "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
DRIVE_FOLDER_ID = os.getenv("FOLDER_ID", "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt")


def get_drive_service():
    """Authenticate and return Google Drive service."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service


def search_drive_files(query: str, max_results: int = 10) -> list[dict]:
    """
    Search Google Drive files using the Drive API q parameter.

    Args:
        query: A Google Drive API query string.
                Examples:
                  - "name contains 'report'"
                  - "mimeType = 'application/pdf'"
                  - "fullText contains 'invoice'"
                  - "name contains 'budget' and mimeType = 'application/vnd.google-apps.spreadsheet'"
        max_results: Maximum number of results to return (default 10).

    Returns:
        List of dicts with file info: id, name, mimeType, webViewLink, modifiedTime
    """
    try:
        service = get_drive_service()

        # Always restrict search to the shared folder
        folder_query = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"

        # Combine with user query if provided
        if query and query.strip():
            full_query = f"({query}) and {folder_query}"
        else:
            full_query = folder_query

        results = service.files().list(
            q=full_query,
            pageSize=max_results,
            fields="files(id, name, mimeType, webViewLink, modifiedTime, size)",
            orderBy="modifiedTime desc",
        ).execute()

        files = results.get("files", [])

        if not files:
            return []

        formatted = []
        for f in files:
            mime = f.get("mimeType", "")
            formatted.append({
                "id": f.get("id"),
                "name": f.get("name"),
                "type": _mime_to_readable(mime),
                "mimeType": mime,
                "link": f.get("webViewLink", ""),
                "modified": f.get("modifiedTime", ""),
                "size": f.get("size", "N/A"),
            })

        return formatted

    except Exception as e:
        return [{"error": str(e)}]


def _mime_to_readable(mime: str) -> str:
    """Convert MIME type to human-readable format."""
    mime_map = {
        "application/vnd.google-apps.document": "Google Doc",
        "application/vnd.google-apps.spreadsheet": "Google Sheet",
        "application/vnd.google-apps.presentation": "Google Slides",
        "application/vnd.google-apps.folder": "Folder",
        "application/pdf": "PDF",
        "image/jpeg": "JPEG Image",
        "image/png": "PNG Image",
        "text/plain": "Text File",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel Sheet",
    }
    return mime_map.get(mime, mime.split("/")[-1].capitalize())
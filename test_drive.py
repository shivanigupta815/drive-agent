"""
Test script to verify Google Drive API connection
Run this to test if your service account and Drive access are working correctly
"""

import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

def test_drive_connection():
    """Test Google Drive API connection"""
    
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
    FOLDER_ID = os.getenv("FOLDER_ID")
    
    # Validate configuration
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Error: Service account file not found: {SERVICE_ACCOUNT_FILE}")
        print("Please ensure service_account.json is in the project root")
        return False
    
    if not FOLDER_ID:
        print("❌ Error: FOLDER_ID not set in .env file")
        print("Please add FOLDER_ID to .env file")
        return False
    
    print(f"✓ Using folder: {FOLDER_ID}")
    print(f"✓ Using service account: {SERVICE_ACCOUNT_FILE}\n")
    
    try:
        # Authenticate
        print("🔐 Authenticating...")
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        print("✓ Authentication successful\n")
        
        # Build service
        print("🔗 Building Google Drive service...")
        service = build("drive", "v3", credentials=creds)
        print("✓ Service built\n")
        
        # Test: Get all files in folder
        print(f"📂 Listing files in folder...")
        query = f"'{FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="files(id, name, mimeType, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = results.get("files", [])
        print(f"✓ Found {len(files)} files\n")
        
        if files:
            print("Sample files:")
            for i, file in enumerate(files[:5], 1):
                print(f"{i}. {file['name']} ({file['mimeType']})")
            if len(files) > 5:
                print(f"... and {len(files) - 5} more")
        else:
            print("⚠️ No files found in folder")
        
        # Test: Search for PDFs
        print("\n" + "="*50)
        print("🔍 Searching for PDF files...")
        pdf_query = f"'{FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
        pdf_results = service.files().list(
            q=pdf_query,
            pageSize=10,
            fields="files(id, name)"
        ).execute()
        
        pdf_files = pdf_results.get("files", [])
        print(f"✓ Found {len(pdf_files)} PDF files")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Drive Connection\n")
    print("="*50)
    
    success = test_drive_connection()
    
    print("\n" + "="*50)
    if success:
        print("✅ All tests passed! Your setup is correct.")
    else:
        print("❌ Tests failed. Please check your configuration.")

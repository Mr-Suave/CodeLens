import os
import sys
import tempfile
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "Raghavendra"
MONGO_COLLECTION = "Sastry"

# Google Drive Authentication using Service Account
SERVICE_ACCOUNT_FILE = "fileuploaderapp-454310-b3fb5dbe37a4.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1YiRmfbNlhT_NJXEwe6QGJ-ApOH3xW-rR'  # Replace with actual folder ID

# Function to authenticate Google Drive
def authenticate_drive():
    """Authenticate and return a Google Drive API client."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("❌ Google Drive Service Account JSON missing!")
        return None
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

# Function to upload a file to Google Drive
def upload_to_drive(file_path, file_name, folder_id=FOLDER_ID):
    """Uploads a file to Google Drive under the correct account."""
    drive_service = authenticate_drive()
    if not drive_service:
        return None, "❌ Google Drive authentication failed!"
    
    try:
        file_metadata = {"name": file_name, "parents": [folder_id] if folder_id else []}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_id = uploaded_file.get("id")
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        # Store the file URL in MongoDB
        store_file_url_in_mongodb(file_name, file_url)
        
        return file_url, f"✅ File '{file_name}' uploaded successfully! [View File]({file_url})"
    except Exception as e:
        return None, f"❌ Upload failed for '{file_name}': {str(e)}"

# Function to store file URL in MongoDB
def store_file_url_in_mongodb(file_name, file_url):
    """Stores the file URL in MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        file_data = {
            "file_name": file_name,
            "file_url": file_url,
            "uploaded_at": datetime.utcnow()
        }
        collection.insert_one(file_data)
        print(f"✅ File URL for '{file_name}' successfully stored in MongoDB!")
    except Exception as e:
        print(f"❌ Failed to store file URL for '{file_name}' in MongoDB: {str(e)}")

# Function to find text files in the specified folder
def find_text_files(folder_path):
    """Find text files that match specific names in the specified folder."""
    text_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file in ["Documentation_client.txt", "Documentation_novice.txt", "Documentation_senior.txt"]:
                text_files.append(os.path.join(root, file))
    return text_files

# Main Execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <path_to_cloned_repo>")
        sys.exit(1)

    cloned_repo_path = sys.argv[1]

    if not os.path.isdir(cloned_repo_path):
        print("Invalid directory path provided.")
        sys.exit(1)

    print(f"Searching for text files in {cloned_repo_path}...")

    text_files = find_text_files(cloned_repo_path)

    if text_files:
        print(f"Found {len(text_files)} text file(s) to upload.")
        
        for file_path in text_files:
            file_name = os.path.basename(file_path)
            file_url, upload_message = upload_to_drive(file_path, file_name)  
            print(upload_message)
    else:
        print("❌ No text files found matching the specified names.")
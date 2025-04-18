import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "Raghavendra"
MONGO_COLLECTION = "Sastry"

# Google Drive Configuration
SERVICE_ACCOUNT_FILE = "fileuploaderapp-454310-9e8ab3e1bc5b.json"  # Replace with your correct path
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1YiRmfbNlhT_NJXEwe6QGJ-ApOH3xW-rR'  # Replace with your root Google Drive folder ID

# ---------------- GOOGLE DRIVE HELPERS ----------------

def authenticate_drive():
    """Authenticate and return a Google Drive API client."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("❌ Google Drive Service Account JSON missing!")
        return None
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)

def create_drive_folder(folder_name, parent_folder_id):
    """Creates a folder in Google Drive and returns its folder ID."""
    drive_service = authenticate_drive()
    if not drive_service:
        return None, "❌ Drive authentication failed while creating folder."

    try:
        query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            return items[0]['id'], f"📁 Folder '{folder_name}' already exists."

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
        return folder["id"], f"📁 Folder '{folder_name}' created successfully."
    except Exception as e:
        return None, f"❌ Error creating folder '{folder_name}': {str(e)}"

def upload_to_drive(file_path, file_name, repo_name, folder_id=FOLDER_ID):
    """Uploads a file to a Drive folder named after the repo."""
    drive_service = authenticate_drive()
    if not drive_service:
        return None, "❌ Google Drive authentication failed!"

    subfolder_id, folder_msg = create_drive_folder(repo_name, folder_id)
    print(folder_msg)
    if not subfolder_id:
        return None, folder_msg

    try:
        file_metadata = {"name": file_name, "parents": [subfolder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_id = uploaded_file.get("id")
        file_url = f"https://drive.google.com/file/d/{file_id}/view"

        store_file_url_in_mongodb(file_name, file_url, repo_name)

        return file_url, f"✅ File '{file_name}' uploaded to '{repo_name}' folder! [View File]({file_url})"
    except Exception as e:
        return None, f"❌ Upload failed for '{file_name}': {str(e)}"

# ---------------- MONGODB ----------------

def store_file_url_in_mongodb(file_name, file_url, repo_name):
    """Stores the file URL in MongoDB with associated repo."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        file_data = {
            "repo": repo_name,
            "file_name": file_name,
            "file_url": file_url,
            "uploaded_at": datetime.utcnow()
        }
        collection.insert_one(file_data)
        print(f"✅ File URL for '{file_name}' from repo '{repo_name}' stored in MongoDB!")
    except Exception as e:
        print(f"❌ Failed to store file URL in MongoDB: {str(e)}")

# ---------------- FILE SEARCH ----------------

def find_text_files(folder_path):
    """Find MD files that match specific names in the specified folder."""
    text_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file in ["Documentation_client.md", "Documentation_novice.md", "Documentation_senior.md"]:
                text_files.append(os.path.join(root, file))
    return text_files

# ---------------- MAIN ----------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <path_to_cloned_repo>")
        sys.exit(1)

    cloned_repo_path = sys.argv[1]

    if not os.path.isdir(cloned_repo_path):
        print("Invalid directory path provided.")
        sys.exit(1)

    repo_name = os.path.basename(os.path.normpath(cloned_repo_path))  # Get repo folder name
    print(f"🔍 Searching for Markdown files in: {cloned_repo_path}")

    text_files = find_text_files(cloned_repo_path)

    if text_files:
        print(f"📄 Found {len(text_files)} text file(s) to upload.")
        for file_path in text_files:
            file_name = os.path.basename(file_path)
            file_url, upload_message = upload_to_drive(file_path, file_name, repo_name)
            print(upload_message)
    else:
        print("❌ No text files found matching the specified names.")

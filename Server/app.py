import streamlit as st
import os
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from github import Github
from pymongo import MongoClient
from datetime import datetime

# Streamlit UI Configuration
st.set_page_config(page_title="Batch File Uploader", page_icon="📂", layout="centered")
st.title("📂 Batch Upload Files to Google Drive & Store in MongoDB")

# GitHub Repository Information
REPO_NAME = "raghavaa2506/CODELENS"
FOLDER_PATH = "LLM_Interaction"  # Folder containing text files
GITHUB_TOKEN = "raghava2506"  # Replace with your GitHub token

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
        st.error("❌ Google Drive Service Account JSON missing!")
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
        st.success(f"✅ File URL for '{file_name}' successfully stored in MongoDB!")
    except Exception as e:
        st.error(f"❌ Failed to store file URL for '{file_name}' in MongoDB: {str(e)}")

# Function to fetch all text files from the specified GitHub repository folder
def get_text_files_from_github(repo_name, folder_path, token):
    """Fetches the list of text files from the specified GitHub repository and folder."""
    try:
        g = Github(token) if token else Github()  # Use token if provided
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(folder_path)
        text_files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))  # Fetch nested files
            elif file_content.name.endswith('.txt'):
                text_files.append(file_content)

        return text_files
    except Exception as e:
        st.error(f"❌ Error fetching text files from GitHub: {str(e)}")
        return []

# Function to download a file from GitHub
def download_file_from_github(file, download_path):
    """Downloads the file from GitHub to a local path."""
    try:
        with open(download_path, 'wb') as f:
            f.write(file.decoded_content)
        return True
    except Exception as e:
        st.error(f"❌ Error downloading file '{file.name}': {str(e)}")
        return False

# Main Execution
st.subheader("📤 Uploading Text Files from GitHub to Google Drive")

# Fetch text files from GitHub folder
github_files = get_text_files_from_github(REPO_NAME, FOLDER_PATH, GITHUB_TOKEN)

if github_files:
    for file in github_files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            if download_file_from_github(file, temp_file.name):
                file_url, upload_message = upload_to_drive(temp_file.name, file.name)  
                st.write(upload_message)
                os.remove(temp_file.name)  # Clean up temporary file
else:
    st.write("❌ No text files found in the specified GitHub repository and folder.")

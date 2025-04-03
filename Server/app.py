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
st.set_page_config(page_title="File Uploader", page_icon="📂", layout="centered")
st.title("📂 Upload File to Google Drive,Store it in MongoDB"
" & Verify GitHub Repo")

# GitHub Repo Verification Section
st.subheader("🔗 Enter GitHub Repository URL")
github_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
github_token = st.text_input("GitHub Token (for private repos)", type="password")

def verify_github_repo(repo_url, token):
    """Verifies if a GitHub repository exists."""
    try:
        if "github.com/" not in repo_url:
            return False, "❌ Invalid GitHub URL!"

        repo_name = repo_url.split("github.com/")[-1]  # Extract user/repo
        g = Github(token) if token else Github()  # Use token if provided
        repo = g.get_repo(repo_name)
        return True, f"✅ Repository '{repo.full_name}' is valid!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

if github_url:
    if st.button("🔍 Verify GitHub Repo"):
        valid, message = verify_github_repo(github_url, github_token)
        st.success(message) if valid else st.error(message)

# File Upload Section
st.subheader("📤 Upload a File to Google Drive")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "jpg", "png", "zip"])

# Google Drive Authentication using Service Account
SERVICE_ACCOUNT_FILE = "fileuploaderapp-454310-b3fb5dbe37a4.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1YiRmfbNlhT_NJXEwe6QGJ-ApOH3xW-rR'  # Replace with actual folder ID

def authenticate_drive():
    """Authenticate and return a Google Drive API client."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        st.error("❌ Google Drive Service Account JSON missing!")
        return None
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def upload_to_drive(file, folder_id=FOLDER_ID):
    """Uploads a file to Google Drive under the correct account."""
    drive_service = authenticate_drive()
    if not drive_service:
        return "❌ Google Drive authentication failed!"
    
    # Use a temporary file to prevent permission issues
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.getbuffer())  # Save uploaded file
        temp_file_path = temp_file.name  # Get temp file path
    
    try:
        file_metadata = {"name": file.name, "parents": [folder_id] if folder_id else []}
        media = MediaFileUpload(temp_file_path, resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_id = uploaded_file.get("id")
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        # Store the file URL in MongoDB
        store_file_url_in_mongodb(file.name, file_url)
        
        return f"✅ File uploaded successfully! [View File]({file_url})"
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                st.warning(f"⚠️ Could not delete temp file: {e}")

def store_file_url_in_mongodb(file_name, file_url):
    """Stores the file URL in MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Raghavendra"]
        collection = db["Sastry"]
        file_data = {
            "file_name": file_name,
            "file_url": file_url,
            "uploaded_at": datetime.utcnow()  # Use datetime module for timestamp
        }
        collection.insert_one(file_data)
        st.success("✅ File URL successfully stored in MongoDB!")
    except Exception as e:
        st.error(f"❌ Failed to store file URL in MongoDB: {str(e)}")

if uploaded_file:
    st.write(f"📁 File selected: {uploaded_file.name}")
    if st.button("🚀 Upload to Google Drive"):
        upload_message = upload_to_drive(uploaded_file)  # Uses the correct folder ID
        st.success(upload_message) if "✅" in upload_message else st.error(upload_message)
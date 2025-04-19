// background.js with OAuth2 authentication
const MAIN_DRIVE_FOLDER_ID = "1YiRmfbNlhT_NJXEwe6QGJ-ApOH3xW-rR";

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "fetchDocumentation") {
    fetchDocumentation(request.repoName, request.fileName)
      .then(content => {
        sendResponse({ content });
      })
      .catch(error => {
        console.error("Error fetching documentation:", error);
        sendResponse({ error: error.message });
      });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});

// Get OAuth2 token
async function getAuthToken() {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, function(token) {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(token);
      }
    });
  });
}

// Find and fetch documentation
async function fetchDocumentation(repoName, fileName) {
  try {
    console.log(`Fetching documentation for repo: ${repoName}, file: ${fileName}`);
    
    // Get auth token
    const token = await getAuthToken();
    
    // Find the repo folder within the main folder
    const repoFolderId = await findRepoFolder(repoName, token);
    if (!repoFolderId) {
      throw new Error(`Repository folder "${repoName}" not found`);
    }
    
    console.log(`Found repo folder with ID: ${repoFolderId}`);
    
    // Find the documentation file within the repo folder
    const fileId = await findFileInFolder(repoFolderId, fileName, token);
    if (!fileId) {
      throw new Error(`File "${fileName}" not found in repository`);
    }
    
    console.log(`Found file with ID: ${fileId}`);
    
    // Download the file content
    const content = await downloadFileContent(fileId, token);
    return content;
  } catch (error) {
    console.error("Error in fetchDocumentation:", error);
    throw error;
  }
}

// Find repository folder within main folder
async function findRepoFolder(repoName, token) {
  const query = `'${MAIN_DRIVE_FOLDER_ID}' in parents and name = '${repoName}' and mimeType = 'application/vnd.google-apps.folder'`;
  
  try {
    console.log(`Searching for repo folder with query: ${query}`);
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}`, 
      { 
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        } 
      }
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Google Drive API Error (${response.status}):`, errorText);
      throw new Error(`Google Drive API Error: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Folder search response:", data);
    
    if (data.files && data.files.length > 0) {
      return data.files[0].id;
    } else {
      return null;
    }
  } catch (error) {
    console.error("Error finding repo folder:", error);
    throw error;
  }
}

// Find file within folder
async function findFileInFolder(folderId, fileName, token) {
  const query = `'${folderId}' in parents and name = '${fileName}'`;
  
  try {
    console.log(`Searching for file with query: ${query}`);
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}`, 
      { 
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        } 
      }
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Google Drive API Error (${response.status}):`, errorText);
      throw new Error(`Google Drive API Error: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("File search response:", data);
    
    if (data.files && data.files.length > 0) {
      return data.files[0].id;
    } else {
      return null;
    }
  } catch (error) {
    console.error("Error finding file:", error);
    throw error;
  }
}

// Download file content
async function downloadFileContent(fileId, token) {
  try {
    console.log(`Downloading file content for ID: ${fileId}`);
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`, 
      { 
        headers: { 
          'Authorization': `Bearer ${token}` 
        } 
      }
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`File download error (${response.status}):`, errorText);
      throw new Error(`Failed to download file: ${response.status}`);
    }
    
    const content = await response.text();
    return content;
  } catch (error) {
    console.error("Error downloading content:", error);
    throw error;
  }
}
// background.js
import { marked } from 'marked';

chrome.runtime.onInstalled.addListener(() => {
  console.log('CodeLens extension installed');
});

// Make marked available to content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getMarkedParser") {
    // Send the marked parser serialized as a string to the content script
    sendResponse({ 
      success: true,
      markedFunction: marked.parse.toString()
    });
    return true;
  }
  
  if (request.action === "fetchGitHubAPI") {
    // Use background script to make API requests to avoid CORS issues
    fetch(request.url)
      .then(response => {
        return response.text();
      })
      .then(text => {
        sendResponse({ success: true, data: text });
      })
      .catch(error => {
        sendResponse({ success: false, error: error.message });
      });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
  
  if (request.action === "saveFileWithDialog" || request.action === "saveFile") {
    try {
      // Convert content to a data URL to avoid using URL.createObjectURL
      const contentString = request.content;
      const contentType = 'text/markdown';
      const base64Content = btoa(unescape(encodeURIComponent(contentString)));
      const dataUrl = `data:${contentType};base64,${base64Content}`;
      
      // Use chrome.downloads.download with saveAs: true to show the native file browser dialog
      chrome.downloads.download({
        url: dataUrl,
        filename: request.filename || 'document.md',
        saveAs: true // This forces the browser to show the "Save As" dialog
      }, (downloadId) => {
        if (chrome.runtime.lastError) {
          console.error("Download error:", chrome.runtime.lastError);
          sendResponse({ 
            success: false, 
            error: chrome.runtime.lastError.message 
          });
        } else {
          // No need to revoke a data URL
          sendResponse({ success: true });
        }
      });
    } catch (error) {
      console.error("Error initiating download:", error);
      sendResponse({ 
        success: false, 
        error: error.message 
      });
    }
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});
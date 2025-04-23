// content.js 

(function () {
    let button = null;
    let optionsMenu = null;
    let overlay = null;
    let githubPane = null;
    let isEditing = false;
    let currentMarkdownContent = null;
    let markedInstance = null;
    
    // Documentation files to look for
    const USER_DOCUMENTATION_FILES = {
      "Novice Developer": "Documentation_novice.md",
      "Client": "Documentation_client.md",
      "Senior Developer": "Documentation_senior.md"
    };
  
    function isRepoPage() {
      return /^https:\/\/github\.com\/[^\/]+\/[^\/]+$/.test(window.location.href);
    }
  
    function getRepoInfo() {
      const pathParts = window.location.pathname.split('/');
      if (pathParts.length >= 3) {
        return {
          owner: pathParts[1],
          repo: pathParts[2]
        };
      }
      return null;
    }
  
    function addButton() {
      if (!isRepoPage()) { 
        cleanup(); 
        return; 
      }
      
      if (button) return;
  
      button = document.createElement("div");
      button.id = "codelens-main-button";
      button.innerText = "CodeLens";
      button.addEventListener("click", toggleOptionsMenu);
      document.body.appendChild(button);
    }
  
    function toggleOptionsMenu() {
      if (optionsMenu) { 
        optionsMenu.remove(); 
        optionsMenu = null; 
        return; 
      }
  
      optionsMenu = document.createElement("div");
      optionsMenu.id = "overlay-options-menu";
  
      const expandBtn = document.createElement("button");
      expandBtn.innerText = "Expand";
      expandBtn.addEventListener("click", showOverlay);
  
      const vanishBtn = document.createElement("button");
      vanishBtn.innerText = "Vanish";
      vanishBtn.classList.add("vanish");
      vanishBtn.addEventListener("click", cleanup);
  
      optionsMenu.appendChild(expandBtn);
      optionsMenu.appendChild(vanishBtn);
      document.body.appendChild(optionsMenu);
    }
  
    function showOverlay() {
      if (overlay || githubPane) return;
  
      // Store the existing content in the githubPane
      githubPane = document.createElement("div");
      githubPane.id = "github-pane";
      githubPane.style.width = "50%";
      githubPane.style.float = "left";
      githubPane.style.overflowY = "auto";
      githubPane.style.height = "100vh";
      
      while (document.body.firstChild) {
        githubPane.appendChild(document.body.firstChild);
      }
      document.body.appendChild(githubPane);
  
      // Create the overlay that will take the right half of the screen
      overlay = document.createElement("div");
      overlay.id = "codelens-overlay";
      overlay.style.width = "50%";
      overlay.style.float = "right";
      overlay.style.height = "100vh";
      overlay.style.overflowY = "auto";
      overlay.style.padding = "20px";
      overlay.style.boxSizing = "border-box";
  
      const imgURL = chrome.runtime.getURL("images/basic.jpg");
      overlay.style.background = `
        url(${imgURL}) no-repeat center center / cover,
        linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8))
      `;
  
      const heading = document.createElement("h2");
      heading.innerText = "Whom do you want to generate the document for?";
      overlay.appendChild(heading);
  
      const choices = ["Novice Developer", "Client", "Senior Developer"];
      const optionGroup = document.createElement("div");
      optionGroup.className = "radio-group";
  
      let selected = null;
      choices.forEach(text => {
        const btn = document.createElement("button");
        btn.className = "choice-button";
        btn.innerText = text;
        btn.addEventListener("click", () => {
          optionGroup.querySelectorAll("button").forEach(b => b.classList.remove("selected"));
          btn.classList.add("selected");
          selected = text;
          generateBtn.style.display = "block";
        });
        optionGroup.appendChild(btn);
      });
      overlay.appendChild(optionGroup);
  
      const generateBtn = document.createElement("button");
      generateBtn.className = "display-button";
      generateBtn.innerText = "Find Documentation";
      generateBtn.style.display = "none";
      generateBtn.addEventListener("click", () => {
        if (!selected) return;
  
        const fileName = USER_DOCUMENTATION_FILES[selected];
        
        // Clear any previous content
        const existingContent = overlay.querySelector(".markdown-content");
        if (existingContent) {
          existingContent.remove();
        }
        
        // Show loading indicator while searching for the file
        showSearchingIndicator(overlay, fileName);
        
        // Start searching for the file in the repository
        searchRepositoryForFile(fileName, selected);
      });
      overlay.appendChild(generateBtn);
  
      const closeBtn = document.createElement("button");
      closeBtn.id = "close-overlay-btn";
      closeBtn.innerText = "Close";
      closeBtn.style.position = "absolute";
      closeBtn.style.top = "10px";
      closeBtn.style.right = "10px";
      closeBtn.addEventListener("click", cleanup);
      overlay.appendChild(closeBtn);
  
      document.body.appendChild(overlay);
      
      // Load markdown parser
      loadMarkdownParser();
    }
    
    function loadMarkdownParser() {
      if (!markedInstance) {
        // Request marked parser from background script
        chrome.runtime.sendMessage({ action: "getMarkedParser" }, function(response) {
          if (response && response.success) {
            // Create a function from the string representation
            try {
              // Create a function from the serialized marked.parse function
              markedInstance = new Function('markdown', 
                `return (${response.markedFunction})(markdown);`
              );
              
              // If there are any markdown elements waiting to be rendered, render them now
              const pendingElements = document.querySelectorAll('.raw-markdown');
              pendingElements.forEach(elem => {
                const parentElement = elem.parentNode;
                const markdown = elem.textContent;
                renderMarkdown(parentElement, markdown);
              });
            } catch (error) {
              console.error("Error initializing marked parser:", error);
            }
          }
        });
      }
    }
  
    function showSearchingIndicator(container, fileName) {
      const searchingDiv = document.createElement("div");
      searchingDiv.id = "searching-indicator";
      searchingDiv.className = "loading-indicator";
      searchingDiv.innerHTML = `
        <div class="spinner"></div>
        <p>Searching repository for ${fileName}...</p>
      `;
      container.appendChild(searchingDiv);
    }
  
    function searchRepositoryForFile(fileName, userType) {
      const repoInfo = getRepoInfo();
      if (!repoInfo) {
        showError(overlay, "Could not determine repository information.");
        return;
      }
  
      // First, get the master branch or default branch
      fetchDefaultBranch(repoInfo.owner, repoInfo.repo)
        .then(defaultBranch => {
          // Now recursively search the repository
          return searchDirectoryForFile(repoInfo.owner, repoInfo.repo, defaultBranch, "", fileName);
        })
        .then(fileInfo => {
          if (fileInfo) {
            // Found the file - now fetch its content
            return fetchFileContent(fileInfo.download_url);
          } else {
            throw new Error(`Documentation file ${fileName} not found in the repository.`);
          }
        })
        .then(content => {
          // Remove searching indicator
          const searchingIndicator = document.getElementById("searching-indicator");
          if (searchingIndicator) {
            searchingIndicator.remove();
          }
          
          // Store the markdown content for editing
          currentMarkdownContent = content.content;
          
          // Display the markdown content
          showMarkdownContent(overlay, content.content, content.path);
        })
        .catch(error => {
          // Remove searching indicator
          const searchingIndicator = document.getElementById("searching-indicator");
          if (searchingIndicator) {
            searchingIndicator.remove();
          }
          
          showError(overlay, error.message);
        });
    }
    
    function fetchDefaultBranch(owner, repo) {
      return fetch(`https://api.github.com/repos/${owner}/${repo}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Failed to fetch repository info: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          return data.default_branch || 'master'; // Default to 'master' if no default branch found
        });
    }
  
    function searchDirectoryForFile(owner, repo, branch, path, fileName) {
      return fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Failed to fetch directory contents: ${response.status}`);
          }
          return response.json();
        })
        .then(items => {
          // Check if fileName is in this directory
          const foundFile = items.find(item => 
            item.type === 'file' && 
            (item.name.toLowerCase() === fileName.toLowerCase())
          );
          
          if (foundFile) {
            return foundFile; // File found
          }
          
          // If not found, search in subdirectories
          const subDirPromises = items
            .filter(item => item.type === 'dir')
            .map(dir => {
              const newPath = path ? `${path}/${dir.name}` : dir.name;
              return searchDirectoryForFile(owner, repo, branch, newPath, fileName);
            });
          
          // Return the first non-null result from subdirectories
          return Promise.all(subDirPromises)
            .then(results => results.find(result => result !== null) || null);
        });
    }
  
    function fetchFileContent(downloadUrl) {
      return fetch(downloadUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Failed to fetch file content: ${response.status}`);
          }
          return response.text();
        })
        .then(text => {
          return {
            content: text,
            path: downloadUrl.split('/').slice(-2).join('/')
          };
        });
    }
  
    function showMarkdownContent(container, markdown, path) {
      const contentDiv = document.createElement("div");
      contentDiv.className = "markdown-content";
      
      // Add the path information
      const pathInfo = document.createElement("div");
      pathInfo.className = "path-info";
      pathInfo.innerHTML = `<p><strong>Source:</strong> ${path}</p>`;
      contentDiv.appendChild(pathInfo);
      
      // Create the markdown view container
      const contentElement = document.createElement("div");
      contentElement.className = "markdown-body";
      contentElement.id = "markdown-view";
      
      // Create editor container (initially hidden)
      const editorContainer = document.createElement("div");
      editorContainer.className = "markdown-editor-container";
      editorContainer.id = "markdown-editor-container";
      editorContainer.style.display = "none";
      
      // Create the editor element
      const editorElement = document.createElement("div");
      editorElement.className = "markdown-editor";
      editorElement.id = "markdown-editor";
      
      // Create textarea for editing
      const textArea = document.createElement("textarea");
      textArea.id = "markdown-textarea";
      textArea.value = markdown;
      textArea.spellcheck = false;
      textArea.addEventListener('input', function() {
        // Update preview on textarea change if in split view mode
        if (document.getElementById('markdown-preview')) {
          renderMarkdownPreview(textArea.value);
        }
      });
      
      editorElement.appendChild(textArea);
      editorContainer.appendChild(editorElement);
      
      // Create preview pane for split view (initially hidden)
      const previewPane = document.createElement("div");
      previewPane.className = "markdown-preview";
      previewPane.id = "markdown-preview";
      previewPane.style.display = "none";
      editorContainer.appendChild(previewPane);
      
      // Render the markdown in the view container
      renderMarkdown(contentElement, markdown);
      
      // Create action buttons container
      const actionsContainer = document.createElement("div");
      actionsContainer.className = "file-action-buttons";
      
      // Edit button
      const editBtn = document.createElement("button");
      editBtn.className = "file-button edit-button";
      editBtn.innerText = "Edit";
      editBtn.addEventListener("click", () => {
        toggleEdit(contentElement, editorContainer, editBtn);
      });
      
      // Split view toggle button (initially hidden)
      const splitViewBtn = document.createElement("button");
      splitViewBtn.className = "file-button split-view-button";
      splitViewBtn.innerText = "Split View";
      splitViewBtn.style.display = "none";
      splitViewBtn.addEventListener("click", () => {
        toggleSplitView(editorElement, previewPane, textArea.value, splitViewBtn);
      });
      
      // Save button
      const saveBtn = document.createElement("button");
      saveBtn.className = "file-button save-button";
      saveBtn.innerText = "Save";
      saveBtn.addEventListener("click", () => {
        // Get current content from editor if in edit mode, or use stored content
        const contentToSave = isEditing ? 
          document.getElementById('markdown-textarea').value : 
          currentMarkdownContent;
        
        showSaveDialog(contentToSave);
      });
      
      actionsContainer.appendChild(editBtn);
      actionsContainer.appendChild(splitViewBtn);
      actionsContainer.appendChild(saveBtn);
      
      contentDiv.appendChild(contentElement);
      contentDiv.appendChild(editorContainer);
      contentDiv.appendChild(actionsContainer);
      
      container.appendChild(contentDiv);
    }
    
    function renderMarkdown(element, markdown) {
      if (markedInstance) {
        try {
          element.innerHTML = markedInstance(markdown);
          
          // Add syntax highlighting if possible
          if (typeof hljs !== 'undefined') {
            element.querySelectorAll('pre code').forEach((block) => {
              hljs.highlightBlock(block);
            });
          }
        } catch (error) {
          console.error("Error rendering markdown:", error);
          element.innerHTML = `<p class="error">Error rendering markdown: ${error.message}</p>`;
        }
      } else {
        // If marked.js is not loaded yet, display raw text temporarily
        const preElement = document.createElement("pre");
        preElement.className = "raw-markdown";
        preElement.textContent = markdown;
        element.innerHTML = '';
        element.appendChild(preElement);
        
        // Load marked.js
        loadMarkdownParser();
      }
    }
    
    function renderMarkdownPreview(markdown) {
      const previewElement = document.getElementById('markdown-preview');
      if (previewElement) {
        renderMarkdown(previewElement, markdown);
      }
    }
    
    function toggleSplitView(editorElement, previewPane, markdown, toggleButton) {
      if (previewPane.style.display === "none") {
        // Enable split view
        previewPane.style.display = "block";
        editorElement.classList.add("split-mode");
        previewPane.classList.add("split-mode");
        toggleButton.innerText = "Editor Only";
        
        // Render markdown in preview pane
        renderMarkdown(previewPane, markdown);
      } else {
        // Disable split view
        previewPane.style.display = "none";
        editorElement.classList.remove("split-mode");
        previewPane.classList.remove("split-mode");
        toggleButton.innerText = "Split View";
      }
    }
    
    function toggleEdit(viewElement, editorContainer, editBtn) {
      if (isEditing) {
        // Switch back to view mode
        const textarea = document.getElementById('markdown-textarea');
        currentMarkdownContent = textarea.value;
        
        renderMarkdown(viewElement, currentMarkdownContent);
        
        viewElement.style.display = "block";
        editorContainer.style.display = "none";
        editBtn.innerText = "Edit";
        
        // Hide split view button
        const splitViewBtn = document.querySelector('.split-view-button');
        if (splitViewBtn) {
          splitViewBtn.style.display = "none";
        }
        
      } else {
        // Switch to edit mode
        document.getElementById('markdown-textarea').value = currentMarkdownContent;
        viewElement.style.display = "none";
        editorContainer.style.display = "block";
        editBtn.innerText = "Preview";
        
        // Show split view button
        const splitViewBtn = document.querySelector('.split-view-button');
        if (splitViewBtn) {
          splitViewBtn.style.display = "inline-block";
        }
        
        // Focus the textarea
        document.getElementById('markdown-textarea').focus();
      }
      
      isEditing = !isEditing;
    }
    
    function showSaveDialog(content) {
      // Send a message to the background script to trigger the native file dialog
      chrome.runtime.sendMessage({
        action: "saveFileWithDialog",
        content: content,
        filename: "documentation.md"
      }, (response) => {
        if (response && response.success) {
          // Show success message
          showNotification("File was saved successfully!", "success");
        } else if (response && response.error) {
          // Show error message
          showNotification(`Error saving file: ${response.error}`, "error");
        }
      });
    }
    
    function showNotification(message, type) {
      const notificationDiv = document.createElement("div");
      notificationDiv.className = type === "error" ? "error-message" : "success-message";
      notificationDiv.innerText = message;
      
      const container = document.querySelector(".file-action-buttons");
      container.appendChild(notificationDiv);
      
      // Remove the message after a few seconds
      setTimeout(() => {
        notificationDiv.remove();
      }, type === "error" ? 5000 : 3000);
    }
  
    function showError(container, message) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "markdown-content error";
      errorDiv.innerHTML = `<p class="error-message">${message}</p>`;
      container.appendChild(errorDiv);
    }
  
    function cleanup() {
      if (overlay) { overlay.remove(); overlay = null; }
      if (githubPane) {
        while (githubPane.firstChild) {
          document.body.appendChild(githubPane.firstChild);
        }
        githubPane.remove(); githubPane = null;
      }
      if (optionsMenu) { optionsMenu.remove(); optionsMenu = null; }
      if (button) { button.remove(); button = null; }
      isEditing = false;
      currentMarkdownContent = null;
    }
  
    // Listen for URL changes to update the button
    let lastUrl = location.href;
    new MutationObserver(() => {
      if (location.href !== lastUrl) {
        lastUrl = location.href;
        cleanup();
        addButton();
      }
    }).observe(document, { subtree: true, childList: true });
  
    // Initialize button on page load
    addButton();
  })();
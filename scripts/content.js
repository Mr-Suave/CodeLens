(function () {
  let button = null;
  let optionsMenu = null;
  let overlay = null;
  let githubPane = null;
  
  // Configuration - you should move this to a secure backend
  const MAIN_DRIVE_FOLDER_ID = "https://drive.google.com/drive/u/0/folders/1YiRmfbNlhT_NJXEwe6QGJ-ApOH3xW-rR";
  
  // File name mappings
  const USER_DOCUMENTATION_FILES = {
    "Novice Developer": "Documentation_novice.md",
    "Client": "Documentation_client.md",
    "Senior Developer": "Documentation_senior.md"
  };

  function isRepoPage() {
    return /^https:\/\/github\.com\/[^\/]+\/[^\/]+$/.test(window.location.href);
  }

  function getRepoName() {
    const pathParts = window.location.pathname.split('/');
    return pathParts.length >= 3 ? pathParts[2] : null;
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
    generateBtn.innerText = "Display";
    generateBtn.style.display = "none";
    generateBtn.addEventListener("click", () => {
      if (!selected) return;

      const repo = getRepoName();
      if (!repo) {
        showError(overlay, "Could not determine repository name.");
        return;
      }

      const fileName = USER_DOCUMENTATION_FILES[selected];
      
      // Clear any previous content
      const existingContent = overlay.querySelector(".markdown-content");
      if (existingContent) {
        existingContent.remove();
      }
      
      // Show loading indicator
      const loadingDiv = document.createElement("div");
      loadingDiv.innerText = "Loading documentation...";
      loadingDiv.style.margin = "20px 0";
      overlay.appendChild(loadingDiv);

      // Generate repo name variants to try
      const repoVariants = [
        repo,                      // Original
        repo.toLowerCase(),        // lowercase
        repo.toUpperCase(),        // UPPERCASE
        capitalizeFirstLetter(repo) // Capitalized
      ];
      
      fetchDocumentationFromBackend(repoVariants, fileName, loadingDiv, overlay);
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
  }

  // Helper function to capitalize the first letter
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
  }

  // Fetch documentation through your backend service
  function fetchDocumentationFromBackend(repoVariants, fileName, loadingDiv, overlay) {
    let triedVariants = [];
    tryNextVariant(0);
    
    function tryNextVariant(index) {
      if (index >= repoVariants.length) {
        loadingDiv.remove();
        showVariantsError(overlay, triedVariants, fileName);
        return;
      }
      
      const currentVariant = repoVariants[index];
      triedVariants.push(currentVariant);
      
      loadingDiv.innerText = `Searching for documentation in ${currentVariant}...`;
      
      // Use message passing to communicate with the background script
      chrome.runtime.sendMessage({
        action: "fetchDocumentation",
        repoName: currentVariant,
        fileName: fileName
      }, response => {
        if (chrome.runtime.lastError) {
          console.error("Runtime error:", chrome.runtime.lastError);
          tryNextVariant(index + 1);
          return;
        }
        
        if (response.error) {
          console.log(`Failed with variant ${currentVariant}: ${response.error}`);
          tryNextVariant(index + 1);
        } else if (response.content) {
          loadingDiv.remove();
          showMarkdownContent(overlay, response.content);
        } else {
          console.log(`No content returned for ${currentVariant}`);
          tryNextVariant(index + 1);
        }
      });
    }
  }

  // Helper function to show markdown content
  function showMarkdownContent(container, markdown) {
    const contentDiv = document.createElement("div");
    contentDiv.className = "markdown-content";
    contentDiv.innerHTML = `
      <pre style="white-space: pre-wrap; background: white; padding: 20px; 
      border-radius: 8px; max-height: 80vh; overflow-y: auto;">${markdown}</pre>
    `;
    container.appendChild(contentDiv);
  }

  // Helper function to show error
  function showError(container, message) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "markdown-content error";
    errorDiv.innerHTML = `<p style="color: red;">Error: ${message}</p>`;
    container.appendChild(errorDiv);
  }

  // Helper function to show variants error
  function showVariantsError(container, variants, fileName) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "markdown-content error";
    errorDiv.innerHTML = `
      <p style="color: red;">Error: Could not find documentation.</p>
      <p>We tried the following repository names:</p>
      <ul>
        ${variants.map(v => `<li>${v}</li>`).join('')}
      </ul>
      <p>Make sure a folder with one of these names exists in Google Drive and contains ${fileName}.</p>
      <p>Please check that the backend service is running and properly configured.</p>
    `;
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
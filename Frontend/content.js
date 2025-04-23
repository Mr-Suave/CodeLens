
  /* content.js */
  function isGitHubRepoPage() {
    return /^https:\/\/github\.com\/[^\/]+\/[^\/]+(\/)?$/.test(window.location.href);
  }
  
  function createCodeLensButton() {
    const button = document.createElement('div');
    button.id = 'codelens-btn';
    button.innerText = 'CodeLens';
    document.body.appendChild(button);
    
    button.onclick = () => {
      const overlay = document.createElement('div');
      overlay.id = 'codelens-overlay';
      button.style.display = 'none';
      const title = document.createElement('h2');
      title.className = 'codelens-title';
      title.innerText = 'CodeLens';
      overlay.appendChild(title);

      const subtitle = document.createElement('h3');
      subtitle.className = 'codelens-subtitle';
      subtitle.innerText = 'Documentation making just got easier!';;

      overlay.appendChild(subtitle);
      
      const docBtn = document.createElement('button');
      docBtn.className = 'overlay-btn';
      docBtn.innerText = 'View Documentation For the Repository';
  
      const graphBtn = document.createElement('button');
      graphBtn.className = 'overlay-btn';
      graphBtn.innerText = 'View Commit Messages Graph';
  
      overlay.appendChild(docBtn);
      overlay.appendChild(graphBtn);
  
      document.body.appendChild(overlay);

      //close overlay when clicking outside the overlay
      function handleOutsideClick(e) {
        const rect = overlay.getBoundingClientRect();
        if (e.clientX < rect.left) {
          overlay.remove();
          button.style.display = 'block';
          document.removeEventListener('click', handleOutsideClick);
        }
      }

      document.addEventListener('click', handleOutsideClick);
    };
  }
  
  if (isGitHubRepoPage()) {
    createCodeLensButton();
  }
(function () {
  let button = null;
  let optionsMenu = null;
  let overlay = null;

  function addButton() {
    if (!/^https:\/\/github\.com\/[^\/]+\/[^\/]+$/.test(window.location.href)) {
        if (button) {
            button.remove();
            button = null;
        }
        if (optionsMenu) {
            optionsMenu.remove();
            optionsMenu = null;
        }
        if (overlay) {
            overlay.remove();
            overlay = null;
        }
        return;
    }

    if (!button) {
        button = document.createElement("div");
        button.innerText = "≡";
        button.style.position = "fixed";
        button.style.top = "120px";
        button.style.right = "15px";
        button.style.width = "80px"; // rectangular width
        button.style.height = "40px"; // rectangular height
        button.style.background = "#2ea44f";
        button.style.color = "white";
        button.style.borderRadius = "8px"; // softer corners instead of circle
        button.style.display = "flex";
        button.style.alignItems = "center";
        button.style.justifyContent = "center";
        button.style.fontSize = "20px";
        button.style.cursor = "pointer";
        button.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.2)";
        button.style.zIndex = "1000";

        button.addEventListener("click", toggleOptionsMenu);
        document.body.appendChild(button);
    }
}


  function toggleOptionsMenu() {
      if (optionsMenu) {
          optionsMenu.remove();
          optionsMenu = null;
          return;
      }

      optionsMenu = document.createElement("div");
      optionsMenu.style.position = "fixed";
      optionsMenu.style.top = "140px";
      optionsMenu.style.right = "20px";
      optionsMenu.style.background = "white";
      optionsMenu.style.border = "1px solid #ccc";
      optionsMenu.style.borderRadius = "8px";
      optionsMenu.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.2)";
      optionsMenu.style.padding = "10px";
      optionsMenu.style.display = "flex";
      optionsMenu.style.flexDirection = "column";
      optionsMenu.style.zIndex = "1001";

      let expandButton = document.createElement("button");
      expandButton.innerText = "Expand";
      expandButton.style.padding = "10px";
      expandButton.style.border = "none";
      expandButton.style.background = "#007bff";
      expandButton.style.color = "white";
      expandButton.style.cursor = "pointer";
      expandButton.style.marginBottom = "5px";
      expandButton.addEventListener("click", showOverlay);

      let vanishButton = document.createElement("button");
      vanishButton.innerText = "Vanish";
      vanishButton.style.padding = "10px";
      vanishButton.style.border = "none";
      vanishButton.style.background = "#cc0000";
      vanishButton.style.color = "white";
      vanishButton.style.cursor = "pointer";
      vanishButton.addEventListener("click", function () {
          button.remove();
          optionsMenu.remove();
          if (overlay) overlay.remove();
          button = null;
          optionsMenu = null;
          overlay = null;
      });

      optionsMenu.appendChild(expandButton);
      optionsMenu.appendChild(vanishButton);
      document.body.appendChild(optionsMenu);
  }

  function showOverlay() {
      if (overlay) return;

      overlay = document.createElement("div");
      overlay.style.position = "fixed";
      overlay.style.top = "0";
      overlay.style.right = "0";
      overlay.style.width = "30%"; // Covers right side
      overlay.style.height = "100%";
      overlay.style.background = "rgba(255, 255, 255, 0.95)";
      overlay.style.boxShadow = "-2px 0px 10px rgba(0, 0, 0, 0.2)";
      overlay.style.padding = "20px";
      overlay.style.zIndex = "1002";
      overlay.style.overflowY = "auto";

      let heading = document.createElement("h2");
      heading.innerText = "CodeLens";
      heading.style.color = "#333";

      let closeButton = document.createElement("button");
      closeButton.innerText = "Close";
      closeButton.style.marginTop = "10px";
      closeButton.style.padding = "8px";
      closeButton.style.border = "none";
      closeButton.style.background = "#ff4d4d";
      closeButton.style.color = "white";
      closeButton.style.cursor = "pointer";
      closeButton.addEventListener("click", function () {
          overlay.remove();
          overlay = null;
      });

      overlay.appendChild(heading);
      overlay.appendChild(closeButton);
      document.body.appendChild(overlay);
  }

  let lastUrl = location.href;
  new MutationObserver(() => {
      if (location.href !== lastUrl) {
          lastUrl = location.href;
          addButton();
      }
  }).observe(document, { subtree: true, childList: true });

  addButton();
})();

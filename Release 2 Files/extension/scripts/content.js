function injectToggleButton() {
    let existingButton = document.querySelector("#codelens-toggle");
    if (existingButton) return; // Prevent duplicates

    let button = document.createElement("button");
    button.id = "codelens-toggle";
    button.innerText = "Summarise";
    document.body.appendChild(button);

    button.addEventListener("click", () => {
        let sidebar = document.getElementById("codelens-sidebar");
        if (sidebar) {
            sidebar.classList.remove("slide-in");
            setTimeout(() => sidebar.remove(), 300);
        } else {
            injectSidebar();
        }
    });
}

function injectSidebar() {
    let sidebar = document.createElement("div");
    sidebar.id = "codelens-sidebar";
    sidebar.innerHTML = `
        <div id="codelens-header">
            <span>🚀 CodeLens</span>
            <button id="codelens-close">✖</button>
        </div>
        <div id="codelens-content">
            <h3>📂 Repository Info</h3>
            <p><strong>Repo Name:</strong> <span id="repo-name">Loading...</span></p>
            <p><strong>Description:</strong> <span id="repo-desc">Loading...</span></p>
        </div>
    `;
    document.body.appendChild(sidebar);
    setTimeout(() => sidebar.classList.add("slide-in"), 10);

    document.getElementById("codelens-close").addEventListener("click", () => {
        sidebar.classList.remove("slide-in");
        setTimeout(() => sidebar.remove(), 300);
    });
}

// Run script after DOM loads
document.addEventListener("DOMContentLoaded", injectToggleButton);
setTimeout(injectToggleButton, 2000); // Backup in case it fails

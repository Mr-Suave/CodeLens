(function () {
    // Prevent duplicate injection
    if (document.getElementById("codelens-button")) return;

    // Create floating button
    let button = document.createElement("button");
    button.id = "codelens-button";
    button.innerText = "📜 CodeLens";
    document.body.appendChild(button);

    // Create sidebar (initially hidden)
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
            <hr>
            <button id="fetch-details">🔍 Get Repo Details</button>
            <button id="highlight-code">🎨 Highlight Code</button>
        </div>
    `;

    document.body.appendChild(sidebar);

    // Click button to open sidebar
    button.addEventListener("click", () => {
        sidebar.classList.add("slide-in");
    });

    // Close sidebar
    document.getElementById("codelens-close").addEventListener("click", () => {
        sidebar.classList.remove("slide-in");
    });

    // Fetch repo details
    document.getElementById("fetch-details").addEventListener("click", () => {
        let repoName = document.querySelector("strong.mr-2 a")?.innerText || "Unknown";
        let description = document.querySelector("p.f4.mt-3")?.innerText || "No description available.";
        document.getElementById("repo-name").innerText = repoName;
        document.getElementById("repo-desc").innerText = description;
    });

    // Highlight code
    document.getElementById("highlight-code").addEventListener("click", () => {
        document.querySelectorAll("pre").forEach((codeBlock) => {
            codeBlock.style.background = "#f4f4f4";
            codeBlock.style.padding = "10px";
            codeBlock.style.borderRadius = "5px";
            codeBlock.style.border = "1px solid #ddd";
        });
        alert("Code blocks highlighted!");
    });

})();

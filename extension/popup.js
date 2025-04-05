document.getElementById("openSidebar").addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (tab.url.includes("github.com")) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ["scripts/content.js"]
        });
    } else {
        alert("Please open a GitHub repository to use CodeLens.");
    }
});

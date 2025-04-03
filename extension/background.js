chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete" && tab.url.includes("github.com")) {
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ["scripts/content.js"]
        });
    }
});

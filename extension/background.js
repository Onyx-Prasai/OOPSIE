// OOPSIE Chrome Extension Service Worker

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "oopsie-analyze-error",
    title: "Analyze Error with OOPSIE 🚀",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "oopsie-analyze-error" && info.selectionText) {
    chrome.storage.local.set({ pendingError: info.selectionText }, () => {
      chrome.action.openPopup();
    });
  }
});

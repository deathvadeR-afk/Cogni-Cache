// Event-based service worker for Chrome Side Panel
// This file handles extension lifecycle events

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
    console.log('Cognitive Cache extension installed');

    // Create context menu for links and text selection
    chrome.contextMenus.create({
        id: 'save-link',
        title: 'Save Link to Cognitive Cache',
        contexts: ['link']
    });

    chrome.contextMenus.create({
        id: 'save-selection',
        title: 'Save Selection to Cognitive Cache',
        contexts: ['selection']
    });

    // Set default storage values
    chrome.storage.local.set({
        isFirstRun: true,
        sourceCount: 0,
        chatHistory: []
    });
});

// Handle side panel button click
chrome.action.onClicked.addListener(async (tab) => {
    await chrome.sidePanel.open({ windowId: tab.windowId });
});

// Handle keyboard shortcut
chrome.commands.onCommand.addListener(async (command) => {
    if (command === 'save-context') {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, { action: 'saveContext' });
    }
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === 'save-link' && info.linkUrl) {
        chrome.tabs.sendMessage(tab.id, {
            action: 'saveLink',
            url: info.linkUrl
        });
    } else if (info.menuItemId === 'save-selection' && info.selectionText) {
        chrome.tabs.sendMessage(tab.id, {
            action: 'saveSelection',
            text: info.selectionText
        });
    }
});

// Listen for messages from content script or side panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'updateBadge') {
        chrome.action.setBadgeText({ text: request.count.toString() });
        chrome.action.setBadgeBackgroundColor({ color: '#007bff' });
    } else if (request.action === 'getTabUrl') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            sendResponse({ url: tabs[0]?.url || '' });
        });
        return true;
    }
});
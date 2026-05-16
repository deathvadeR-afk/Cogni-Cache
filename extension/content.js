// Content script for extracting page content
// Used by the side panel to get readable content from the current page

// Check if current page is an article or YouTube video
function isArticlePage() {
    // Check for common article indicators
    const articleSelectors = [
        'article',
        '[role="article"]',
        '.article-content',
        '.post-content',
        '.entry-content'
    ];

    for (const selector of articleSelectors) {
        if (document.querySelector(selector)) return true;
    }

    // Check for sufficient text content
    const textLength = document.body.innerText.length;
    return textLength > 500;
}

function isYouTubeVideo() {
    return window.location.hostname.includes('youtube.com') &&
        window.location.pathname === '/watch';
}

// Extract page content using Readability
function extractArticleContent() {
    const documentClone = document.cloneNode(true);
    const reader = new Readability(documentClone);
    const article = reader.parse();

    return {
        content: article.textContent || article.innerHTML,
        title: article.title,
        url: window.location.href
    };
}

// Extract YouTube video ID
function getYouTubeVideoId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('v');
}

// Send content to backend
async function sendToBackend(data) {
    try {
        const response = await fetch('http://localhost:8000/api/v1/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();
            return { success: true, taskId: result.task_id };
        } else {
            return { success: false, error: 'Ingest failed' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Handle messages from service worker or side panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageInfo') {
        sendResponse({
            isArticle: isArticlePage(),
            isYouTube: isYouTubeVideo(),
            url: window.location.href
        });
    } else if (request.action === 'saveContext') {
        if (isYouTubeVideo()) {
            const videoId = getYouTubeVideoId();
            sendToBackend({
                source_type: 'youtube',
                source_url: window.location.href
            }).then(result => {
                sendResponse(result);
            });
        } else if (isArticlePage()) {
            const content = extractArticleContent();
            sendToBackend({
                source_type: 'article',
                source_url: content.url,
                content: content.content
            }).then(result => {
                sendResponse(result);
            });
        } else {
            sendResponse({ success: false, error: 'Not a supported page type' });
        }
        return true;
    } else if (request.action === 'saveLink') {
        sendToBackend({
            source_type: 'web',
            source_url: request.url
        }).then(result => {
            sendResponse(result);
        });
        return true;
    } else if (request.action === 'saveSelection') {
        sendToBackend({
            source_type: 'text',
            content: request.text
        }).then(result => {
            sendResponse(result);
        });
        return true;
    }
});
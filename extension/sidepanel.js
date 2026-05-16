// Cognitive Cache Side Panel - Vanilla JS
// Cerebral Glass Design

const API_BASE = 'http://localhost:8000/api/v1';
const MAX_CHAT_HISTORY = 100;
const MAX_INPUT_LENGTH = 500;

document.addEventListener('DOMContentLoaded', () => {
    const welcomeScreen = document.getElementById('welcome-screen');
    const mainScreen = document.getElementById('main-screen');
    const startBackendBtn = document.getElementById('start-backend-btn');
    const saveContextBtn = document.getElementById('save-context-btn');
    const ingestStatus = document.getElementById('ingest-status');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const backendError = document.getElementById('backend-error');
    const dismissErrorBtn = document.getElementById('dismiss-error-btn');
    const sourceCountBadge = document.getElementById('source-count');
    const emptyState = document.getElementById('empty-state');

    let isBackendReachable = true;

    // Check if first run
    chrome.storage.local.get(['isFirstRun'], (result) => {
        if (result.isFirstRun) {
            showWelcomeScreen();
        } else {
            showMainScreen();
            checkPageType();
            loadChatHistory();
            checkBackendHealth();
            updateSourceCount();
        }
    });

    // Welcome screen handlers
    startBackendBtn.addEventListener('click', () => {
        chrome.storage.local.set({ isFirstRun: false }, () => {
            showMainScreen();
            checkPageType();
            loadChatHistory();
            checkBackendHealth();
            updateSourceCount();
        });
    });

    // Dismiss error button
    dismissErrorBtn.addEventListener('click', () => {
        hideBackendError();
    });

    // Save context button
    saveContextBtn.addEventListener('click', async () => {
        saveContextBtn.disabled = true;
        showStatus('Processing...', 'loading');

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Try to use content script first
            try {
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'saveContext' });

                if (response && response.success) {
                    showStatus('Saved successfully!', 'success');
                    updateSourceCount();
                } else {
                    throw new Error(response?.error || 'Save failed');
                }
            } catch (contentScriptError) {
                // Fallback: save as web page directly if content script isn't available
                console.log('Content script not available, using fallback:', contentScriptError);
                const response = await fetch(`${API_BASE}/ingest`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_type: 'web',
                        url: tab.url
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    showStatus('Saved successfully!', 'success');
                    updateSourceCount();
                } else {
                    throw new Error('Save failed');
                }
            }
        } catch (error) {
            showStatus('Error: ' + error.message, 'error');
        }

        saveContextBtn.disabled = false;
    });

    // Chat form submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = chatInput.value.trim();
        if (!message) return;

        // Hide empty state
        if (emptyState) emptyState.style.display = 'none';

        // Add user message
        addMessage('user', message);
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Add loading message
        const loadingMsg = addMessage('assistant', 'Thinking...');
        loadingMsg.classList.add('loading');

        try {
            const response = await fetch(`${API_BASE}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });

            if (response.ok) {
                const data = await response.json();
                loadingMsg.classList.remove('loading');
                addMessage('assistant', data.response, data.citations);
                saveChatHistory(message, data.response);
                isBackendReachable = true;
                hideBackendError();
            } else {
                throw new Error('Query failed');
            }
        } catch (error) {
            loadingMsg.remove();
            isBackendReachable = false;
            showBackendError();
            addMessage('assistant', 'Error: ' + error.message);
        }
    });

    // Chat input handling
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Clear history button
    clearHistoryBtn.addEventListener('click', () => {
        chrome.storage.local.set({ chatHistory: [] }, () => {
            chatMessages.innerHTML = '';
            if (emptyState) {
                emptyState.style.display = 'flex';
            }
        });
    });

    // Check page type and enable/disable save button
    async function checkPageType() {
        let attempts = 0;
        const maxAttempts = 3;

        while (attempts < maxAttempts) {
            try {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'getPageInfo' });

                if (response && (response.isArticle || response.isYouTube)) {
                    saveContextBtn.disabled = false;
                    document.getElementById('save-btn-text').textContent = response.isYouTube ? 'Save YouTube Video' : 'Save Article';
                } else {
                    // Enable save button for all pages (will save as web page)
                    saveContextBtn.disabled = false;
                    document.getElementById('save-btn-text').textContent = 'Save Current Page';
                }
                return; // Success, exit the function
            } catch (error) {
                attempts++;
                if (attempts >= maxAttempts) {
                    console.error('checkPageType: failed after', maxAttempts, 'attempts:', error);
                    // Enable save button even on error (will save as web page)
                    saveContextBtn.disabled = false;
                    document.getElementById('save-btn-text').textContent = 'Save Current Page';
                } else {
                    // Wait before retrying
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
        }
    }

    // Update source count badge
    async function updateSourceCount() {
        try {
            const response = await fetch(`${API_BASE}/sources`);
            if (response.ok) {
                const data = await response.json();
                const count = data.sources?.length || 0;
                sourceCountBadge.textContent = count;
                chrome.runtime.sendMessage({
                    action: 'updateBadge',
                    count: count
                });
            }
        } catch (error) {
            console.error('Failed to update source count:', error);
        }
    }

    // Show status toast
    function showStatus(message, type) {
        ingestStatus.textContent = message;
        ingestStatus.className = `status-toast ${type}`;
        ingestStatus.classList.remove('hidden');

        // Auto-hide after 3 seconds
        setTimeout(() => {
            ingestStatus.classList.add('hidden');
        }, 3000);
    }

    // Add message to chat
    function addMessage(role, content, citations = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (role === 'assistant') {
            // Render markdown for assistant messages
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        msgDiv.appendChild(contentDiv);

        // Add citations if present
        if (citations && citations.length > 0) {
            const citationsDiv = document.createElement('div');
            citationsDiv.className = 'citations';
            citationsDiv.innerHTML = '<h4>Sources:</h4><ul>' +
                citations.map(c => `<li><a href="${c.url}" target="_blank">${c.title || c.url}</a></li>`).join('') +
                '</ul>';
            msgDiv.appendChild(citationsDiv);
        }

        chatMessages.appendChild(msgDiv);
        scrollToBottom();

        return msgDiv;
    }

    // Scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Load chat history
    function loadChatHistory() {
        chrome.storage.local.get(['chatHistory'], (result) => {
            const history = result.chatHistory || [];
            if (history.length > 0 && emptyState) {
                emptyState.style.display = 'none';
            }
            history.forEach(item => {
                addMessage('user', item.question);
                addMessage('assistant', item.answer);
            });
        });
    }

    // Save chat history
    function saveChatHistory(question, answer) {
        chrome.storage.local.get(['chatHistory'], (result) => {
            let history = result.chatHistory || [];
            history.push({ question, answer, timestamp: Date.now() });

            if (history.length > MAX_CHAT_HISTORY) {
                history = history.slice(-MAX_CHAT_HISTORY);
            }

            chrome.storage.local.set({ chatHistory: history });
        });
    }

    // Check backend health
    async function checkBackendHealth() {
        try {
            const response = await fetch(`${API_BASE}/health`, { method: 'GET' });
            isBackendReachable = response.ok;
            if (isBackendReachable) {
                hideBackendError();
            } else {
                showBackendError();
            }
        } catch (error) {
            isBackendReachable = false;
            showBackendError();
        }
    }

    // Show backend error
    function showBackendError() {
        backendError.classList.remove('hidden');
        chatInput.disabled = true;
        sendBtn.disabled = true;
    }

    // Hide backend error
    function hideBackendError() {
        backendError.classList.add('hidden');
        chatInput.disabled = false;
        sendBtn.disabled = false;
    }

    // Show welcome screen
    function showWelcomeScreen() {
        welcomeScreen.classList.remove('hidden');
        mainScreen.classList.add('hidden');
    }

    // Show main screen
    function showMainScreen() {
        welcomeScreen.classList.add('hidden');
        mainScreen.classList.remove('hidden');
        // Auto-focus input
        setTimeout(() => chatInput.focus(), 100);
    }
});
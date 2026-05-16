## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement extension chat UI with input (500 char limit, auto-focus, Enter to send, Shift+Enter for new lines, paper plane button), right-aligned user messages, left-aligned LLM responses, markdown rendering, inline citations, auto-scroll, "Clear History" button, and backend unreachable state (disabled input, red error icon 24x24px, "Backend offline" tooltip with red background/white text/8px border radius/auto-hide 5s).

## Acceptance criteria

- [ ] Chat input: 500 char limit, auto-focus on panel open, Enter to send, Shift+Enter for new lines
- [ ] Paper plane icon send button
- [ ] Right-aligned user messages, left-aligned LLM responses
- [ ] Markdown rendering for responses
- [ ] Inline citations (page titles for web, video titles for YouTube, clickable URLs)
- [ ] Auto-scroll to latest message
- [ ] "Clear History" button (100 conversation limit in browser storage)
- [ ] Chat side-panel: 400px default width, no header/footer
- [ ] Side-panel close is handled natively by Chrome (the Side Panel API does not support programmatic close-on-outside-click from extension code — no custom implementation required or attempted)
- [ ] Backend unreachable state: disabled input, red circle error icon (24x24px) below input
- [ ] Tooltip: "Backend offline", red background, white text, 8px border radius, above input, auto-hide 5s
- [ ] No dark mode, no footer, no character counter for MVP

## Blocked by

- /issues/issue-007-extension-setup.md
- /issues/issue-006-query-endpoint.md

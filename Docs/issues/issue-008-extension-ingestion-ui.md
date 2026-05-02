## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement extension ingestion UI with "Save Context" button, auto-detect for supported sources, Ctrl+Shift+S shortcut, right-click context menu (links/text only), status indicator, badge with source count, welcome screen with "Start Backend" button, and browser storage API with 100 conversation limit.

## Acceptance criteria

- [ ] "Save Context" button with auto-detect (enabled/disabled based on page type)
- [ ] Ctrl+Shift+S keyboard shortcut for ingestion
- [ ] Right-click context menu only on links/text selections
- [ ] Ingestion status indicator (processing/saved/error)
- [ ] Badge on extension icon showing ingested source count
- [ ] Welcome screen on first install with "Start Backend" button
- [ ] Browser storage API for chat history (100 conversation limit)
- [ ] No telemetry (privacy-first design)
- [ ] Readability.js used for article text extraction
- [ ] youtube-transcript-api used for YouTube transcripts

## Blocked by

- /issues/issue-007-extension-setup.md

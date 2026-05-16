## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement extension ingestion UI with "Save Context" button, auto-detect for supported sources, Ctrl+Shift+S shortcut, right-click context menu (links/text only), status indicator, badge with source count, welcome screen with "Start Backend" button, and browser storage API with 100 conversation limit.

For **web articles**, the extension extracts page text using Readability.js and POSTs it to `/api/v1/ingest` as `source_type: "article"` with the `content` field populated.

For **YouTube pages**, the extension extracts the video URL/ID from the DOM and POSTs it to `/api/v1/ingest` as `source_type: "youtube"` — transcript fetching is handled server-side by the backend (Issue #4).

## Acceptance criteria

- [x] "Save Context" button with auto-detect (enabled for article pages and YouTube video pages; disabled for all other sources)
- [x] Ctrl+Shift+S keyboard shortcut for ingestion
- [x] Right-click context menu only on links/text selections
- [x] Ingestion status indicator (processing/saved/error), polled via GET /api/v1/tasks/{task_id}
- [x] Badge on extension icon showing ingested source count, fetched from GET /api/v1/sources
- [x] Welcome screen on first install with "Start Backend" button
- [x] Browser storage API for chat history (100 conversation limit)
- [x] No telemetry (privacy-first design)
- [x] Readability.js used for article text extraction (client-side)
- [x] YouTube ingestion sends video URL only — no client-side transcript extraction

## Blocked by

- /issues/issue-007-extension-setup.md
- /issues/issue-004-ingest-endpoint.md
- /issues/issue-005-sources-endpoint.md

## Implementation

Created/updated the following files:

- `extension/manifest.json` - Added `contextMenus`, `storage` permissions, and `commands` for Ctrl+Shift+S
- `extension/service-worker.js` - Added context menu creation, keyboard shortcut handler, badge updates
- `extension/content.js` - Added page type detection, content extraction, save handlers
- `extension/sidepanel.html` - Added welcome screen, save context button, status indicator
- `extension/sidepanel.js` - Added auto-detect, keyboard shortcut, context menu, status indicator, badge, welcome screen, chat history storage
- `extension/sidepanel.css` - Added styles for welcome screen, disabled button state

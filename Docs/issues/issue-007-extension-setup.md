## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Set up Manifest V3 browser extension with Chrome Side Panel API, strict CSP, event-based service worker, Vanilla JS/HTML/CSS (Pure CSS, system fonts), and Readability.js via CDN.

## Acceptance criteria

- [x] Manifest V3 configured with strict CSP
- [x] Event-based service worker (not long-running)
- [x] Chrome Side Panel API integrated (400px default width)
- [x] Vanilla JS, HTML, Pure CSS (no frameworks)
- [x] System fonts used throughout
- [x] Readability.js loaded via CDN
- [x] Default browser icon used
- [x] No dark mode, no custom fonts/icons for MVP

## Blocked by

None - can start immediately

## Implementation

Created the following files:

- `extension/manifest.json` - Manifest V3 with strict CSP, side panel, content scripts
- `extension/service-worker.js` - Event-based service worker
- `extension/sidepanel.html` - Side panel HTML with Readability.js CDN
- `extension/sidepanel.js` - Vanilla JS for ingest and query functionality
- `extension/sidepanel.css` - Pure CSS with system fonts
- `extension/content.js` - Content script for page content extraction
- `extension/icons/icon16.png`, `icon32.png`, `icon48.png`, `icon128.png` - Default browser icons

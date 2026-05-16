# MVP Product Requirements Document (PRD): "Cognitive Cache"

## Problem Statement

Users consume large amounts of web content (text articles, YouTube videos) daily but lack a private, low-cost way to recall and query that information later. Existing solutions are either cloud-dependent (raising privacy concerns) or require paid subscriptions, creating a gap for users who want a fully local, free "Second Brain" AI assistant.

## Solution

Build a 100% local, open-source "Cognitive Cache" system that:

1. Ingests text from web articles and YouTube transcripts via a browser extension
2. Processes and stores content in a local vector database (ChromaDB)
3. Allows users to query their ingested content via a conversational chat UI in the browser extension
4. Uses a locally hosted Small Language Model (Phi-3.5-mini via Ollama) for response generation with inline source citations

## User Stories

1. As a user, I want to click a button in my browser extension to save the current article/YouTube video to my local knowledge base, so that I can query it later.
2. As a user, I want to use a keyboard shortcut (Ctrl+Shift+S) to trigger ingestion, so that I can save content faster.
3. As a user, I want to right-click on links/text selections to save content, so that I have flexible ingestion options.
4. As a user, I want to chat with my saved content via a side-panel, so that I can get answers with source citations.
5. As a user, I want multi-turn conversation history in the chat, so that I can ask follow-up questions.
6. As a user, I want to see inline clickable citations (page titles for web, video titles for YouTube), so that I know where answers come from.
7. As a user, I want the extension to auto-detect supported pages (articles/YouTube) and disable the save button for unsupported sources, so that I don't waste time on invalid ingestion.
8. As a user, I want to see ingestion status (processing/saved/error) in the extension, so that I know if my content was saved.
9. As a user, I want to see a badge with my ingested source count on the extension icon, so that I have quick visibility into my knowledge base size.
10. As a user, I want the chat input to auto-focus when the side-panel opens, so that I can type immediately.
11. As a user, I want the chat to auto-scroll to the latest message, so that I always see new responses.
12. As a user, I want to clear my chat history with a button, so that I can reset conversations.
13. As a user, I want to see a welcome screen with a "Start Backend" button on first install, so that I know how to set up the local server.
14. As a user, I want the backend to auto-pull the Phi-3.5-mini model if missing, so that I don't have to manually configure Ollama.
15. As a user, I want to see a "Backend offline" tooltip when the chat is disabled, so that I know why I can't type.
16. As a user, I want to use the Chrome Side Panel API for the chat UI, so that it integrates natively with my browser.
17. As a user, I want to use Manifest V3 for the extension, so that it's compatible with modern Chrome standards.

## Implementation Decisions

### Core Tech Stack

- Orchestration: LangGraph (for agentic logic, state management)
- SLM: Phi-3.5-mini (hosted via Ollama, auto-pull on startup if missing)
- Chunking: SemanticChunker + ParentDocumentRetriever + metadata filtering + HyDE
- Embeddings: all-MiniLM-L6-v2 (auto-detect GPU with CPU fallback)
- Vector DB: ChromaDB (persistent on-disk storage)
- API Framework: FastAPI (port 8000, /api/v1/ prefix)
- Browser Extension: Vanilla JS/HTML/CSS (Manifest V3, Chrome Side Panel API)

### Extension UI/UX

- Chat input: 500 character limit, auto-focus on panel open, Enter to send, Shift+Enter for new lines
- Error states: Red circle icon (24x24px) below input, white text on red background tooltip ("Backend offline"), visible on click, auto-hide after 5s
- Side-panel: 400px default width, no header/footer for more chat space
- Side-panel close: Handled natively by Chrome — the Chrome Side Panel API does not expose a programmatic API for close-on-outside-click from extension code; no custom workaround will be implemented
- Icon: Default browser icon, badge showing ingested source count
- Context menu: Only on links/text selections, fixed Ctrl+Shift+S shortcut
- Storage: Browser storage API (100 conversation limit, persist chat history)
- Welcome screen: Include "Start Backend" button, no telemetry

### Ingestion: Article vs YouTube

- **Web articles:** Readability.js runs client-side in the extension to extract clean text from the DOM; the extracted text is POSTed to the backend as `source_type: "article"` with a `content` field.
- **YouTube videos:** The extension extracts the video URL/ID from the DOM and POSTs it to the backend as `source_type: "youtube"` with no `content` field. The backend fetches the transcript server-side using the `youtube-transcript-api` Python library.

### FastAPI Backend

- Endpoints: POST /api/v1/ingest (accepts `source_type`, `url`, and optional `content`; returns ingestion ID + status), POST /api/v1/query (full response with sources), GET /api/v1/health (detailed checks), GET /api/v1/sources (full metadata), GET /api/v1/tasks/{task_id} (task status)
- Background tasks: Async ingestion, persist task status/results to disk, daily cleanup at 00:00 UTC via APScheduler (30 rotated logs, JSON format, DEBUG level, separate cleanup.log)
- Middleware: Request ID (X-Request-ID header), GZip compression, rate limiting (10 req/min), 30s timeout for /query
- Error handling: Custom exception handlers, structured JSON error responses, DEBUG logging level
- CORS: Allow all origins (*), all methods, no auth for MVP
- Validation: Pydantic models, dependency injection for shared resources
- Testing: Basic pytest tests for critical endpoints

## Testing Decisions

- Test framework: pytest for FastAPI endpoints
- Scope: Test external behavior (not implementation details) of /ingest (both source types), /query, /health, /sources endpoints
- Modules to test: FastAPI route handlers, LangGraph orchestration logic, ChromaDB integration
- Prior art: Follow existing Python testing patterns in the repo (if any)

## Out of Scope (MVP)

- PDF ingestion, local desktop files, real-time audio/video processing
- Email ingestion, cloud backups, cross-device syncing
- Standalone desktop application, mobile app
- Dark mode, custom fonts/icons, telemetry, aria-labels for MVP
- Close-on-outside-click for the Side Panel (not supported by Chrome Side Panel API)

## Further Notes

- All decisions were validated via Grill Me session (Phase 1) with one question per decision branch
- Local-first, privacy-centric design: no cloud dependencies, no telemetry
- MVP focuses on core ingestion → storage → query flow with essential UX feedback loops

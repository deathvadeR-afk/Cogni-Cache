## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement POST /api/v1/ingest endpoint with background task processing, task status storage to disk, GET /api/v1/tasks/{task_id} endpoint, and APScheduler daily cleanup for old tasks. The endpoint handles two source types: web articles (receives raw extracted text from the extension) and YouTube videos (receives the video URL/ID, fetches the transcript server-side using `youtube-transcript-api`).

## Acceptance criteria

- [x] POST /api/v1/ingest accepts a JSON body with `source_type` (`"article"` | `"youtube"`), `url`, and `content` (raw text for articles; omitted for YouTube)
- [x] For `source_type: "youtube"`, backend fetches transcript via `youtube-transcript-api` using the supplied URL/video ID
- [x] For `source_type: "article"`, backend uses the `content` field supplied by the extension (extracted via Readability.js client-side)
- [x] POST /api/v1/ingest returns ingestion ID + status immediately (non-blocking)
- [x] 10MB request size limit configured
- [x] Background task processes chunking and ChromaDB storage asynchronously
- [x] Task status and results persisted to disk
- [x] GET /api/v1/tasks/{task_id} endpoint returns task status and result
- [x] APScheduler daily cleanup at 00:00 UTC (dedicated thread)
- [x] Cleanup deletes tasks older than 7 days
- [x] Cleanup logs to separate cleanup.log (JSON format, DEBUG level, daily rotation, 30 rotated files)
- [x] pytest tests for POST /api/v1/ingest (both source types) and GET /api/v1/tasks/{task_id}

## Status

[x] COMPLETED - All acceptance criteria met. Ingest endpoint with background task processing, task storage, YouTube transcript fetching, and daily cleanup implemented.

## Blocked by

- /issues/issue-001-fastapi-backend-setup.md
- /issues/issue-002-chromadb-setup.md

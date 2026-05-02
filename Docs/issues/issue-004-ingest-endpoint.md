## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement POST /api/v1/ingest endpoint with background task processing, task status storage to disk, GET /api/v1/tasks/{task_id} endpoint, and APScheduler daily cleanup for old tasks.

## Acceptance criteria

- [ ] POST /api/v1/ingest returns ingestion ID + status
- [ ] 10MB request size limit configured
- [ ] Background task processing for ingestion (non-blocking)
- [ ] Task status and results persisted to disk
- [ ] GET /api/v1/tasks/{task_id} endpoint returns task status
- [ ] APScheduler daily cleanup at 00:00 UTC (dedicated thread)
- [ ] Cleanup deletes tasks older than 7 days
- [ ] Cleanup logs to separate cleanup.log (JSON format, DEBUG level, daily rotation, 30 rotated files)
- [ ] pytest tests for /api/v1/ingest endpoint

## Blocked by

- /issues/issue-001-fastapi-backend-setup.md
- /issues/issue-002-chromadb-setup.md

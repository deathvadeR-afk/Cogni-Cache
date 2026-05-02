## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement GET /api/v1/sources endpoint that returns full metadata for all ingested sources, supporting the extension badge and source listing.

## Acceptance criteria

- [ ] GET /api/v1/sources returns full metadata (URL, title, timestamp, chunk count)
- [ ] Endpoint uses dependency injection for ChromaDB client
- [ ] Pydantic response model defined
- [ ] pytest tests for /api/v1/sources endpoint

## Blocked by

- /issues/issue-002-chromadb-setup.md

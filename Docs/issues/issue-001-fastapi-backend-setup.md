## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Set up FastAPI backend with health endpoint, CORS, rate limiting, timeout, request ID middleware, Pydantic validation, dependency injection, custom error handlers, and DEBUG logging. This is a foundational vertical slice that delivers a working API base for all other slices.

## Acceptance criteria

- [x] FastAPI running on port 8000 with `/api/v1/` prefix
- [x] GET `/api/v1/health` returns detailed checks (Ollama connection, ChromaDB status)
- [x] CORS allows all origins (`*`) and all methods
- [x] GZip compression enabled for responses
- [x] Rate limiting set to 10 requests/minute
- [x] 30s timeout configured for `/api/v1/query` endpoint
- [x] Request ID middleware adds `X-Request-ID` header to responses
- [x] Pydantic models used for request/response validation
- [x] Dependency injection for shared resources (ChromaDB, Ollama clients)
- [x] Custom exception handlers for common errors (ChromaDB, Ollama, etc.)
- [x] DEBUG level logging configured
- [x] Structured JSON error responses returned
- [x] Basic pytest tests for `/api/v1/health` endpoint

## Blocked by

None - can start immediately

## Status

[x] COMPLETED - All acceptance criteria met. FastAPI backend setup with health endpoint, CORS, rate limiting, timeout, middleware, Pydantic models, dependency injection, and tests complete.

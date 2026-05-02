## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Implement POST /api/v1/query endpoint with streaming responses, multi-turn conversation history, and inline source citations (page titles for web, video titles for YouTube with clickable URLs).

## Acceptance criteria

- [ ] POST /api/v1/query returns streaming response
- [ ] Multi-turn conversation history supported via LangGraph
- [ ] Full response includes inline citations (page titles for web, video titles for YouTube)
- [ ] Citations are clickable URLs
- [ ] Endpoint uses dependency injection for ChromaDB, Ollama, LangGraph
- [ ] Pydantic request/response models defined
- [ ] pytest tests for /api/v1/query endpoint

## Blocked by

- /issues/issue-001-fastapi-backend-setup.md
- /issues/issue-002-chromadb-setup.md
- /issues/issue-003-ollama-phi-setup.md

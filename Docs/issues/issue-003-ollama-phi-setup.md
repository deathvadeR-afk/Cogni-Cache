## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Set up Ollama with Phi-3.5-mini model, auto-pull on startup if missing, and configure LangGraph orchestration for the RAG pipeline.

## Acceptance criteria

- [ ] Ollama integration via FastAPI dependency injection
- [ ] Phi-3.5-mini model auto-pull on backend startup if missing
- [ ] LangGraph orchestration framework configured for RAG workflow
- [ ] Connection to ChromaDB (from Issue #2) and Ollama established
- [ ] Basic RAG pipeline routing (query → retrieve → generate) set up

## Blocked by

None - can start immediately

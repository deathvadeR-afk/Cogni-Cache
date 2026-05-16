## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Set up Ollama with Phi-3.5-mini model, auto-pull on startup if missing, and configure LangGraph orchestration for the RAG pipeline.

## Acceptance criteria

- [x] Ollama integration via FastAPI dependency injection
- [x] Phi-3.5-mini model auto-pull on backend startup if missing
- [x] LangGraph orchestration framework configured for RAG workflow
- [x] Basic RAG pipeline routing (query → retrieve → generate) set up with mocked ChromaDB retriever (real connection validated in Issue #6)
- [x] Unit tests cover LangGraph node logic in isolation (ChromaDB dependency mocked)

## Blocked by

None - can start immediately

> **Note:** The RAG pipeline routing acceptance criterion connects to ChromaDB (Issue #2). For this issue, ChromaDB integration should be tested with a mock/stub so the slice remains independently implementable. End-to-end wiring of the real ChromaDB client is validated in Issue #6 (Query Endpoint), which explicitly blocks on both this issue and Issue #2.

## Status

[x] COMPLETED - All acceptance criteria met. Ollama Phi-3.5-mini integration with auto-pull, LangGraph orchestration configured, RAG pipeline with mocked ChromaDB retriever implemented, and 12 unit tests passing.

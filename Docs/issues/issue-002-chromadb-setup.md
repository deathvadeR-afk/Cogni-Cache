## Parent

/issues/PRD-Cognitive-Cache.md

## What to build

Set up ChromaDB with persistent on-disk storage, initialize all-MiniLM-L6-v2 embeddings with GPU auto-detect + CPU fallback, and configure SemanticChunker + ParentDocumentRetriever + metadata filtering + HyDE for the RAG pipeline.

## Acceptance criteria

- [x] ChromaDB initialized with persistent on-disk storage
- [x] Lifespan events used for ChromaDB initialization
- [x] all-MiniLM-L6-v2 embeddings configured via HuggingFace
- [x] GPU auto-detection with CPU fallback for embeddings
- [x] SemanticChunker configured for text chunking
- [x] ParentDocumentRetriever set up for document retrieval
- [x] Metadata filtering enabled for ingested sources
- [x] HyDE (Hypothetical Document Embeddings) configured for query enhancement

## Blocked by

None - can start immediately

## Status

[x] COMPLETED - All acceptance criteria met. ChromaDB initialized with persistent storage, embeddings configured with GPU/CPU auto-detect, SemanticChunker and ParentDocumentRetriever set up, metadata filtering and HyDE configured, lifespan events updated, and tests created.

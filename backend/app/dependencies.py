from typing import AsyncGenerator
from fastapi import Depends, Request
from functools import lru_cache
from app.chromadb_client import ChromaDBClient
from app.ollama_client import OllamaClient


@lru_cache(maxsize=1)
def get_chromadb_client() -> ChromaDBClient:
    """Dependency for ChromaDB client."""
    client = ChromaDBClient()
    client.initialize()
    return client


@lru_cache(maxsize=1)
def get_ollama_client() -> OllamaClient:
    """Dependency for Ollama client."""
    client = OllamaClient()
    client.initialize()
    return client


async def get_db_client(request: Request) -> ChromaDBClient:
    """Get ChromaDB client from app state or create new."""
    if hasattr(request.app.state, 'chromadb_client'):
        return request.app.state.chromadb_client
    return get_chromadb_client()


async def get_ollama_client_dep(request: Request) -> OllamaClient:
    """Get Ollama client from app state or create new."""
    if hasattr(request.app.state, 'ollama_client'):
        return request.app.state.ollama_client
    return get_ollama_client()

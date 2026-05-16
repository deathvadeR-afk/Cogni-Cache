from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

class HealthResponse(BaseModel):
    """Response schema for health endpoint."""
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="0.1.0")
    services: Dict[str, Dict[str, str]] = Field(
        ...,
        example={
            "ollama": {"status": "not_checked"},
            "chromadb": {"status": "not_checked"},
        },
    )
    request_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str = Field(..., example="Internal server error")
    detail: str = Field(..., example="An unexpected error occurred")
    request_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

class SourceType(str, Enum):
    """Source type for ingestion."""
    article = "article"
    youtube = "youtube"

class IngestRequest(BaseModel):
    """Request schema for ingest endpoint."""
    source_type: SourceType = Field(..., example="article")
    url: str = Field(..., example="https://example.com/article")
    content: Optional[str] = Field(None, example="Article text content...")

class IngestResponse(BaseModel):
    """Response schema for ingest endpoint."""
    task_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    status: str = Field(..., example="processing")
    message: str = Field(..., example="Ingestion started")

class TaskStatus(str, Enum):
    """Task status values."""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class TaskResponse(BaseModel):
    """Response schema for task status endpoint."""
    task_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    status: TaskStatus = Field(..., example="completed")
    source_type: Optional[SourceType] = Field(None, example="article")
    url: Optional[str] = Field(None, example="https://example.com/article")
    created_at: Optional[str] = Field(None, example="2024-01-01T00:00:00Z")
    completed_at: Optional[str] = Field(None, example="2024-01-01T00:00:01Z")
    result: Optional[Dict[str, Any]] = Field(None)
    error: Optional[str] = Field(None)


class SourceMetadata(BaseModel):
    """Metadata for a single source."""
    url: str = Field(..., example="https://example.com/article")
    title: Optional[str] = Field(None, example="Article Title")
    timestamp: Optional[str] = Field(None, example="2024-01-01T00:00:00Z")
    chunk_count: int = Field(..., example=5)


class SourcesResponse(BaseModel):
    """Response schema for sources endpoint."""
    sources: List[SourceMetadata] = Field(default_factory=list)


class Citation(BaseModel):
    """Citation for a source used in the response."""
    url: str = Field(..., example="https://example.com/article")
    title: Optional[str] = Field(None, example="Article Title")


class QueryRequest(BaseModel):
    """Request schema for query endpoint."""
    query: str = Field(..., example="What is the capital of France?")
    conversation_id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    history: Optional[List[Dict[str, str]]] = Field(
        None,
        example=[
            {"role": "user", "content": "What is France known for?"},
            {"role": "assistant", "content": "France is known for..."}
        ]
    )


class QueryResponse(BaseModel):
    """Response schema for query endpoint."""
    response: str = Field(..., example="The capital of France is Paris.")
    citations: List[Citation] = Field(default_factory=list)
    conversation_id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")

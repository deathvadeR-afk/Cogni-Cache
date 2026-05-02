from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

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

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.rag_pipeline import RAGPipeline

# Module-level client - allows lifespan to run once
client = TestClient(app)


def test_query_success():
    """Test successful query endpoint."""
    mock_rag_pipeline = MagicMock(spec=RAGPipeline)
    mock_rag_pipeline.query = Mock(return_value={
        "response": "The capital of France is Paris.",
        "citations": [
            {"url": "https://example.com/article", "title": "Article Title"}
        ]
    })
    
    app.state.rag_pipeline = mock_rag_pipeline
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": "What is the capital of France?",
            "conversation_id": "test-conv-123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "citations" in data
    assert "conversation_id" in data
    assert data["response"] == "The capital of France is Paris."
    assert len(data["citations"]) == 1
    assert data["citations"][0]["url"] == "https://example.com/article"


def test_query_with_history():
    """Test query endpoint with conversation history."""
    mock_rag_pipeline = MagicMock(spec=RAGPipeline)
    mock_rag_pipeline.query = Mock(return_value={
        "response": "The capital of France is Paris.",
        "citations": []
    })
    
    app.state.rag_pipeline = mock_rag_pipeline
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": "What is the capital of France?",
            "conversation_id": "test-conv-123",
            "history": [
                {"role": "user", "content": "What is France known for?"},
                {"role": "assistant", "content": "France is known for its cuisine and art."}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    # Verify history was passed to the pipeline
    call_args = mock_rag_pipeline.query.call_args
    assert call_args[1]['history'] is not None
    assert len(call_args[1]['history']) == 2


def test_query_generates_conversation_id():
    """Test that conversation_id is generated if not provided."""
    mock_rag_pipeline = MagicMock(spec=RAGPipeline)
    mock_rag_pipeline.query = Mock(return_value={
        "response": "The capital of France is Paris.",
        "citations": []
    })
    
    app.state.rag_pipeline = mock_rag_pipeline
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": "What is the capital of France?"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] is not None


def test_query_no_citations():
    """Test query endpoint with no citations."""
    mock_rag_pipeline = MagicMock(spec=RAGPipeline)
    mock_rag_pipeline.query = Mock(return_value={
        "response": "I don't have enough information to answer that.",
        "citations": []
    })
    
    app.state.rag_pipeline = mock_rag_pipeline
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": "What is the meaning of life?"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["citations"] == []


def test_query_rag_pipeline_not_initialized():
    """Test query endpoint when RAG pipeline is not initialized."""
    app.state.rag_pipeline = None
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": "What is the capital of France?"
        }
    )
    
    assert response.status_code == 503


def test_query_empty_query():
    """Test query endpoint with empty query."""
    mock_rag_pipeline = MagicMock(spec=RAGPipeline)
    mock_rag_pipeline.query = Mock(return_value={
        "response": "Empty query response",
        "citations": []
    })
    
    app.state.rag_pipeline = mock_rag_pipeline
    
    response = client.post(
        "/api/v1/query",
        json={
            "query": ""
        }
    )
    
    # Should still work, just with empty query
    assert response.status_code == 200
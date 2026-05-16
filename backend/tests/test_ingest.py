import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.task_storage import TaskStorage
from app.youtube_transcript import fetch_youtube_transcript, extract_video_id

# Module-level client - allows lifespan to run once
client = TestClient(app)


def test_ingest_article_success():
    """Test successful article ingestion."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.create_task.return_value = "test-task-id"
    
    # Set the attribute first, then patch
    app.state.task_storage = mock_task_storage
    app.state.chromadb_client = MagicMock()
    
    response = client.post(
        "/api/v1/ingest",
        json={
            "source_type": "article",
            "url": "https://example.com/article",
            "content": "This is the article content to ingest."
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"
    assert "message" in data


def test_ingest_youtube_success():
    """Test successful YouTube ingestion."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.create_task.return_value = "test-task-id"
    
    app.state.task_storage = mock_task_storage
    app.state.chromadb_client = MagicMock()
    
    with patch("app.youtube_transcript.fetch_youtube_transcript") as mock_transcript:
        mock_transcript.return_value = "YouTube transcript content"
        
        response = client.post(
            "/api/v1/ingest",
            json={
                "source_type": "youtube",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"


def test_ingest_article_missing_content():
    """Test article ingestion without content fails."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.create_task.return_value = "test-task-id"
    
    app.state.task_storage = mock_task_storage
    
    response = client.post(
        "/api/v1/ingest",
        json={
            "source_type": "article",
            "url": "https://example.com/article"
        }
    )

    # Should still return 200, but task will fail in background
    assert response.status_code == 200


def test_get_task_success():
    """Test getting task status."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.get_task.return_value = {
        "task_id": "test-task-id",
        "status": "completed",
        "source_type": "article",
        "url": "https://example.com/article",
        "created_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:00:01Z",
        "result": {"chunks_added": 1},
        "error": None,
    }
    
    app.state.task_storage = mock_task_storage
    
    response = client.get("/api/v1/tasks/test-task-id")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id"
    assert data["status"] == "completed"
    assert data["source_type"] == "article"
    assert data["url"] == "https://example.com/article"


def test_get_task_not_found():
    """Test getting non-existent task."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.get_task.return_value = None
    
    app.state.task_storage = mock_task_storage
    
    response = client.get("/api/v1/tasks/nonexistent-id")

    assert response.status_code == 404


def test_get_task_failed():
    """Test getting failed task status."""
    mock_task_storage = MagicMock(spec=TaskStorage)
    mock_task_storage.get_task.return_value = {
        "task_id": "failed-task-id",
        "status": "failed",
        "source_type": "youtube",
        "url": "https://youtube.com/watch?v=test",
        "created_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:00:01Z",
        "result": None,
        "error": "Could not fetch transcript"
    }
    
    app.state.task_storage = mock_task_storage
    
    response = client.get("/api/v1/tasks/failed-task-id")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "Could not fetch transcript"


def test_extract_video_id_from_url():
    """Test extracting video ID from various URL formats."""
    # Standard URL
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Short URL
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Already a video ID
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


@patch("app.youtube_transcript.YouTubeTranscriptApi")
def test_fetch_transcript_success(mock_api):
    """Test successful transcript fetch."""
    mock_api.get_transcript.return_value = [
        {"text": "Hello", "start": 0, "duration": 1},
        {"text": "World", "start": 1, "duration": 1}
    ]
    
    result = fetch_youtube_transcript("dQw4w9WgXcQ")
    assert result == "Hello World"


@patch("app.youtube_transcript.YouTubeTranscriptApi")
def test_fetch_transcript_failure(mock_api):
    """Test transcript fetch failure."""
    mock_api.get_transcript.side_effect = Exception("Video unavailable")
    
    # Use a valid video ID format so it passes validation
    with pytest.raises(ValueError, match="Could not fetch transcript"):
        fetch_youtube_transcript("dQw4w9WgXcQ")


def test_create_and_get_task(tmp_path):
    """Test creating and retrieving a task."""
    storage = TaskStorage(tasks_dir=tmp_path)
    
    task_id = storage.create_task(
        source_type="article",
        url="https://example.com",
        content="Test content"
    )
    
    task = storage.get_task(task_id)
    assert task["task_id"] == task_id
    assert task["status"] == "pending"
    assert task["source_type"] == "article"
    assert task["url"] == "https://example.com"


def test_update_task(tmp_path):
    """Test updating task status."""
    storage = TaskStorage(tasks_dir=tmp_path)
    
    task_id = storage.create_task(
        source_type="article",
        url="https://example.com"
    )
    
    storage.update_task(
        task_id,
        status="completed",
        result={"chunks_added": 1}
    )
    
    task = storage.get_task(task_id)
    assert task["status"] == "completed"
    assert task["result"]["chunks_added"] == 1


def test_delete_task(tmp_path):
    """Test deleting a task."""
    storage = TaskStorage(tasks_dir=tmp_path)
    
    task_id = storage.create_task(
        source_type="article",
        url="https://example.com"
    )
    
    assert storage.delete_task(task_id) is True
    assert storage.get_task(task_id) is None


def test_get_sources_success():
    """Test getting sources list."""
    mock_chromadb = MagicMock()
    mock_chromadb.get_sources.return_value = [
        {"url": "https://example.com/1", "title": "Title 1", "timestamp": "2024-01-01T00:00:00Z", "chunk_count": 2},
        {"url": "https://example.com/2", "title": "Title 2", "timestamp": "2024-01-02T00:00:00Z", "chunk_count": 1},
    ]
    
    app.state.chromadb_client = mock_chromadb
    
    response = client.get("/api/v1/sources")
    
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) == 2
    assert data["sources"][0]["url"] == "https://example.com/1"
    assert data["sources"][0]["chunk_count"] == 2


def test_get_sources_empty():
    """Test getting sources when none exist."""
    mock_chromadb = MagicMock()
    mock_chromadb.get_sources.return_value = []
    
    app.state.chromadb_client = mock_chromadb
    
    response = client.get("/api/v1/sources")
    
    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == []
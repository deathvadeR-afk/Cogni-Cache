import pytest
import requests
from unittest.mock import patch, MagicMock, PropertyMock
from app.ollama_client import OllamaClient
from app.rag_pipeline import RAGPipeline, RAGState
from langchain_core.documents import Document


class TestOllamaClient:
    """Tests for OllamaClient."""

    def test_initialization(self):
        """Test OllamaClient initialization."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "phi3.5:mini"
        assert client.status == "not_initialized"

    def test_get_status_not_initialized(self):
        """Test get_status when not initialized."""
        client = OllamaClient()
        status = client.get_status()
        assert status["status"] == "not_initialized"
        assert status["model"] == "phi3.5:mini"

    @patch('app.ollama_client.requests.Session')
    def test_check_server_health_success(self, mock_session):
        """Test server health check when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        client = OllamaClient()
        result = client._check_server_health()
        assert result is True

    @patch('app.ollama_client.requests.Session')
    def test_check_server_health_failure(self, mock_session):
        """Test server health check when Ollama is not running."""
        mock_session.return_value.get.side_effect = requests.RequestException("Connection refused")

        client = OllamaClient()
        result = client._check_server_health()
        assert result is False

    @patch('app.ollama_client.requests.Session')
    def test_model_exists_true(self, mock_session):
        """Test model_exists when model is present."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "phi3.5:mini"},
                {"name": "llama2:latest"}
            ]
        }
        mock_session.return_value.get.return_value = mock_response

        client = OllamaClient()
        result = client._model_exists("phi3.5:mini")
        assert result is True

    @patch('app.ollama_client.requests.Session')
    def test_model_exists_false(self, mock_session):
        """Test model_exists when model is not present."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"}
            ]
        }
        mock_session.return_value.get.return_value = mock_response

        client = OllamaClient()
        result = client._model_exists("phi3.5:mini")
        assert result is False

    @patch('app.ollama_client.subprocess.run')
    @patch('app.ollama_client.OllamaClient._model_exists')
    @patch('app.ollama_client.OllamaClient._check_server_health')
    def test_initialize_success(self, mock_health, mock_exists, mock_run):
        """Test successful initialization."""
        mock_health.return_value = True
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        client = OllamaClient()
        result = client.initialize()
        assert result is True
        assert client.status == "healthy"

    @patch('app.ollama_client.OllamaClient._check_server_health')
    def test_initialize_server_not_running(self, mock_health):
        """Test initialization when server is not running."""
        mock_health.return_value = False

        client = OllamaClient()
        result = client.initialize()
        assert result is False
        assert client.status == "error"


class TestRAGPipeline:
    """Tests for RAGPipeline."""

    def test_pipeline_query(self):
        """Test RAG pipeline query method."""
        mock_chromadb = MagicMock()
        mock_chromadb.status = "healthy"
        mock_chromadb.similarity_search.return_value = [
            Document(page_content="Test document content", metadata={"url": "https://example.com"})
        ]

        mock_ollama = MagicMock()
        mock_ollama.status = "healthy"
        mock_ollama.generate.return_value = "Test response"

        pipeline = RAGPipeline(mock_chromadb, mock_ollama)
        result = pipeline.query("Test query")

        assert result["response"] == "Test response"
        assert "citations" in result
        mock_chromadb.similarity_search.assert_called_once()
        mock_ollama.generate.assert_called_once()

    def test_pipeline_query_hyde(self):
        """Test RAG pipeline query with HyDE."""
        mock_chromadb = MagicMock()
        mock_chromadb.status = "healthy"
        mock_chromadb.enhanced_search.return_value = [
            Document(page_content="HyDE document")
        ]

        mock_ollama = MagicMock()
        mock_ollama.status = "healthy"
        mock_ollama.generate.return_value = "HyDE response"

        pipeline = RAGPipeline(mock_chromadb, mock_ollama)
        response = pipeline.query_with_hyde("Test query")

        assert response == "HyDE response"
        mock_chromadb.enhanced_search.assert_called_once()
        mock_ollama.generate.assert_called_once()

    def test_pipeline_unhealthy_chromadb(self):
        """Test pipeline raises error when ChromaDB is unhealthy."""
        mock_chromadb = MagicMock()
        mock_chromadb.status = "error"

        mock_ollama = MagicMock()
        mock_ollama.status = "healthy"

        pipeline = RAGPipeline(mock_chromadb, mock_ollama)
        with pytest.raises(RuntimeError, match="ChromaDB client not healthy"):
            pipeline.query("Test query")

    def test_pipeline_unhealthy_ollama(self):
        """Test pipeline raises error when Ollama is unhealthy."""
        mock_chromadb = MagicMock()
        mock_chromadb.status = "healthy"

        mock_ollama = MagicMock()
        mock_ollama.status = "error"

        pipeline = RAGPipeline(mock_chromadb, mock_ollama)
        with pytest.raises(RuntimeError, match="Ollama client not healthy"):
            pipeline.query("Test query")

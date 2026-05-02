import logging
import subprocess
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Default Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "phi3.5:mini"


class OllamaClient:
    """Ollama client for interacting with local Ollama server and Phi-3.5-mini model."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model
        self.status = "not_initialized"
        self._session = requests.Session()

    def initialize(self) -> bool:
        """
        Initialize the Ollama client.
        Checks if Ollama is running and if the model is available.
        Auto-pulls the model if missing.
        """
        try:
            # Check if Ollama server is running
            if not self._check_server_health():
                logger.error("Ollama server is not running")
                self.status = "error"
                return False

            # Check if model exists, pull if missing
            if not self._model_exists(self.model):
                logger.info(f"Model {self.model} not found. Auto-pulling...")
                if not self._pull_model(self.model):
                    logger.error(f"Failed to pull model {self.model}")
                    self.status = "error"
                    return False

            self.status = "healthy"
            logger.info(f"Ollama client initialized successfully with model {self.model}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.status = "error"
            return False

    def _check_server_health(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _model_exists(self, model_name: str) -> bool:
        """Check if a model exists in Ollama."""
        try:
            response = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name") == model_name for m in models)
            return False
        except requests.RequestException:
            return False

    def _pull_model(self, model_name: str) -> bool:
        """Pull a model using Ollama API."""
        try:
            # Use subprocess to call ollama pull (more reliable than streaming API)
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout for model pull
            )
            if result.returncode == 0:
                logger.info(f"Successfully pulled model {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while pulling model {model_name}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def get_status(self) -> Dict[str, str]:
        """Return the status of Ollama client."""
        return {"status": self.status, "model": self.model}

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate a response using the Ollama model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature

        Returns:
            Generated text response
        """
        if self.status != "healthy":
            raise RuntimeError("Ollama client not initialized")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            logger.error(f"Error generating response: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Chat with the Ollama model using message history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        if self.status != "healthy":
            raise RuntimeError("Ollama client not initialized")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        try:
            response = self._session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.RequestException as e:
            logger.error(f"Error in chat: {e}")
            raise

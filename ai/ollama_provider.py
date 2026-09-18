"""Ollama LLM provider implementation."""

import json
from typing import List, Dict, Optional

import requests

from ai.provider import AIProvider
from core.config import Config
from core.logger import get_logger
from core.exceptions import AIProviderError

logger = get_logger("ollama")


class OllamaProvider(AIProvider):
    """Local LLM provider using Ollama."""

    def __init__(self) -> None:
        self.config = Config()
        self.base_url = self.config.ollama_base_url
        self.model = self.config.ollama_model
        self.timeout = 120

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                if self.model.split(":")[0] in models or not models:
                    return True
                # Model might be available with different tag
                logger.info(f"Available models: {models}")
                return True
            return False
        except requests.ConnectionError:
            logger.warning("Cannot connect to Ollama. Is it running?")
            return False
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send chat messages to Ollama and return the response."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.get("ai.temperature", 0.7),
                    "num_predict": self.config.get("ai.max_tokens", 2048),
                }
            }

            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )

            if resp.status_code != 200:
                raise AIProviderError(f"Ollama returned status {resp.status_code}: {resp.text}")

            data = resp.json()
            content = data.get("message", {}).get("content", "")
            if not content:
                raise AIProviderError("Ollama returned empty response.")
            return content.strip()

        except requests.ConnectionError:
            raise AIProviderError(
                "Cannot connect to Ollama. Please ensure Ollama is running: 'ollama serve'"
            )
        except requests.Timeout:
            raise AIProviderError("Ollama request timed out. The model may be loading.")
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"Ollama error: {str(e)}")

    def generate(self, prompt: str) -> str:
        """Generate text from a single prompt."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get("ai.temperature", 0.7),
                    "num_predict": self.config.get("ai.max_tokens", 2048),
                }
            }

            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if resp.status_code != 200:
                raise AIProviderError(f"Ollama returned status {resp.status_code}")

            data = resp.json()
            return data.get("response", "").strip()

        except requests.ConnectionError:
            raise AIProviderError("Cannot connect to Ollama.")
        except requests.Timeout:
            raise AIProviderError("Ollama request timed out.")
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"Ollama error: {str(e)}")

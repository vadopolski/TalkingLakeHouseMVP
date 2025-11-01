"""
Ollama LLM Client

Provides integration with Ollama for local LLM inference.
Uses simple HTTP requests to the Ollama API.
"""

import os
import json
import requests
from typing import Dict, List, Optional


class OllamaClient:
    """Client for interacting with Ollama local LLM"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "llama3.2",
        temperature: float = 0.1,
        max_tokens: int = 500
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate completion from Ollama

        Args:
            prompt: User prompt
            system_prompt: Optional system instruction

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat completion using Ollama

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Assistant's response
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is available and model is loaded"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(m.get("name", "").startswith(self.model) for m in models)
        except:
            return False

    def pull_model(self) -> bool:
        """Pull the model if not available"""
        url = f"{self.base_url}/api/pull"
        payload = {"name": self.model}

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return True
        except:
            return False

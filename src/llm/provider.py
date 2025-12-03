"""LLM provider abstraction with an OpenAI implementation."""
from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

try:  # Optional dependency
    import requests
except ModuleNotFoundError:  # pragma: no cover - allow tests without requests installed
    requests = None  # type: ignore

from src.config import Settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for chat-based LLM providers."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send chat messages and return the assistant's reply."""


class OpenAILLMProvider(LLMProvider):
    """OpenAI Chat Completions API wrapper."""

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        if not self.api_key:
            raise ValueError("OpenAI API key is required for OpenAI provider")
        if requests is None:
            raise ImportError("The requests package is required to use OpenAILLMProvider")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        if requests is None:  # pragma: no cover - defensive
            raise ImportError("The requests package is required to use OpenAILLMProvider")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        logger.debug("Sending request to OpenAI model %s", self.model)
        start = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        data = response.json()
        duration = time.time() - start
        logger.info("OpenAI response in %.2fs", duration)
        return data["choices"][0]["message"]["content"]


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Factory to instantiate the configured LLM provider."""

    provider = settings.llm_provider.lower()
    if provider == "openai":
        return OpenAILLMProvider(settings)
    raise ValueError(f"Unsupported LLM provider: {provider}")


__all__ = ["LLMProvider", "OpenAILLMProvider", "get_llm_provider"]

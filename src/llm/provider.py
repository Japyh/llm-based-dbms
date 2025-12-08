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

from src.config import Settings, BASE_HF_NL2SQL_MODEL, LOCAL_NL2SQL_ADAPTER_DIR

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


class LocalHFLLMProvider(LLMProvider):
    """
    Local Hugging Face LLM provider using fine-tuned LoRA adapter.
    
    This provider loads:
    - Base model: BASE_HF_NL2SQL_MODEL (from config.py)
    - LoRA adapter: LOCAL_NL2SQL_ADAPTER_DIR (from config.py)
    
    After running notebooks/03-kaggle-finetune-nl2sql.ipynb on Kaggle and downloading
    the adapter to models/nl2sql-mistral-lora/, this class will load both and use
    them for NL2SQL generation.
    """
    
    def __init__(self):
        """
        Initialize the local HF provider.
        
        TODO: After Kaggle fine-tuning is complete, implement:
        1. Load tokenizer from BASE_HF_NL2SQL_MODEL
        2. Load base model with quantization (optional for inference)
        3. Load PEFT adapter from LOCAL_NL2SQL_ADAPTER_DIR using PeftModel.from_pretrained
        4. Set model to eval mode
        """
        self.base_model_name = BASE_HF_NL2SQL_MODEL
        self.adapter_dir = LOCAL_NL2SQL_ADAPTER_DIR
        
        # Check if adapter exists
        if not self.adapter_dir.exists():
            raise FileNotFoundError(
                f"LoRA adapter not found at {self.adapter_dir}. "
                "Please run notebooks/03-kaggle-finetune-nl2sql.ipynb on Kaggle "
                "and download the output to this directory."
            )
        
        # TODO: Lazy loading - only load model when first chat() is called
        # This allows instantiation without GPU/memory overhead
        self.tokenizer = None
        self.model = None
    
    def _ensure_loaded(self):
        """
        Lazy load the model and tokenizer on first use.
        
        TODO: Implement full loading logic:
        - from transformers import AutoTokenizer, AutoModelForCausalLM
        - from peft import PeftModel
        - Load tokenizer
        - Load base model (optionally with 4-bit/8-bit quantization)
        - Load PEFT adapter
        """
        if self.model is not None:
            return
        
        # Placeholder - to be implemented after Kaggle fine-tuning
        raise NotImplementedError(
            "LocalHFLLMProvider model loading not yet implemented. "
            "This will be completed after Kaggle fine-tuning produces the adapter."
        )
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate SQL from natural language using fine-tuned model.
        
        Args:
            messages: Chat messages with system/user roles
                     Expected: [{"role": "system", ...}, {"role": "user", ...}]
        
        Returns:
            Generated SQL query as string
        
        TODO: Implement chat logic:
        1. Ensure model is loaded via _ensure_loaded()
        2. Use tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        3. Tokenize and move to device
        4. Generate with model.generate(...)
        5. Decode and return generated SQL
        """
        self._ensure_loaded()
        
        # Placeholder - to be implemented after Kaggle fine-tuning
        raise NotImplementedError(
            "LocalHFLLMProvider chat not yet implemented. "
            "This will be completed after Kaggle fine-tuning produces the adapter."
        )


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Factory to instantiate the configured LLM provider."""

    provider = settings.llm_provider.lower()
    if provider == "openai":
        return OpenAILLMProvider(settings)
    elif provider == "local_hf":
        return LocalHFLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {provider}")


__all__ = ["LLMProvider", "OpenAILLMProvider", "LocalHFLLMProvider", "get_llm_provider"]

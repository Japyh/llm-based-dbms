"""Application configuration settings."""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

try:  # Optional dependency
    from pydantic import BaseSettings, Field
except Exception:  # pragma: no cover - fallback when pydantic is absent
    BaseSettings = None  # type: ignore
    Field = None  # type: ignore


def _load_dotenv(path: Path) -> None:
    """Load environment variables from a .env file if present."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if BaseSettings is not None:

    class Settings(BaseSettings):
        """Typed application settings using Pydantic for parsing."""

        database_path: str = "data/sales.db"
        llm_provider: str = "openai"
        openai_api_key: Optional[str] = None
        openai_model: str = "gpt-4.1-mini"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

else:

    class Settings:  # type: ignore[no-redef]
        """Lightweight settings container when Pydantic is unavailable."""

        def __init__(
            self,
            database_path: str | None = None,
            llm_provider: str | None = None,
            openai_api_key: Optional[str] = None,
            openai_model: str | None = None,
        ) -> None:
            env_path = Path.cwd() / ".env"
            _load_dotenv(env_path)
            self.database_path = database_path or os.getenv("DATABASE_PATH", "data/sales.db")
            self.llm_provider = llm_provider or os.getenv("LLM_PROVIDER", "openai")
            self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            self.openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


_settings_lock = threading.Lock()
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Return a singleton Settings instance."""

    global _settings_instance
    if _settings_instance is None:
        with _settings_lock:
            if _settings_instance is None:
                if BaseSettings is not None:
                    _settings_instance = Settings()  # type: ignore[call-arg]
                else:
                    _settings_instance = Settings()
    return _settings_instance


# Fine-tuning configuration
# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# HF base model used for fine-tuning in Kaggle (shared between training and inference)
BASE_HF_NL2SQL_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Local adapter directory where Kaggle fine-tuned LoRA will be placed
LOCAL_NL2SQL_ADAPTER_DIR = BASE_DIR / "models" / "nl2sql-mistral-lora"


__all__ = ["Settings", "get_settings", "BASE_DIR", "BASE_HF_NL2SQL_MODEL", "LOCAL_NL2SQL_ADAPTER_DIR"]

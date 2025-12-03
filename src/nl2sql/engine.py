"""NL to SQL engine using an LLM provider and schema-aware prompts."""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

from src.config import Settings
from src.db import core as db_core
from src.llm.provider import LLMProvider
from src.nl2sql.prompt_templates import build_system_prompt, get_few_shot_examples
from src.validation import sql_validator

logger = logging.getLogger(__name__)


class NL2SQLEngine:
    """Convert natural language queries to validated SQL and execute them."""

    def __init__(self, db_module=db_core, llm: LLMProvider | None = None, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.db_module = db_module
        self.llm = llm or None

    def generate_sql(self, nl_query: str) -> str:
        """Generate SQL from natural language using the configured LLM."""

        if self.llm is None:
            raise ValueError("LLM provider is not configured")
        schema_description = self.db_module.get_schema_description(self.settings)
        system_prompt = build_system_prompt(schema_description)
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for nl_example, sql_example in get_few_shot_examples():
            messages.append({"role": "user", "content": nl_example})
            messages.append({"role": "assistant", "content": sql_example})
        messages.append({"role": "user", "content": nl_query})
        logger.debug("Sending NL query to LLM: %s", nl_query)
        response = self.llm.chat(messages)
        return self._clean_sql_response(response)

    def _clean_sql_response(self, response: str) -> str:
        """Remove code fences and ensure a single SQL statement remains."""

        cleaned = response.strip()
        cleaned = re.sub(r"^```sql", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1]
        return cleaned.strip()

    def run_nl_query(self, nl_query: str) -> Tuple[str, List[Dict]]:
        """Generate SQL, validate, execute, and return results."""

        sql = self.generate_sql(nl_query)
        schema_info = self.db_module.get_schema_info(self.settings)
        sql_validator.validate_sql(sql, schema_info)
        results = self.db_module.run_query(sql, settings=self.settings)
        return sql, results


__all__ = ["NL2SQLEngine"]

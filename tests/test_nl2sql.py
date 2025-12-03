"""Tests for NL2SQL engine cleaning logic."""
from __future__ import annotations

from src.config import Settings
from src.nl2sql.engine import NL2SQLEngine


class DummyLLM:
    def chat(self, messages):
        return "```sql\nSELECT 1;\n```"


def test_generate_sql_cleans_code_fence(tmp_path):
    settings = Settings(database_path=str(tmp_path / "dummy.db"))
    engine = NL2SQLEngine(llm=DummyLLM(), settings=settings)
    sql = engine.generate_sql("any question")
    assert sql == "SELECT 1"

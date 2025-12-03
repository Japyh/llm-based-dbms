"""Tests for database helper functions."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import Settings
from src.db import core


def setup_temp_db(tmp_path: Path) -> Settings:
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    try:
        conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT);")
        conn.execute("INSERT INTO sample (value) VALUES ('a'), ('b');")
        conn.commit()
    finally:
        conn.close()
    return Settings(database_path=str(db_file))


def test_get_schema_description(tmp_path: Path) -> None:
    settings = setup_temp_db(tmp_path)
    description = core.get_schema_description(settings)
    assert "Table sample" in description


def test_run_query_select(tmp_path: Path) -> None:
    settings = setup_temp_db(tmp_path)
    rows = core.run_query("SELECT 1 as col", settings=settings)
    assert rows == [{"col": 1}]

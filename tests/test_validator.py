"""Tests for SQL validator."""
from __future__ import annotations

import pytest

from src.validation import sql_validator


@pytest.fixture
def schema_info() -> dict:
    return {"sample": {"columns": {"id": {}, "value": {}}}}


def test_accepts_select(schema_info: dict) -> None:
    sql_validator.validate_sql("SELECT 1", schema_info)


def test_rejects_drop(schema_info: dict) -> None:
    with pytest.raises(sql_validator.InvalidQueryError):
        sql_validator.validate_sql("DROP TABLE sample", schema_info)


def test_rejects_update(schema_info: dict) -> None:
    with pytest.raises(sql_validator.InvalidQueryError):
        sql_validator.validate_sql("UPDATE sample SET value='x'", schema_info)

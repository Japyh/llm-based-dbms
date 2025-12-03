"""Core database utilities for interacting with SQLite."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.config import get_settings, Settings
from src.validation.sql_validator import is_safe_select

logger = logging.getLogger(__name__)


class ReadOnlyQueryError(ValueError):
    """Raised when a non-SELECT query is attempted."""


def get_connection(settings: Settings | None = None) -> sqlite3.Connection:
    """Create a SQLite connection to the configured database path.

    Args:
        settings: Optional settings instance. If omitted, the global settings are used.

    Returns:
        sqlite3.Connection with row factory set to sqlite3.Row.
    """

    settings = settings or get_settings()
    db_path = Path(settings.database_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_read_only(sql: str) -> None:
    """Ensure that the provided SQL is a read-only SELECT statement."""

    if not is_safe_select(sql):
        logger.error("Blocked non-read-only query: %s", sql)
        raise ReadOnlyQueryError("Only read-only SELECT queries are allowed")


def run_query(sql: str, params: Dict[str, Any] | Iterable[Any] | None = None, settings: Settings | None = None) -> List[Dict[str, Any]]:
    """Execute a read-only SQL query and return rows as dictionaries."""

    _ensure_read_only(sql)
    settings = settings or get_settings()
    conn = get_connection(settings)
    try:
        cursor = conn.execute(sql, params or {})
        rows = [dict(row) for row in cursor.fetchall()]
        logger.debug("Executed query returned %d rows", len(rows))
        return rows
    finally:
        conn.close()


def get_schema_info(settings: Settings | None = None) -> Dict[str, Dict[str, Any]]:
    """Return structured schema information.

    Returns a dictionary of table name to column metadata (name and type).
    """

    settings = settings or get_settings()
    conn = get_connection(settings)
    schema: Dict[str, Dict[str, Any]] = {}
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            col_cursor = conn.execute(f"PRAGMA table_info({table})")
            columns = {row[1]: {"type": row[2], "notnull": bool(row[3]), "default": row[4]} for row in col_cursor.fetchall()}
            schema[table] = {"columns": columns}
        return schema
    finally:
        conn.close()


def get_schema_description(settings: Settings | None = None) -> str:
    """Generate a human-readable description of the database schema."""

    schema_info = get_schema_info(settings)
    lines: List[str] = []
    for table, meta in schema_info.items():
        lines.append(f"Table {table}:")
        for column, col_meta in meta["columns"].items():
            nullable = "NOT NULL" if col_meta.get("notnull") else "NULLABLE"
            default = col_meta.get("default")
            default_part = f", default={default}" if default is not None else ""
            lines.append(f"  - {column} ({col_meta.get('type', 'UNKNOWN')} {nullable}{default_part})")
    description = "\n".join(lines)
    logger.debug("Schema description generated with %d tables", len(schema_info))
    return description


__all__ = ["get_connection", "run_query", "get_schema_description", "get_schema_info", "ReadOnlyQueryError"]

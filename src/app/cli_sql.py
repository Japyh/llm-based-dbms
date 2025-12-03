"""Command-line SQL REPL with validation."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable

from src import config
from src.db import core as db_core
from src.validation import sql_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _format_rows(rows: Iterable[Dict[str, Any]]) -> str:
    rows = list(rows)
    if not rows:
        return "(no rows)"
    headers = rows[0].keys()
    lines = [" | ".join(str(h) for h in headers)]
    lines.append("-+-".join("-" * len(str(h)) for h in headers))
    for row in rows:
        lines.append(" | ".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines)


def repl() -> None:
    """Interactive SQL shell with schema validation."""

    settings = config.get_settings()
    schema_info = db_core.get_schema_info(settings)
    while True:
        try:
            user_input = input("SQL> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"q", "quit"}:
            break
        try:
            sql_validator.validate_sql(user_input, schema_info)
            rows = db_core.run_query(user_input, settings=settings)
            print(_format_rows(rows))
        except Exception as exc:
            logger.error("Error: %s", exc)


if __name__ == "__main__":  # pragma: no cover
    repl()

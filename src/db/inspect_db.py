"""Utility script to inspect the SQLite database schema and sample rows."""
from __future__ import annotations

import logging
from typing import Any

from src.db.core import get_connection, get_schema_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(show_samples: bool = True, sample_limit: int = 5) -> None:
    """Print the tables, columns, and optional sample rows from the database."""

    schema = get_schema_info()
    if not schema:
        logger.warning("No tables found in database")
        return

    for table, meta in schema.items():
        print(f"\nTable: {table}")
        for column, col_meta in meta["columns"].items():
            print(f"  - {column}: {col_meta.get('type')} (not null: {col_meta.get('notnull')})")
        if show_samples:
            conn = get_connection()
            try:
                cursor = conn.execute(f"SELECT * FROM {table} LIMIT {sample_limit}")
                rows = cursor.fetchall()
                if not rows:
                    print("  (no sample rows)")
                    continue
                columns = [col[0] for col in cursor.description]
                print("  Sample rows:")
                for row in rows:
                    row_dict = {col: row[idx] for idx, col in enumerate(columns)}
                    print(f"    {row_dict}")
            except Exception as exc:  # pragma: no cover - informational
                logger.error("Failed to fetch samples for %s: %s", table, exc)
            finally:
                conn.close()


if __name__ == "__main__":  # pragma: no cover - manual script
    main()

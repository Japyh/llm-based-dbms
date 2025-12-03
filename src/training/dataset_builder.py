"""Rule-based NL↔SQL dataset builder for fine-tuning."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from src.db.core import get_schema_info

logger = logging.getLogger(__name__)


def get_schema_metadata() -> Dict:
    """Return structured schema metadata suitable for dataset generation."""

    return get_schema_info()


def generate_sql_templates(schema_meta: Dict) -> List[str]:
    """Generate SQL templates based on schema metadata."""

    templates: List[str] = []
    tables = list(schema_meta.keys())
    for table in tables:
        columns = list(schema_meta[table]["columns"].keys())
        if columns:
            templates.append(f"SELECT * FROM {table} LIMIT 10;")
            templates.append(f"SELECT COUNT(*) AS count_{table} FROM {table};")
            first_col = columns[0]
            templates.append(f"SELECT {first_col}, COUNT(*) AS frequency FROM {table} GROUP BY {first_col} ORDER BY frequency DESC LIMIT 10;")
    if "orders" in schema_meta and "order_details" in schema_meta:
        templates.append(
            "SELECT o.id, SUM(od.quantity * od.unit_price) AS order_total "
            "FROM orders o JOIN order_details od ON o.id = od.order_id "
            "GROUP BY o.id ORDER BY order_total DESC LIMIT 10;"
        )
    if "orders" in schema_meta:
        templates.append(
            "SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) AS order_count "
            "FROM orders GROUP BY month ORDER BY month;"
        )
    return templates


def generate_nl_for_sql(sql: str) -> str:
    """Generate a natural language description for a SQL query."""

    normalized = sql.lower()
    if "count" in normalized and "group by" not in normalized:
        return "Return the total number of records."
    if "group by" in normalized and "order_total" in normalized:
        return "Show top orders by total revenue."
    if "group by" in normalized:
        return "Summarize results grouped by the specified column."
    if "join" in normalized:
        return "List combined information from related tables."
    return "Retrieve records according to the specified filters."


def build_pairs(limit: int | None = None) -> List[Dict[str, str]]:
    """Build NL-SQL training pairs."""

    schema_meta = get_schema_metadata()
    sql_templates = generate_sql_templates(schema_meta)
    pairs: List[Dict[str, str]] = []
    for sql in sql_templates[:limit]:
        nl = generate_nl_for_sql(sql)
        pairs.append({"input": nl, "output": sql})
    return pairs


def export_to_jsonl(pairs: List[Dict[str, str]], path: str) -> None:
    """Export NL-SQL pairs to a JSONL file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    logger.info("Exported %d pairs to %s", len(pairs), path)


def main() -> None:  # pragma: no cover - convenience script
    pairs = build_pairs(limit=100)
    export_to_jsonl(pairs, "data/nl2sql_training.jsonl")
    print("Generated", len(pairs), "pairs at data/nl2sql_training.jsonl")


if __name__ == "__main__":  # pragma: no cover
    main()

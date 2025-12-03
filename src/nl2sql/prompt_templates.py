"""Prompt templates for converting natural language to SQL."""
from __future__ import annotations

from typing import List, Tuple


def build_system_prompt(schema_description: str) -> str:
    """Build the system prompt embedding schema and safety rules."""

    return (
        "You are a precise Text-to-SQL generator for SQLite. "
        "Generate a single valid SQL SELECT statement based on the user's question. "
        "Do not include explanations. Only return the SQL.\n\n"
        "Database schema:\n" + schema_description + "\n\n"
        "Rules:\n"
        "- Only use SELECT queries.\n"
        "- Never modify data: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, ATTACH, DETACH are forbidden.\n"
        "- Use columns and tables exactly as provided in the schema.\n"
    )


def get_few_shot_examples() -> List[Tuple[str, str]]:
    """Return generic few-shot NL↔SQL examples to guide the model."""

    return [
        (
            "List the first 5 rows from the products table.",
            "SELECT * FROM products LIMIT 5;",
        ),
        (
            "Show total sales amount per customer ordered by total descending.",
            "SELECT customer_id, SUM(total_amount) AS total_sales FROM orders GROUP BY customer_id ORDER BY total_sales DESC;",
        ),
        (
            "Find the top 10 products by quantity sold.",
            "SELECT product_id, SUM(quantity) AS total_quantity FROM order_details GROUP BY product_id ORDER BY total_quantity DESC LIMIT 10;",
        ),
    ]


__all__ = ["build_system_prompt", "get_few_shot_examples"]

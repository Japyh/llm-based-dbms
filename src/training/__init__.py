"""Utilities for generating NL↔SQL training data."""
from .dataset_builder import (
    get_schema_metadata,
    generate_sql_templates,
    generate_nl_for_sql,
    build_pairs,
    export_to_jsonl,
)

__all__ = [
    "get_schema_metadata",
    "generate_sql_templates",
    "generate_nl_for_sql",
    "build_pairs",
    "export_to_jsonl",
]

"""Utilities for generating NL↔SQL training data."""
from .dataset_builder import (
    get_schema_metadata,
    generate_sql_templates,
    generate_nl_variants_for_sql,
    build_chat_dataset,
    export_chat_jsonl,
    make_chat_example,
)

__all__ = [
    "get_schema_metadata",
    "generate_sql_templates",
    "generate_nl_variants_for_sql",
    "build_chat_dataset",
    "export_chat_jsonl",
    "make_chat_example",
]

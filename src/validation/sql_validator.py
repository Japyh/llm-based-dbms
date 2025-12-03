"""SQL validation for safety and schema compliance."""
from __future__ import annotations

import logging
import re
from typing import Dict, Set

try:
    import sqlparse
    from sqlparse.sql import Identifier, IdentifierList
    from sqlparse.tokens import Keyword
except ModuleNotFoundError:  # pragma: no cover - fallback when sqlparse is unavailable
    sqlparse = None  # type: ignore
    Identifier = IdentifierList = Keyword = object  # type: ignore

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "CREATE",
    "REPLACE",
    "PRAGMA",
}


class InvalidQueryError(ValueError):
    """Raised when a SQL query fails safety or schema validation."""


def is_safe_select(sql: str) -> bool:
    """Check whether SQL is a single SELECT statement without forbidden keywords."""

    if sqlparse:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False
        first = parsed[0]
        first_token = first.token_first(skip_cm=True)
        if not first_token or first_token.normalized.upper() != "SELECT":
            return False
    else:
        stripped = sql.strip().upper()
        if not stripped.startswith("SELECT"):
            return False
    upper_sql = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, upper_sql, flags=re.IGNORECASE):
            return False
    return True


def _extract_from_tokens(token) -> Set[str]:
    tables: Set[str] = set()
    if sqlparse is None:
        return tables
    if isinstance(token, IdentifierList):
        for identifier in token.get_identifiers():
            name = identifier.get_real_name()
            if name:
                tables.add(name)
    elif isinstance(token, Identifier):
        name = token.get_real_name()
        if name:
            tables.add(name)
    elif getattr(token, "is_group", False):
        for sub in token.tokens:
            tables.update(_extract_from_tokens(sub))
    return tables


def extract_identifiers(sql: str) -> Dict[str, Set[str]]:
    """Best-effort extraction of table and column identifiers from SQL."""

    if sqlparse is None:
        return {"tables": set(), "columns": set()}
    parsed = sqlparse.parse(sql)
    if not parsed:
        return {"tables": set(), "columns": set()}
    statement = parsed[0]
    tables: Set[str] = set()
    columns: Set[str] = set()
    for token in statement.tokens:
        if token.ttype is Keyword and token.normalized.upper() == "FROM":
            next_token = statement.token_next(statement.token_index(token))
            if next_token:
                tables.update(_extract_from_tokens(next_token))
        if isinstance(token, Identifier):
            if token.get_parent_name():
                columns.add(token.get_real_name())
    return {"tables": tables, "columns": columns}


def validate_against_schema(sql: str, schema_info: Dict) -> bool:
    """Ensure tables and columns referenced in SQL exist in schema_info."""

    identifiers = extract_identifiers(sql)
    tables = identifiers.get("tables", set())
    columns = identifiers.get("columns", set())
    for table in tables:
        if table not in schema_info:
            logger.error("Unknown table referenced: %s", table)
            return False
    if tables and columns:
        for column in columns:
            if not any(column in schema_info[table]["columns"] for table in tables if table in schema_info):
                logger.error("Unknown column referenced: %s", column)
                return False
    return True


def validate_sql(sql: str, schema_info: Dict) -> None:
    """Validate SQL for safety and schema correctness."""

    if not is_safe_select(sql):
        raise InvalidQueryError("Only safe SELECT queries are allowed")
    if not validate_against_schema(sql, schema_info):
        raise InvalidQueryError("Query references unknown tables or columns")


def normalize_sql(sql: str) -> str:
    """Normalize SQL whitespace and remove trailing semicolons."""

    stripped = sql.strip().rstrip(";")
    if sqlparse:
        return sqlparse.format(stripped, reindent=True, keyword_case="upper")
    return " ".join(stripped.split())


__all__ = [
    "InvalidQueryError",
    "is_safe_select",
    "extract_identifiers",
    "validate_against_schema",
    "validate_sql",
    "normalize_sql",
]

from __future__ import annotations

import re
from typing import Tuple

BLACKLISTED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]

_BLACKLIST_PATTERN = re.compile(r"\b(" + "|".join(BLACKLISTED_KEYWORDS) + r")\b", re.IGNORECASE)


def is_query_safe(sql_query: str) -> Tuple[bool, str]:
    """
    Perform basic validation to ensure the SQL query is read-only and free of destructive commands.
    """
    if not sql_query or not sql_query.strip():
        return False, "Query is empty."

    cleaned = sql_query.strip()

    if not cleaned.upper().startswith("SELECT"):
        return False, "Only SELECT statements are allowed."

    match = _BLACKLIST_PATTERN.search(cleaned)
    if match:
        keyword = match.group(0).upper()
        return False, f"Query contains disallowed keyword: {keyword}"

    return True, "Query is safe."

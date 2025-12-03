"""Command-line natural language REPL using the NL2SQL engine."""
from __future__ import annotations

import logging

from src import config
from src.llm.provider import get_llm_provider
from src.nl2sql.engine import NL2SQLEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def repl() -> None:
    """Interactive NL -> SQL shell."""

    settings = config.get_settings()
    llm = get_llm_provider(settings)
    engine = NL2SQLEngine(llm=llm, settings=settings)
    while True:
        try:
            user_input = input("NL> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"q", "quit"}:
            break
        try:
            sql, rows = engine.run_nl_query(user_input)
            print("\nSQL:\n```\n" + sql + "\n```")
            print(f"Rows returned: {len(rows)}")
            if rows:
                print(rows[:5])
        except Exception as exc:
            logger.error("Error: %s", exc)


if __name__ == "__main__":  # pragma: no cover
    repl()

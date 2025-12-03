"""Simple Streamlit UI for running natural language queries."""
from __future__ import annotations

import time

import streamlit as st

from src import config
from src.llm.provider import get_llm_provider
from src.nl2sql.engine import NL2SQLEngine


def main() -> None:
    st.title("LLM-based Database Explorer")
    settings = config.get_settings()
    llm = get_llm_provider(settings)
    engine = NL2SQLEngine(llm=llm, settings=settings)

    nl_query = st.text_area("Enter a question", placeholder="Show the top 10 orders by quantity in 2024")
    if st.button("Run query"):
        start = time.time()
        try:
            sql, rows = engine.run_nl_query(nl_query)
            elapsed = time.time() - start
            st.subheader("Generated SQL")
            st.code(sql, language="sql")
            st.subheader("Results")
            st.dataframe(rows)
            st.caption(f"Executed in {elapsed:.2f}s")
        except Exception as exc:
            st.error(str(exc))


if __name__ == "__main__":  # pragma: no cover
    main()

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.database import get_db_connection, get_schema, run_query
from src.llm_chain import create_query_chain
from src.validator import is_query_safe


st.set_page_config(page_title="LLM-Based Database Management System", layout="wide")


@st.cache_resource(show_spinner=False)
def load_schema() -> str:
    with get_db_connection() as conn:
        return get_schema(conn)


@st.cache_resource(show_spinner=False)
def load_chain():
    schema = load_schema()
    return create_query_chain(schema)


def main() -> None:
    st.title("LLM-Based Database Management System")

    st.markdown(
        "Enter a natural language question about your sales data. "
        "The application will translate it into SQL, validate it, and execute the query if it is safe."
    )

    with st.expander("View database schema"):
        st.code(load_schema(), language="sql")

    user_query = st.text_area("Ask a question", placeholder="How many products were sold last month?")

    if st.button("Generate & Run SQL"):
        if not user_query.strip():
            st.warning("Please enter a question before running the query.")
            return

        chain = load_chain()
        try:
            generated_sql = chain.invoke({"question": user_query})
        except Exception as exc:  # noqa: BLE001
            st.error(f"Failed to generate SQL: {exc}")
            return

        if not isinstance(generated_sql, str):
            st.error("The LLM chain returned an unexpected response.")
            return

        st.subheader("Generated SQL")
        st.code(generated_sql, language="sql")

        is_safe, message = is_query_safe(generated_sql)
        if not is_safe:
            st.error(f"Query rejected: {message}")
            return

        st.success("Query passed validation. Executing on the database...")
        try:
            with get_db_connection() as conn:
                rows, columns = run_query(conn, generated_sql)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Failed to execute SQL: {exc}")
            return

        if not rows:
            st.info("Query executed successfully but returned no rows.")
        else:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)

        st.caption(message)


if __name__ == "__main__":
    main()

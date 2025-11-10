from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import List, Sequence, Tuple

import pandas as pd

DB_PATH = Path("./data/sales.sqlite3")


def get_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Create and return a SQLite3 connection.
    The directory for the database is created if it does not already exist.
    """
    db_path = Path(db_path)
    if db_path.parent and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(conn: sqlite3.Connection, sql_query: str) -> Tuple[List[Tuple], List[str]]:
    """
    Execute a SQL query and return the rows and column names.
    """
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description] if cursor.description else []
    return [tuple(row) for row in rows], column_names


def get_schema(conn: sqlite3.Connection) -> str:
    """
    Inspect sqlite_master to build a string representation of the database schema.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            name,
            sql
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
        """
    )
    rows = cursor.fetchall()
    if not rows:
        return "No tables found in the database."

    schema_parts: List[str] = []
    for row in rows:
        table_name = row["name"]
        create_statement = row["sql"]
        schema_parts.append(f"-- Table: {table_name}\n{create_statement}")
    return "\n\n".join(schema_parts)


def populate_database(
    db_path: Path = DB_PATH,
    csv_path: Path = Path("./data/sales_data.csv"),
    table_name: str = "sales",
) -> None:
    """
    Placeholder utility to populate the database from a CSV file.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found at {csv_path}. Please provide a dataset before populating."
        )

    df = pd.read_csv(csv_path)
    with get_db_connection(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def _parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database utilities for the LLM DBMS project.")
    parser.add_argument(
        "--populate",
        action="store_true",
        help="Populate the SQLite database from the default CSV dataset.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("./data/sales_data.csv"),
        help="Path to the CSV file used when populating the database.",
    )
    parser.add_argument(
        "--table",
        type=str,
        default="sales",
        help="Destination table name when populating the database.",
    )
    return parser.parse_args(args=args)


def main() -> None:
    args = _parse_args()
    if args.populate:
        populate_database(DB_PATH, args.csv, args.table)
        print(f"Database populated at {DB_PATH.resolve()} (table `{args.table}`).")
    else:
        print("No action taken. Use --populate to load data into the database.")


if __name__ == "__main__":
    main()

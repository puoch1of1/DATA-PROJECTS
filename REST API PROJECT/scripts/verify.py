import argparse
import re
import sqlite3
import pandas as pd
from pathlib import Path


def _validate_table_name(table_name: str):
    if not isinstance(table_name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError(
            "Invalid table name. Use only letters, numbers, and underscore, and start with a letter or underscore."
        )


def verify_table(db_path: Path, table_name: str = "development_indicators", limit: int = 10):
    _validate_table_name(table_name)
    conn = sqlite3.connect(db_path)
    try:
        result = pd.read_sql(
            (
                f"SELECT country, year, indicator, value, ingested_at "
                f"FROM {table_name} ORDER BY year DESC LIMIT {int(limit)}"
            ),
            conn
        )
        total_rows = pd.read_sql(
            f"SELECT COUNT(*) AS row_count FROM {table_name}",
            conn
        )
        null_summary = pd.read_sql(
            f"""
            SELECT
                SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country,
                SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
                SUM(CASE WHEN indicator IS NULL THEN 1 ELSE 0 END) AS null_indicator,
                SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
            FROM {table_name}
            """,
            conn
        )

        duplicate_keys = pd.read_sql(
            f"""
            SELECT country, year, indicator, COUNT(*) AS duplicate_count
            FROM {table_name}
            GROUP BY country, year, indicator
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
            """,
            conn,
        )

        indicator_coverage = pd.read_sql(
            f"""
            SELECT
                indicator,
                COUNT(*) AS rows,
                MIN(year) AS min_year,
                MAX(year) AS max_year
            FROM {table_name}
            GROUP BY indicator
            ORDER BY indicator
            """,
            conn,
        )

        return {
            "latest_rows": result,
            "row_count": int(total_rows.iloc[0]["row_count"]),
            "null_summary": null_summary.iloc[0].to_dict(),
            "duplicate_keys": duplicate_keys,
            "indicator_coverage": indicator_coverage,
        }
    finally:
        conn.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Verify loaded development indicators table")
    parser.add_argument("--db", default="database/worldbank.db", help="SQLite database path")
    parser.add_argument("--table", default="development_indicators", help="Table name to verify")
    parser.add_argument("--limit", default=10, type=int, help="Number of latest rows to display")
    return parser.parse_args()


def main():
    args = parse_args()
    project_dir = Path(__file__).resolve().parent.parent
    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = project_dir / db_path

    verification = verify_table(db_path, args.table, args.limit)
    print(f"Rows in table: {verification['row_count']}")
    print("Null summary:", verification["null_summary"])
    print("Indicator coverage:")
    print(verification["indicator_coverage"])

    if verification["duplicate_keys"].empty:
        print("Duplicate business keys: none")
    else:
        print("Duplicate business keys found:")
        print(verification["duplicate_keys"])

    print("Latest rows:")
    print(verification["latest_rows"])


if __name__ == "__main__":
    main()
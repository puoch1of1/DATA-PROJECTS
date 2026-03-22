import sqlite3
import pandas as pd
from pathlib import Path


def verify_table(db_path: Path, table_name: str = "development_indicators"):
    conn = sqlite3.connect(db_path)
    try:
        result = pd.read_sql(
            f"SELECT * FROM {table_name} ORDER BY year DESC LIMIT 10",
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
        return result, total_rows.iloc[0]["row_count"], null_summary.iloc[0].to_dict()
    finally:
        conn.close()


def main():
    project_dir = Path(__file__).resolve().parent.parent
    db_path = project_dir / "database" / "worldbank.db"

    sample, row_count, nulls = verify_table(db_path)
    print(f"Rows in table: {row_count}")
    print("Null summary:", nulls)
    print("Latest rows:")
    print(sample)


if __name__ == "__main__":
    main()
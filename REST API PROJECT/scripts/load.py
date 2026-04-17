import os
import re
import sqlite3

import pandas as pd

REQUIRED_COLUMNS = ["country", "year", "indicator", "value", "ingested_at"]


def _validate_table_name(table_name: str):
    if not isinstance(table_name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError(
            "Invalid table name. Use only letters, numbers, and underscore, and start with a letter or underscore."
        )


def _normalize_dataframe(df: pd.DataFrame):
    cleaned = df.copy()

    for col in REQUIRED_COLUMNS:
        if col not in cleaned.columns:
            cleaned[col] = None

    cleaned = cleaned[REQUIRED_COLUMNS]
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce").astype("Int64")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = cleaned.dropna(subset=["country", "year", "indicator", "value"])
    cleaned["year"] = cleaned["year"].astype("int64")

    return cleaned


def _ensure_table_schema(conn: sqlite3.Connection, table_name: str):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            country TEXT,
            year INTEGER,
            indicator TEXT,
            value REAL,
            ingested_at TEXT
        )
        """
    )

    existing_cols = {
        row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }

    # Migrate legacy schema that included an index export column.
    if "Unnamed: 0" in existing_cols:
        temp_table = f"{table_name}__normalized"
        conn.execute(
            f"""
            CREATE TABLE {temp_table} (
                country TEXT,
                year INTEGER,
                indicator TEXT,
                value REAL,
                ingested_at TEXT
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO {temp_table} (country, year, indicator, value, ingested_at)
            SELECT country, year, indicator, value, NULL AS ingested_at
            FROM {table_name}
            """
        )
        conn.execute(f"DROP TABLE {table_name}")
        conn.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
        existing_cols = {
            row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        }

    if "ingested_at" not in existing_cols:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN ingested_at TEXT")

    conn.execute(
        f"""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_{table_name}_business_key
        ON {table_name} (country, year, indicator)
        """
    )


def _delete_existing_keys(conn: sqlite3.Connection, table_name: str, df: pd.DataFrame):
    keys = list({(row.country, int(row.year), row.indicator) for row in df.itertuples(index=False)})
    if not keys:
        return

    conn.executemany(
        f"DELETE FROM {table_name} WHERE country = ? AND year = ? AND indicator = ?",
        keys,
    )


def load_to_sqlite(df, db_path, table_name):
    _validate_table_name(table_name)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    prepared_df = _normalize_dataframe(df)
    if prepared_df.empty:
        raise ValueError("No valid rows available for loading after normalization")

    conn = sqlite3.connect(db_path)
    try:
        _ensure_table_schema(conn, table_name)
        _delete_existing_keys(conn, table_name, prepared_df)

        prepared_df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )
        conn.commit()
    finally:
        conn.close()


def load_data_pipeline(csv_path, db_path, table_name="development_indicators"):
    """Load CSV data into SQLite database"""
    df = pd.read_csv(csv_path)
    load_to_sqlite(df, db_path, table_name)
    return df

# Main execution when run directly
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    csv_path = os.path.join(project_dir, "data", "cleaned", "south_sudan_clean.csv")
    db_path = os.path.join(project_dir, "database", "worldbank.db")

    load_data_pipeline(csv_path, db_path)

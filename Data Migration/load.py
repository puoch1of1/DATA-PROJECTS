import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine

from config import POSTGRES_CONN_STR, require_config
from db_utils import validate_identifier
from extract import extract_table


LOAD_MODES = {"append", "truncate", "replace"}


def postgres_table_exists(table_name: str, schema: str | None = None) -> bool:
    target_schema = schema or "public"
    require_config()
    with psycopg2.connect(POSTGRES_CONN_STR) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                )
                """,
                (target_schema, table_name),
            )
            return bool(cursor.fetchone()[0])


def truncate_postgres_table(table_name: str, schema: str | None = None) -> bool:
    target_schema = schema or "public"
    require_config()
    if not postgres_table_exists(table_name, target_schema):
        return False

    with psycopg2.connect(POSTGRES_CONN_STR) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("TRUNCATE TABLE {}").format(
                    sql.Identifier(target_schema, table_name)
                )
            )
    return True


def load_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    schema: str | None = None,
    load_mode: str = "truncate",
    chunk_size: int = 1000,
) -> int:
    require_config()
    validate_identifier(table_name, "table name")
    target_schema = schema or "public"
    validate_identifier(target_schema, "schema name")

    if load_mode not in LOAD_MODES:
        raise ValueError(f"Unsupported load mode: {load_mode!r}")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if df.empty:
        return 0

    if load_mode == "truncate":
        truncate_postgres_table(table_name, target_schema)

    if_exists = "replace" if load_mode == "replace" else "append"
    try:
        engine = create_engine(POSTGRES_CONN_STR)
    except Exception as exc:
        raise RuntimeError(f"Postgres engine creation failed: {exc}") from exc

    try:
        df.to_sql(
            table_name,
            engine,
            schema=target_schema,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=chunk_size,
        )
    finally:
        engine.dispose()

    return len(df)


if __name__ == "__main__":
    try:
        dataframe = extract_table("customers", schema="dbo")
        rows = load_to_postgres(dataframe, "customers")
        print(f"Data loaded successfully: {rows} rows.")
    except Exception as exc:
        print(f"Load error: {exc}")

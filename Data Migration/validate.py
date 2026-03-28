from dataclasses import dataclass

import psycopg2
import pyodbc
from psycopg2 import sql

from config import POSTGRES_CONN_STR, SQLSERVER_CONN_STR, require_config
from db_utils import qualify_sqlserver_table, validate_identifier


@dataclass(slots=True)
class RowCountValidation:
    source_count: int
    target_count: int

    @property
    def matched(self) -> bool:
        return self.source_count == self.target_count


def get_sqlserver_count(table: str, schema: str | None = None) -> int:
    require_config()
    validate_identifier(table, "table name")
    if schema:
        validate_identifier(schema, "schema name")

    full_name = qualify_sqlserver_table(table, schema=schema)
    try:
        conn = pyodbc.connect(SQLSERVER_CONN_STR)
    except pyodbc.Error as exc:
        raise RuntimeError(f"SQL Server connection failed: {exc}") from exc

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
        return int(cursor.fetchone()[0])
    finally:
        conn.close()


def get_postgres_count(table: str, schema: str | None = None) -> int:
    require_config()
    validate_identifier(table, "table name")
    target_schema = schema or "public"
    validate_identifier(target_schema, "schema name")

    try:
        conn = psycopg2.connect(POSTGRES_CONN_STR)
    except psycopg2.Error as exc:
        raise RuntimeError(f"Postgres connection failed: {exc}") from exc

    try:
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}").format(
                sql.Identifier(target_schema, table)
            )
        )
        return int(cursor.fetchone()[0])
    finally:
        conn.close()


def validate_row_counts(
    table: str,
    source_schema: str | None = None,
    target_schema: str | None = None,
) -> RowCountValidation:
    source_count = get_sqlserver_count(table, schema=source_schema)
    target_count = get_postgres_count(table, schema=target_schema)
    return RowCountValidation(source_count=source_count, target_count=target_count)


if __name__ == "__main__":
    table_name = "customers"
    try:
        result = validate_row_counts(
            table_name,
            source_schema="dbo",
            target_schema="public",
        )
        print(f"SQL Server rows: {result.source_count}")
        print(f"Postgres rows: {result.target_count}")
    except Exception as exc:
        print(f"Validation error: {exc}")

import pyodbc
import psycopg2
from config import SQLSERVER_CONN_STR, POSTGRES_CONN_STR, require_config

def get_sqlserver_count(table: str, schema: str | None = None) -> int:
    require_config()
    full_name = f"{schema}.{table}" if schema else table
    try:
        conn = pyodbc.connect(SQLSERVER_CONN_STR)
    except pyodbc.Error as e:
        raise RuntimeError(f"SQL Server connection failed: {e}") from e
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
        count = cursor.fetchone()[0]
    finally:
        conn.close()
    return count

def get_postgres_count(table: str, schema: str | None = None) -> int:
    require_config()
    full_name = f"{schema}.{table}" if schema else table
    try:
        conn = psycopg2.connect(POSTGRES_CONN_STR)
    except psycopg2.Error as e:
        raise RuntimeError(f"Postgres connection failed: {e}") from e
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
        count = cursor.fetchone()[0]
    finally:
        conn.close()
    return count

if __name__ == "__main__":
    table = "customers"
    try:
        src = get_sqlserver_count(table, schema="dbo")
        tgt = get_postgres_count(table)
        print(f"SQL Server rows: {src}")
        print(f"Postgres rows: {tgt}")
    except Exception as e:
        print(f"Validation error: {e}")

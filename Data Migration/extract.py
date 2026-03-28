import pandas as pd
import pyodbc

from config import SQLSERVER_CONN_STR, require_config
from db_utils import qualify_sqlserver_table, validate_identifier


def extract_table(table_name: str, schema: str | None = None) -> pd.DataFrame:
    """Extract all rows from a SQL Server table."""
    require_config()
    validate_identifier(table_name, "table name")
    if schema:
        validate_identifier(schema, "schema name")

    full_name = qualify_sqlserver_table(table_name, schema=schema)
    try:
        conn = pyodbc.connect(SQLSERVER_CONN_STR)
    except pyodbc.Error as exc:
        raise RuntimeError(f"SQL Server connection failed: {exc}") from exc

    try:
        query = f"SELECT * FROM {full_name}"
        return pd.read_sql(query, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        dataframe = extract_table("customers", schema="dbo")
        print(dataframe.head())
    except Exception as exc:
        print(f"Extraction error: {exc}")

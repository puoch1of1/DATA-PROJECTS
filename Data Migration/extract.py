import pyodbc
import pandas as pd
from config import SQLSERVER_CONN_STR, require_config

def extract_table(table_name: str, schema: str | None = None) -> pd.DataFrame:
    """Extract all rows from a SQL Server table.

    Args:
        table_name: Table name to extract.
        schema: Optional schema name (e.g., 'dbo').
    """
    require_config()
    full_name = f"{schema}.{table_name}" if schema else table_name
    try:
        conn = pyodbc.connect(SQLSERVER_CONN_STR)
    except pyodbc.Error as e:
        raise RuntimeError(f"SQL Server connection failed: {e}") from e
    try:
        query = f"SELECT * FROM {full_name}"
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df

if __name__ == "__main__":
    try:
        df = extract_table("customers", schema="dbo")
        print(df.head())
    except Exception as e:
        print(f"Extraction error: {e}")

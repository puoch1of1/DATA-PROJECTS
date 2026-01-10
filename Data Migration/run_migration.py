from pathlib import Path
import psycopg2
from config import POSTGRES_CONN_STR
from extract import extract_table
from load import load_to_postgres
from validate import get_sqlserver_count, get_postgres_count

def ensure_postgres_schema() -> None:
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "postgres_schema.sql"
    ddl = sql_path.read_text(encoding="utf-8")
    conn = psycopg2.connect(POSTGRES_CONN_STR)
    try:
        cur = conn.cursor()
        cur.execute(ddl)
        conn.commit()
    finally:
        conn.close()

def main() -> None:
    table = "customers"
    # 1. Extract from SQL Server
    df = extract_table(table, schema="dbo")
    print(f"Extracted {len(df)} rows from SQL Server.")
    # 2. Ensure Postgres schema
    ensure_postgres_schema()
    print("Ensured Postgres schema is present.")
    # 3. Load to Postgres
    load_to_postgres(df, table)
    print("Loaded data into Postgres.")
    # 4. Validate counts
    src_cnt = get_sqlserver_count(table, schema="dbo")
    tgt_cnt = get_postgres_count(table)
    print(f"SQL Server rows: {src_cnt}")
    print(f"Postgres rows: {tgt_cnt}")
    if src_cnt == tgt_cnt:
        print("Row counts match ✔")
    else:
        print("Row counts do not match ✖")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Migration run failed: {e}")
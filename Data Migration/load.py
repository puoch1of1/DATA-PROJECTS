import pandas as pd
from sqlalchemy import create_engine
from config import POSTGRES_CONN_STR, require_config
from extract import extract_table

def load_to_postgres(df: pd.DataFrame, table_name: str) -> None:
    require_config()
    try:
        engine = create_engine(POSTGRES_CONN_STR)
    except Exception as e:
        raise RuntimeError(f"Postgres engine creation failed: {e}") from e
    try:
        df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )
    finally:
        engine.dispose()

if __name__ == "__main__":
    try:
        df = extract_table("customers", schema="dbo")
        load_to_postgres(df, "customers")
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Load error: {e}")

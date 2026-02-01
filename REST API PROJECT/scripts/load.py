import sqlite3
import pandas as pd

def load_to_sqlite(df, db_path, table_name):
    conn = sqlite3.connect(db_path)

    df.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

# Load the transformed data and save to SQLite
df = pd.read_csv("../data/cleaned/south_sudan_clean.csv")
load_to_sqlite(df, "../database/worldbank.db", "development_indicators")

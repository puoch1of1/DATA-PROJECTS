import sqlite3
import pandas as pd
import os

def load_to_sqlite(df, db_path, table_name):
    conn = sqlite3.connect(db_path)

    df.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False
    )

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

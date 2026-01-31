import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\REST API PROJECT\database\worldbank.db")

df = pd.read_csv(r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\REST API PROJECT\data\cleaned\south_sudan_clean.csv")

df.to_sql(
    "development_indicators",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

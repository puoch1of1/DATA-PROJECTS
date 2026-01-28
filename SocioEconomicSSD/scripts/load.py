import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\database\south_sudan.db")

df = pd.read_csv(r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\cleaned\south_sudan_clean.csv")

df.to_sql(
    "socio_economic_indicators",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

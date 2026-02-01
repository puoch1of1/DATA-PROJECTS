import sqlite3
import pandas as pd

conn = sqlite3.connect("../database/worldbank.db")

result = pd.read_sql(
    "SELECT * FROM development_indicators LIMIT 5",
    conn 
)

print(result)
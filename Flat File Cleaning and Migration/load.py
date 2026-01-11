import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:password@localhost:5432/email_db"
)

df = pd.read_csv("clean_email_list.csv")

df.to_sql(
    "email_subscribers",
    engine,
    if_exists="append",
    index=False
)

print("Clean email list successfully loaded.")

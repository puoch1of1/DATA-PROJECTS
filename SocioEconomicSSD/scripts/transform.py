import pandas as pd

def clean_indicator(path, indicator):
    df = pd.read_csv(path)

    #to standardize column names
    df = df.rename(columns={
        "Country or Area": "country",
        "Year": "year",
        "Value": "value"
    })

    #keep only what matters
    df = df[["country", "year", "value"]]

    #clean data types 
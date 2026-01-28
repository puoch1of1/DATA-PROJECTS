import pandas as pd

def clean_indicator(path, indicator_name):
    df = pd.read_csv(path)

    # Standardize column names (adjust if needed)
    df = df.rename(columns={
        "Country or Area": "country",
        "Year": "year",
        "Year(s)": "year",
        "Value": "value"
    })

    # Keep only what matters
    df = df[["country", "year", "value"]]

    # Clean data types
    df["year"] = df["year"].astype(int)
    df["value"] = (
        df["value"]
        .astype(str)
        .str.replace(",", "")
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Add indicator column
    df["indicator"] = indicator_name

    # Drop missing values
    df = df.dropna()

    return df


population = clean_indicator(
    r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\raw\population.csv",
    "Population"
)

gdp = clean_indicator(
    r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\raw\gdp.csv",
    "GDP (current US$)"
)

life_expectancy = clean_indicator(
    r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\raw\life_expectancy.csv",
    "Life Expectancy at Birth"
)


combined = pd.concat(
    [population, gdp, life_expectancy],
    ignore_index=True
)

combined = combined.sort_values(
    ["indicator", "year"]
)

combined.to_csv(
    r"C:\Users\lomas\OneDrive\Desktop\DATA PROJECTS\DATA-PROJECTS\SocioEconomicSSD\cleaned\south_sudan_clean.csv",
    index=False
)

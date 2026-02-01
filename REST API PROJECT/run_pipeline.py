from datetime import datetime
import pandas as pd

from scripts.worldbank_client import WorldBankClient
from scripts.transform import transform_indicator
from scripts.load import load_to_sqlite

COUNTRY_CODE = "SSD"
DB_PATH = "database/worldbank.db"
TABLE_NAME = "development_indicators"

INDICATORS = {
    "SP.POP.TOTL": "Population",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.DYN.LE00.IN": "Life Expectancy at Birth"
}

def main():
    client = WorldBankClient()
    ingestion_time = datetime.utcnow().isoformat()

    all_data = []

    for code, name in INDICATORS.items():
        print(f"Fetching {name}...")
        raw_json = client.fetch_indicator(COUNTRY_CODE, code)

        df = transform_indicator(
            raw_json,
            name,
            ingestion_time
        )

        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    load_to_sqlite(
        final_df,
        DB_PATH,
        TABLE_NAME
    )

    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()



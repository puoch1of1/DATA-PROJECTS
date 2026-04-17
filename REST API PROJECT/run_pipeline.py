import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from scripts.worldbank_client import WorldBankClient
from scripts.transform import transform_indicator
from scripts.load import load_to_sqlite
from scripts.verify import verify_table

COUNTRY_CODE = "SSD"
DB_PATH = Path("database/worldbank.db")
TABLE_NAME = "development_indicators"

INDICATORS = {
    "SP.POP.TOTL": "Population",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.DYN.LE00.IN": "Life Expectancy at Birth"
}


def run_pipeline(
    country_code: str,
    db_path: Path,
    table_name: str,
    export_csv_path: Path | None,
    verify_after_load: bool,
):
    client = WorldBankClient()
    ingestion_time = datetime.now(timezone.utc).isoformat()

    all_data = []

    for code, name in INDICATORS.items():
        print(f"Fetching {name}...")
        raw_json = client.fetch_indicator(country_code, code)

        df = transform_indicator(
            raw_json,
            name,
            ingestion_time
        )
        if df.empty:
            print(f"No rows returned for {name}; continuing")
            continue

        all_data.append(df)

    if not all_data:
        raise RuntimeError("No indicator data was returned. Nothing to load.")

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["indicator", "year"]).reset_index(drop=True)

    load_to_sqlite(
        final_df,
        str(db_path),
        table_name
    )

    if verify_after_load:
        verification = verify_table(db_path, table_name)
        duplicate_count = len(verification["duplicate_keys"])
        if duplicate_count > 0:
            raise RuntimeError(
                f"Post-load verification found {duplicate_count} duplicate business keys."
            )

        print(
            "Verification summary: "
            f"rows={verification['row_count']}, "
            f"nulls={verification['null_summary']}"
        )

    if export_csv_path is not None:
        export_csv_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(export_csv_path, index=False)
        print(f"Saved transformed data to {export_csv_path}")

    print(f"Loaded {len(final_df)} rows into {table_name} at {db_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Run World Bank REST API ETL pipeline")
    parser.add_argument("--country", default=COUNTRY_CODE, help="Country code to fetch")
    parser.add_argument("--db", default=str(DB_PATH), help="SQLite database path")
    parser.add_argument("--table", default=TABLE_NAME, help="Destination table name")
    parser.add_argument(
        "--export-csv",
        default="data/cleaned/south_sudan_clean.csv",
        help="Optional cleaned CSV path; pass empty string to disable",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip post-load verification checks",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = project_root / db_path

    export_csv_path = None
    if args.export_csv:
        candidate = Path(args.export_csv)
        export_csv_path = candidate if candidate.is_absolute() else project_root / candidate

    run_pipeline(
        args.country,
        db_path,
        args.table,
        export_csv_path,
        verify_after_load=not args.skip_verify,
    )

    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()



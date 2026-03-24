from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = PROJECT_DIR / "raw_email_list.csv"
DEFAULT_OUTPUT = PROJECT_DIR / "clean_email_list.csv"
DEFAULT_REJECTIONS = PROJECT_DIR / "rejected_email_records.csv"

REQUIRED_COLUMNS = [
    "id",
    "full_name",
    "email",
    "signup_source",
    "signup_date",
    "country",
]

OUTPUT_COLUMNS = [
    "source_id",
    "full_name",
    "email",
    "signup_source",
    "signup_date",
    "country",
]

REJECTED_COLUMNS = OUTPUT_COLUMNS + ["rejection_reason"]

EMAIL_PATTERN = re.compile(
    r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$",
    re.IGNORECASE,
)

DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y")

COUNTRY_STANDARDIZATION = {
    "": "Unknown",
    "U.S.A": "United States",
    "U.S.A.": "United States",
    "UK": "United Kingdom",
    "U.K.": "United Kingdom",
    "USA": "United States",
    "UNKOWN": "Unknown",
    "UNKNOWN": "Unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a flat file of email subscribers and optionally load it into PostgreSQL."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the raw CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path where the cleaned CSV will be written.",
    )
    parser.add_argument(
        "--rejections",
        type=Path,
        default=DEFAULT_REJECTIONS,
        help="Path where rejected records will be written.",
    )
    parser.add_argument(
        "--load-to-db",
        action="store_true",
        help="Load the cleaned rows into the configured database.",
    )
    parser.add_argument(
        "--database-url",
        help="SQLAlchemy database URL. Overrides DATABASE_URL.",
    )
    parser.add_argument(
        "--table",
        default="email_subscribers",
        help="Destination table name when using --load-to-db.",
    )
    parser.add_argument(
        "--if-exists",
        default="append",
        choices=["append", "replace", "fail"],
        help="How to behave if the destination table already exists.",
    )
    return parser.parse_args()


def compact_whitespace(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def normalize_title(value: object, fallback: str = "Unknown") -> str:
    text = compact_whitespace(value)
    if not text:
        return fallback
    return text.title()


def normalize_country(value: object) -> str:
    text = compact_whitespace(value)
    if not text:
        return "Unknown"
    standardized = COUNTRY_STANDARDIZATION.get(text.upper())
    if standardized:
        return standardized
    return text.title()


def is_valid_email(value: object) -> bool:
    text = compact_whitespace(value).lower()
    return bool(text) and bool(EMAIL_PATTERN.fullmatch(text))


def format_dates(series: pd.Series) -> pd.Series:
    return series.dt.strftime("%Y-%m-%d").fillna("")


def parse_mixed_date(value: object) -> pd.Timestamp:
    text = compact_whitespace(value)
    if not text:
        return pd.NaT

    for date_format in DATE_FORMATS:
        try:
            return pd.Timestamp(datetime.strptime(text, date_format))
        except ValueError:
            continue

    return pd.to_datetime(text, errors="coerce")


def build_rejection_reason(dataframe: pd.DataFrame) -> pd.Series:
    invalid_email = ~dataframe["email"].apply(is_valid_email)
    missing_signup_date = dataframe["signup_date"].isna()
    missing_source_id = dataframe["source_id"].isna()

    reasons = pd.Series("", index=dataframe.index, dtype="object")
    reasons = reasons.mask(invalid_email, reasons + "invalid_email;")
    reasons = reasons.mask(missing_signup_date, reasons + "missing_signup_date;")
    reasons = reasons.mask(missing_source_id, reasons + "missing_source_id;")

    return reasons.str.rstrip(";").str.replace(";", ", ", regex=False)


def clean_subscribers(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in raw_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    dataframe = raw_df.copy()
    dataframe = dataframe.rename(columns={"id": "source_id"})

    dataframe["source_id"] = pd.to_numeric(dataframe["source_id"], errors="coerce").astype("Int64")
    dataframe["full_name"] = dataframe["full_name"].apply(normalize_title)
    dataframe["email"] = dataframe["email"].apply(lambda value: compact_whitespace(value).lower())
    dataframe["signup_source"] = dataframe["signup_source"].apply(normalize_title)
    dataframe["country"] = dataframe["country"].apply(normalize_country)
    dataframe["signup_date"] = dataframe["signup_date"].apply(parse_mixed_date)
    dataframe["rejection_reason"] = build_rejection_reason(dataframe)

    invalid_rows = dataframe[dataframe["rejection_reason"] != ""].copy()
    valid_rows = dataframe[dataframe["rejection_reason"] == ""].copy()

    valid_rows = valid_rows.sort_values(
        by=["email", "signup_date", "source_id"],
        kind="stable",
    )

    # Keep the earliest signup for each email and log later repeats as duplicates.
    duplicate_mask = valid_rows.duplicated(subset=["email"], keep="first")
    duplicate_rows = valid_rows[duplicate_mask].copy()
    duplicate_rows["rejection_reason"] = "duplicate_email"

    cleaned_rows = valid_rows[~duplicate_mask].copy()
    cleaned_rows = cleaned_rows.sort_values(by=["source_id"], kind="stable")

    cleaned_rows["signup_date"] = format_dates(cleaned_rows["signup_date"])
    invalid_rows["signup_date"] = format_dates(invalid_rows["signup_date"])
    duplicate_rows["signup_date"] = format_dates(duplicate_rows["signup_date"])

    rejected_rows = pd.concat(
        [invalid_rows[REJECTED_COLUMNS], duplicate_rows[REJECTED_COLUMNS]],
        ignore_index=True,
    )
    rejected_rows = rejected_rows.sort_values(by=["source_id"], kind="stable")

    return cleaned_rows[OUTPUT_COLUMNS], rejected_rows[REJECTED_COLUMNS]


def resolve_database_url(explicit_url: str | None) -> str | None:
    if explicit_url:
        return explicit_url

    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT", "5432")
    database = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")

    if all([host, database, user, password]):
        safe_user = quote_plus(user)
        safe_password = quote_plus(password)
        return f"postgresql://{safe_user}:{safe_password}@{host}:{port}/{database}"

    return None


def load_to_database(
    dataframe: pd.DataFrame,
    database_url: str,
    table_name: str,
    if_exists: str,
) -> None:
    if dataframe.empty:
        print("No valid records were available to load into the database.")
        return

    engine = create_engine(database_url)
    with engine.begin() as connection:
        dataframe.to_sql(
            table_name,
            connection,
            if_exists=if_exists,
            index=False,
            method="multi",
        )

    print(f"Loaded {len(dataframe)} cleaned records into '{table_name}'.")


def main() -> None:
    args = parse_args()

    raw_df = pd.read_csv(args.input)
    cleaned_df, rejected_df = clean_subscribers(raw_df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.rejections.parent.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_csv(args.output, index=False)
    rejected_df.to_csv(args.rejections, index=False)

    print(f"Raw records processed: {len(raw_df)}")
    print(f"Clean records exported: {len(cleaned_df)} -> {args.output}")
    print(f"Rejected records exported: {len(rejected_df)} -> {args.rejections}")

    if args.load_to_db:
        database_url = resolve_database_url(args.database_url)
        if not database_url:
            raise SystemExit(
                "Database connection details were not found. Pass --database-url or set DATABASE_URL."
            )
        load_to_database(cleaned_df, database_url, args.table, args.if_exists)


if __name__ == "__main__":
    main()

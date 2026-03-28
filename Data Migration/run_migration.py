import argparse
import logging
from pathlib import Path

import psycopg2

from config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_SOURCE_SCHEMA,
    DEFAULT_TARGET_SCHEMA,
    POSTGRES_CONN_STR,
)
from extract import extract_table
from load import LOAD_MODES, load_to_postgres
from validate import validate_row_counts


LOGGER = logging.getLogger("data_migration")
DEFAULT_DDL_PATH = Path(__file__).resolve().parent / "sql" / "postgres_schema.sql"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate a SQL Server table into PostgreSQL and validate row counts."
    )
    parser.add_argument("--table", default="customers", help="Table to migrate.")
    parser.add_argument(
        "--source-schema",
        default=DEFAULT_SOURCE_SCHEMA,
        help="SQL Server schema to read from.",
    )
    parser.add_argument(
        "--target-schema",
        default=DEFAULT_TARGET_SCHEMA,
        help="PostgreSQL schema to load into.",
    )
    parser.add_argument(
        "--load-mode",
        choices=sorted(LOAD_MODES),
        default="truncate",
        help="How to handle existing target rows before loading.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Number of rows per batch when writing to PostgreSQL.",
    )
    parser.add_argument(
        "--ddl-path",
        type=Path,
        default=DEFAULT_DDL_PATH,
        help="Optional PostgreSQL DDL file to execute before loading.",
    )
    parser.add_argument(
        "--skip-ddl",
        action="store_true",
        help="Skip executing the DDL file before loading.",
    )
    return parser.parse_args()


def ensure_postgres_schema(sql_path: Path) -> None:
    if not sql_path.exists():
        raise FileNotFoundError(f"DDL file not found: {sql_path}")

    ddl = sql_path.read_text(encoding="utf-8")
    conn = psycopg2.connect(POSTGRES_CONN_STR)
    try:
        with conn.cursor() as cursor:
            cursor.execute(ddl)
        conn.commit()
    finally:
        conn.close()


def run_migration(args: argparse.Namespace) -> int:
    LOGGER.info(
        "Starting migration for %s.%s -> %s.%s",
        args.source_schema,
        args.table,
        args.target_schema,
        args.table,
    )

    dataframe = extract_table(args.table, schema=args.source_schema)
    LOGGER.info("Extracted %s rows from SQL Server", len(dataframe))

    if not args.skip_ddl:
        ensure_postgres_schema(args.ddl_path)
        LOGGER.info("Executed PostgreSQL DDL from %s", args.ddl_path)

    loaded_rows = load_to_postgres(
        dataframe,
        args.table,
        schema=args.target_schema,
        load_mode=args.load_mode,
        chunk_size=args.chunk_size,
    )
    LOGGER.info("Loaded %s rows into PostgreSQL", loaded_rows)

    validation = validate_row_counts(
        args.table,
        source_schema=args.source_schema,
        target_schema=args.target_schema,
    )
    LOGGER.info("SQL Server rows: %s", validation.source_count)
    LOGGER.info("Postgres rows: %s", validation.target_count)

    if validation.matched:
        LOGGER.info("Row counts match")
        return 0

    LOGGER.error("Row counts do not match")
    return 1


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    return run_migration(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        LOGGER.error("Migration run failed: %s", exc)
        raise SystemExit(1) from exc

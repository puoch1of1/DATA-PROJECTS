# Data Migration Project

This project contains two small migration examples:

- `run_migration.py`: a SQL Server to PostgreSQL migration flow for table-based ETL.
- `Datappipline/`: a JSON API to MySQL example using `jsonplaceholder.typicode.com/posts`.

## Project Layout

```text
Data Migration/
|-- config.py
|-- db_utils.py
|-- extract.py
|-- load.py
|-- run_migration.py
|-- validate.py
|-- requirements-data-migration.txt
|-- sql/
|   |-- sqlserver_schema.sql
|   `-- postgres_schema.sql
`-- Datappipline/
    |-- pipeline.py
    |-- verify.py
    `-- JSONPlaceholder.json
```

## 1. SQL Server to PostgreSQL Migration

### Features

- CLI-based runner with configurable source and target schemas
- safer table and schema validation before dynamic SQL is built
- idempotent load modes: `append`, `truncate`, or `replace`
- chunked PostgreSQL writes for larger tables
- row-count validation after each run

### Install Dependencies

```powershell
pip install -r requirements-data-migration.txt
```

### Configure Environment Variables

```powershell
$env:SQLSERVER_CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=source_db;UID=sa;PWD=strong_password"
$env:POSTGRES_CONN_STR = "postgresql://postgres:strong_password@localhost:5432/target_db"
```

Optional defaults:

```powershell
$env:MIGRATION_SOURCE_SCHEMA = "dbo"
$env:MIGRATION_TARGET_SCHEMA = "public"
$env:MIGRATION_CHUNK_SIZE = "1000"
```

### Run the Migration

```powershell
python run_migration.py --table customers
```

Useful options:

```powershell
python run_migration.py --table customers --source-schema dbo --target-schema public --load-mode truncate
python run_migration.py --table customers --skip-ddl
python run_migration.py --table customers --ddl-path .\sql\postgres_schema.sql
```

### Supported Load Modes

- `truncate`: clears the target table first and preserves the existing schema
- `append`: adds rows to the existing table
- `replace`: drops and recreates the table through `pandas.to_sql`

## 2. API to MySQL Example

The `Datappipline` folder is a separate example that fetches posts from JSONPlaceholder and upserts them into a MySQL table named `posts`.

Optional environment variables:

```powershell
$env:PIPELINE_MYSQL_HOST = "localhost"
$env:PIPELINE_MYSQL_DATABASE = "pipeline"
$env:PIPELINE_MYSQL_USER = "root"
$env:PIPELINE_MYSQL_PASSWORD = "root"
```

Run it with:

```powershell
python .\Datappipline\pipeline.py
python .\Datappipline\verify.py
```

## Notes

- The default `sql/postgres_schema.sql` file currently creates a `customers` table.
- If you migrate a different table, either provide a matching DDL file or use `--skip-ddl` and create the target table yourself.
- The legacy `requirements.txt/README.MD` folder is left in place as project history; use `requirements-data-migration.txt` for installs.

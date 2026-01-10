# SQL Server to PostgreSQL Migration

## Overview
A simple Python pipeline to extract from SQL Server, load into PostgreSQL, validate counts, and visualize results.

## Prerequisites
- Windows ODBC Driver 17 for SQL Server installed
- Running SQL Server with `source_db` and table `dbo.customers`
- Running PostgreSQL `target_db`
- Python 3.10+

## Setup
1. Create a Python env and install deps:
```
pip install -r requirements_project.txt
```
2. Set connection strings (recommended via environment variables):
```
$env:SQLSERVER_CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=source_db;UID=sa;PWD=<password>"
$env:POSTGRES_CONN_STR  = "postgresql://postgres:<password>@localhost:5432/target_db"
```

## Usage
- Run end-to-end migration:
```
python "DATA-PROJECTS/Data Migration/run_migration.py"
```
- Validate counts only:
```
python "DATA-PROJECTS/Data Migration/validate.py"
```
- Visualize in notebook: open `notebooks/validation_visualization.ipynb` and run the cell.

## SQL Schemas
- SQL Server: `sql/sqlserver_schema.sql`
- PostgreSQL: `sql/postgres_schema.sql`

## Notes
- The code prints a warning if placeholder passwords are detected.
- If you see connection errors, verify drivers, credentials, and DB services.
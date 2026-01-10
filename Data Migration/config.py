import os

# Default connection strings (override via environment variables for production)
DEFAULT_SQLSERVER_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=source_db;"
    "UID=sa;"
    "PWD=your_password"
)

DEFAULT_POSTGRES_CONN_STR = (
    "postgresql://postgres:your_password@localhost:5432/target_db"
)

# Read from environment if available
SQLSERVER_CONN_STR = os.getenv("SQLSERVER_CONN_STR", DEFAULT_SQLSERVER_CONN_STR)
POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR", DEFAULT_POSTGRES_CONN_STR)

def require_config() -> None:
    """Warn if obvious placeholders are present in connection strings."""
    if "your_password" in SQLSERVER_CONN_STR or "your_password" in POSTGRES_CONN_STR:
        print(
            "Warning: Update DB credentials or set SQLSERVER_CONN_STR/POSTGRES_CONN_STR env vars."
        )

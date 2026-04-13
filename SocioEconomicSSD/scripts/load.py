"""
Load cleaned data into SQLite database.

This module handles persisting transformed data to a relational database
with proper schema and error handling.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Tuple


def get_project_paths():
    """
    Get absolute paths to project directories using relative paths from script location.
    Works regardless of where the script is executed from.
    """
    script_dir = Path(__file__).parent.parent
    return {
        'cleaned_csv': script_dir / 'cleaned' / 'south_sudan_clean.csv',
        'database': script_dir / 'database' / 'south_sudan.db',
        'database_dir': script_dir / 'database'
    }


def load_to_database(
    csv_path: str = None,
    db_path: str = None,
    table_name: str = "socio_economic_indicators",
    if_exists: str = "replace"
) -> Tuple[int, str]:
    """
    Load cleaned CSV data into SQLite database.
    
    Args:
        csv_path: Path to cleaned CSV file (uses default if None)
        db_path: Path to SQLite database (uses default if None)
        table_name: Name of table to create/populate (default: 'socio_economic_indicators')
        if_exists: Action if table exists - 'replace', 'append', 'fail'
        
    Returns:
        Tuple containing:
            - int: Number of rows loaded
            - str: Success message with details
            
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        sqlite3.Error: If database operation fails
    """
    paths = get_project_paths()
    
    # Use defaults or provided paths
    csv_file = Path(csv_path) if csv_path else paths['cleaned_csv']
    db_file = Path(db_path) if db_path else paths['database']
    
    # Validate CSV exists
    if not csv_file.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {csv_file}")
    
    # Ensure database directory exists
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read cleaned data
        print(f"  → Reading CSV: {csv_file.name}")
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            raise ValueError("CSV file is empty")
        
        # Connect to database
        print(f"  → Connecting to database: {db_file.name}")
        conn = sqlite3.connect(str(db_file))
        
        # Load to database
        print(f"  → Writing {len(df)} rows to table '{table_name}'...")
        df.to_sql(
            table_name,
            conn,
            if_exists=if_exists,
            index=False
        )
        
        # Verify load
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        conn.close()
        
        message = f"✓ Loaded {row_count} rows to {table_name} table"
        return row_count, message
        
    except Exception as e:
        raise Exception(f"Database load failed: {str(e)}")


def load_to_csv(
    df: pd.DataFrame,
    csv_path: str = None
) -> str:
    """
    Export cleaned dataframe to CSV file.
    
    Args:
        df: Dataframe to export
        csv_path: Path to CSV output file (uses default if None)
        
    Returns:
        str: Success message with file path
    """
    paths = get_project_paths()
    output_file = Path(csv_path) if csv_path else paths['cleaned_csv']
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_file, index=False)
    return f"✓ Exported {len(df)} rows to {output_file.name}"


def validate_database(db_path: str = None, table_name: str = "socio_economic_indicators") -> dict:
    """
    Validate database load and return summary statistics.
    
    Args:
        db_path: Path to SQLite database
        table_name: Table name to validate
        
    Returns:
        dict: Summary statistics (row_count, columns, data_types)
    """
    paths = get_project_paths()
    db_file = Path(db_path) if db_path else paths['database']
    
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")
    
    conn = sqlite3.connect(str(db_file))
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)
    
    # Get schema info
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema = cursor.fetchall()
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'table': table_name,
        'total_rows': total_rows,
        'columns': [col[1] for col in schema],
        'sample_data': df.to_dict('records')[:3]
    }


if __name__ == "__main__":
    # Example usage
    try:
        row_count, msg = load_to_database()
        print(f"\n[LOAD] {msg}")
        
        stats = validate_database()
        print(f"\n[VALIDATE] Database check:")
        print(f"  - Table: {stats['table']}")
        print(f"  - Total rows: {stats['total_rows']:,}")
        print(f"  - Columns: {', '.join(stats['columns'])}")
        
    except Exception as e:
        print(f"Error: {e}")

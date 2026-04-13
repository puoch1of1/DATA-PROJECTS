#!/usr/bin/env python
"""
SocioEconomic Indicators ETL Pipeline Orchestrator

Main entry point for the complete data pipeline:
  1. EXTRACT: Load raw CSV files
  2. TRANSFORM: Standardize and clean data
  3. LOAD: Persist to CSV and SQLite database
  4. VALIDATE: Verify data integrity

Usage:
    python run_pipeline.py [--options]

Examples:
    # Full pipeline
    python run_pipeline.py

    # CSV export only, skip database
    python run_pipeline.py --skip-db-load

    # Show detailed logs
    python run_pipeline.py --verbose

    # Full pipeline with custom output paths
    python run_pipeline.py --output-csv custom/data.csv --db-path custom/db.db
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path so imports work
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from extract import extract_indicators
from transform import transform
from load import load_to_database, load_to_csv, validate_database, get_project_paths


def main():
    """Main pipeline orchestration."""
    
    parser = argparse.ArgumentParser(
        description="South Sudan SocioEconomic Indicators ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                              # Full pipeline
  python run_pipeline.py --verbose                    # With detailed logs
  python run_pipeline.py --skip-db-load               # CSV only
  python run_pipeline.py --force                      # Overwrite existing outputs
        """
    )
    
    parser.add_argument(
        '--output-csv',
        type=str,
        default=None,
        help='Path to save cleaned CSV (default: cleaned/south_sudan_clean.csv)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default=None,
        help='Path to SQLite database (default: database/south_sudan.db)'
    )
    
    parser.add_argument(
        '--skip-db-load',
        action='store_true',
        help='Skip database loading, export to CSV only'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed processing logs'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing outputs without confirmation'
    )
    
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Run extraction stage only'
    )
    
    parser.add_argument(
        '--transform-only',
        action='store_true',
        help='Run transformation stage only (requires extracted data)'
    )
    
    parser.add_argument(
        '--load-only',
        action='store_true',
        help='Run loading stage only (requires transformed data)'
    )
    
    args = parser.parse_args()
    
    # Get paths
    paths = get_project_paths()
    output_csv = args.output_csv or str(paths['cleaned_csv'])
    db_path = args.db_path or str(paths['database'])
    
    try:
        print("=" * 70)
        print("SocioEconomic Indicators ETL Pipeline")
        print("=" * 70)
        
        # EXTRACT
        print("\n[STAGE 1/3] EXTRACT")
        print("-" * 70)
        indicators = extract_indicators()
        
        if args.extract_only:
            print("\n✓ Extraction complete. Stopping (--extract-only flag set)")
            return
        
        # TRANSFORM
        print("\n[STAGE 2/3] TRANSFORM")
        print("-" * 70)
        cleaned_data, transform_stats = transform(indicators)
        
        if args.transform_only:
            print("\n✓ Transformation complete. Stopping (--transform-only flag set)")
            return
        
        # LOAD - CSV Export
        print("\n[STAGE 3/3] LOAD")
        print("-" * 70)
        
        output_csv_path = Path(output_csv)
        if output_csv_path.exists() and not args.force:
            print(f"⚠ CSV file already exists: {output_csv}")
            response = input("Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print("✗ Skipped CSV export")
        else:
            msg = load_to_csv(cleaned_data, output_csv)
            print(f"  {msg}")
        
        # LOAD - Database
        if not args.skip_db_load:
            db_path_obj = Path(db_path)
            if db_path_obj.exists() and not args.force:
                print(f"⚠ Database already exists: {db_path}")
                response = input("Overwrite? (y/n): ").strip().lower()
                if response != 'y':
                    print("✗ Skipped database load")
            else:
                row_count, msg = load_to_database(output_csv, db_path)
                print(f"  {msg}")
        
        if args.load_only:
            print("\n✓ Load complete. Stopping (--load-only flag set)")
            return
        
        # VALIDATE
        print("\n[VALIDATION]")
        print("-" * 70)
        if not args.skip_db_load and Path(db_path).exists():
            stats = validate_database(db_path)
            print(f"  ✓ Database validation:")
            print(f"    - Table: {stats['table']}")
            print(f"    - Total rows: {stats['total_rows']:,}")
            print(f"    - Columns: {', '.join(stats['columns'])}")
            if stats['sample_data']:
                print(f"    - Sample record: {stats['sample_data'][0]}")
        
        # Summary
        print("\n" + "=" * 70)
        print("✓ PIPELINE COMPLETE")
        print("=" * 70)
        print(f"\nOutputs:")
        print(f"  • CSV: {output_csv}")
        if not args.skip_db_load:
            print(f"  • Database: {db_path}")
        print("\nNext steps:")
        print(f"  • Explore with: jupyter notebook analysis/trends.ipynb")
        print(f"  • Query database: sqlite3 {db_path}")
        print(f"  • Load in Python: pd.read_csv('{output_csv}')")
        print()
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ PIPELINE FAILED")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        if args.verbose:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

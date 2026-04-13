"""
Extract socioeconomic indicator CSV files.

This module loads raw CSV data files for South Sudan indicators:
- Population
- GDP (current US$)
- Life Expectancy at Birth
"""

import pandas as pd
import os
from pathlib import Path


def get_raw_data_dir():
    """
    Get the absolute path to the raw data directory.
    Works regardless of where the script is executed from.
    """
    script_dir = Path(__file__).parent.parent
    raw_dir = script_dir / "raw"
    return raw_dir


def extract_indicators():
    """
    Extract socioeconomic indicator data from raw CSV files.
    
    Returns:
        dict: Dictionary with indicator names as keys and pandas DataFrames as values.
              Keys: 'population', 'gdp', 'life_expectancy'
              
    Raises:
        FileNotFoundError: If any required CSV file is missing from raw/ directory.
        ValueError: If CSV files are missing required columns.
    """
    raw_dir = get_raw_data_dir()
    
    # Define expected files
    files = {
        'population': 'population.csv',
        'gdp': 'gdp.csv',
        'life_expectancy': 'life_expectancy.csv'
    }
    
    indicators = {}
    
    for key, filename in files.items():
        filepath = raw_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Raw data file not found: {filepath}\n"
                f"Expected file: {filename} in {raw_dir}"
            )
        
        try:
            df = pd.read_csv(filepath)
            indicators[key] = df
            print(f"✓ Extracted {key}: {len(df)} rows from {filename}")
        except Exception as e:
            raise ValueError(
                f"Error reading {filename}: {str(e)}\n"
                f"Ensure file is valid CSV format."
            )
    
    return indicators


if __name__ == "__main__":
    # Example usage
    try:
        data = extract_indicators()
        for indicator, df in data.items():
            print(f"\n{indicator.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Preview:\n{df.head(2)}")
    except Exception as e:
        print(f"Error: {e}")

"""
Transform and clean socioeconomic indicator data.

This module standardizes columns, data types, and handles missing values
for consistency across all indicators.
"""

import pandas as pd
from typing import Dict, Tuple
from extract import extract_indicators


def clean_indicator(df: pd.DataFrame, indicator_name: str) -> pd.DataFrame:
    """
    Clean and standardize a single indicator dataframe.
    
    Args:
        df: Raw DataFrame with indicator data
        indicator_name: Name of the indicator (e.g., "Population", "GDP (current US$)")
        
    Returns:
        pd.DataFrame: Cleaned dataframe with columns [country, year, value, indicator]
    """
    df = df.copy()
    
    # Standardize column names (flexible to handle variations)
    df = df.rename(columns={
        "Country or Area": "country",
        "Country": "country",
        "Year": "year",
        "Year(s)": "year",
        "Value": "value",
    })
    
    # Validate required columns exist
    required_cols = ["country", "year", "value"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}\nAvailable: {list(df.columns)}")
    
    # Keep only required columns
    df = df[["country", "year", "value"]]
    
    # Clean data types
    try:
        df["year"] = df["year"].astype(int)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Could not convert 'year' to integer: {e}")
    
    # Clean value column: remove commas, convert to float
    df["value"] = (
        df["value"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Add indicator column
    df["indicator"] = indicator_name
    
    # Drop rows with missing values
    initial_rows = len(df)
    df = df.dropna()
    dropped_rows = initial_rows - len(df)
    
    if dropped_rows > 0:
        print(f"  ⚠ {indicator_name}: Dropped {dropped_rows} rows with missing values")
    
    # Reorder columns for consistency
    df = df[["country", "year", "indicator", "value"]]
    
    return df


def transform(indicators_dict: Dict) -> Tuple[pd.DataFrame, dict]:
    """
    Transform raw indicator data into a unified, clean dataset.
    
    Args:
        indicators_dict: Dictionary with indicator DataFrames from extract_indicators()
        
    Returns:
        Tuple containing:
            - pd.DataFrame: Combined cleaned dataframe with all indicators
            - dict: Transformation statistics (row counts, indicators processed)
    """
    print("\n[TRANSFORM] Starting data transformation...")
    
    stats = {
        'indicators_processed': 0,
        'total_rows_extracted': 0,
        'total_rows_cleaned': 0,
        'rows_removed': 0
    }
    
    indicator_mapping = {
        'population': 'Population',
        'gdp': 'GDP (current US$)',
        'life_expectancy': 'Life Expectancy at Birth'
    }
    
    cleaned_dfs = []
    
    for key, df_raw in indicators_dict.items():
        indicator_name = indicator_mapping.get(key, key)
        print(f"  → Cleaning {indicator_name}... ({len(df_raw)} rows)")
        
        df_cleaned = clean_indicator(df_raw, indicator_name)
        cleaned_dfs.append(df_cleaned)
        
        stats['indicators_processed'] += 1
        stats['total_rows_extracted'] += len(df_raw)
        stats['total_rows_cleaned'] += len(df_cleaned)
    
    stats['rows_removed'] = stats['total_rows_extracted'] - stats['total_rows_cleaned']
    
    # Combine all indicators into single dataframe
    combined_df = pd.concat(cleaned_dfs, ignore_index=True)
    combined_df = combined_df.sort_values(['country', 'indicator', 'year']).reset_index(drop=True)
    
    print(f"\n[TRANSFORM] ✓ Complete")
    print(f"  - Rows processed: {stats['total_rows_extracted']:,}")
    print(f"  - Rows kept: {stats['total_rows_cleaned']:,}")
    print(f"  - Rows dropped: {stats['rows_removed']:,}")
    print(f"  - Indicators: {stats['indicators_processed']}")
    
    return combined_df, stats


if __name__ == "__main__":
    # Example usage
    try:
        indicators = extract_indicators()
        cleaned_data, transform_stats = transform(indicators)
        print(f"\nFinal dataset shape: {cleaned_data.shape}")
        print(f"Unique indicators: {cleaned_data['indicator'].unique()}")
        print(f"\nFirst 5 rows:\n{cleaned_data.head()}")
    except Exception as e:
        print(f"Error: {e}")

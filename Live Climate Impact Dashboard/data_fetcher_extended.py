"""Extended data fetchers for historical climate records."""

from __future__ import annotations

from datetime import date, timedelta
import json
from io import StringIO
from typing import Optional

import pandas as pd
import requests

# Open-Meteo API for historical weather data (free, no auth required)
OPEN_METEO_HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_open_meteo_historical(
    lat: float,
    lon: float,
    start: date,
    end: date,
) -> pd.DataFrame:
    """Fetch historical weather data from Open-Meteo API.
    
    Provides: temperature, precipitation, wind speed, pressure, etc.
    Free/open-source, no authentication required.
    
    Args:
        lat: Latitude
        lon: Longitude
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with historical daily weather data
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,precipitation,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "timezone": "UTC",
        }
        
        response = requests.get(OPEN_METEO_HISTORICAL_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "daily" not in data:
            return pd.DataFrame()
        
        daily = data["daily"]
        df = pd.DataFrame({
            "date": pd.to_datetime(daily["time"]),
            "temp_max_c": daily["temperature_2m_max"],
            "temp_min_c": daily["temperature_2m_min"],
            "temp_mean_c": daily["temperature_2m_mean"],
            "precip_mm": daily["precipitation_sum"],
            "wind_speed_kmh": daily["wind_speed_10m_max"],
        })
        
        return df.sort_values("date").reset_index(drop=True)
        
    except Exception as e:
        print(f"Open-Meteo fetch error: {e}")
        return pd.DataFrame()


def fetch_noaa_cdc_precipitation(
    station_id: str,
    start: date,
    end: date,
    token: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch historical daily precipitation from NOAA NCEI.
    
    Args:
        station_id: NOAA station ID
        start: Start date
        end: End date
        token: Optional NOAA API token
        
    Returns:
        DataFrame with daily precipitation totals
    """
    try:
        params = {
            "dataset": "daily-summaries",
            "stations": station_id,
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
            "dataTypes": "PRCP",
            "format": "json",
            "units": "metric",
        }
        
        headers = {}
        if token:
            headers["token"] = token
        
        url = "https://www.ncei.noaa.gov/access/services/data/v1"
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        records = response.json()
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df.get("DATE", df.get("date")))
        df["precip_mm"] = pd.to_numeric(df.get("PRCP", 0), errors="coerce")
        
        return df[["date", "precip_mm"]].sort_values("date").reset_index(drop=True)
        
    except Exception as e:
        print(f"NOAA CDC precipitation fetch error: {e}")
        return pd.DataFrame()


def generate_synthetic_rainfall_data(
    start: date,
    end: date,
    location_name: str = "Location",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic rainfall data for demonstration/testing.
    
    Creates realistic seasonal rainfall patterns with noise.
    
    Args:
        start: Start date
        end: End date
        location_name: Name for reference
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with daily synthetic rainfall
    """
    import numpy as np
    
    np.random.seed(seed)
    
    days = (end - start).days
    dates = pd.date_range(start=start, end=end, freq="D")
    
    # Create seasonal pattern (higher rainfall in certain months)
    day_of_year = np.array([d.dayofyear for d in dates])
    
    # Bimodal distribution for tropical/subtropical regions
    seasonal = (
        5 * np.sin(2 * np.pi * day_of_year / 365) +
        3 * np.sin(4 * np.pi * day_of_year / 365)
    )
    
    # Add random variation and ensure non-negative
    noise = np.random.normal(0, 2, len(dates))
    rainfall = np.maximum(seasonal + noise, 0)
    
    # Rain happens on ~40% of days
    rain_mask = np.random.random(len(dates)) < 0.4
    rainfall = np.where(rain_mask, rainfall * 3, rainfall * 0.3)
    
    df = pd.DataFrame({
        "date": dates,
        "precip_mm": rainfall.clip(0),
        "location": location_name,
    })
    
    return df


def generate_synthetic_aqi_data(
    start: date,
    end: date,
    location_name: str = "Location",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic air quality index data for demonstration.
    
    Creates realistic seasonal AQI patterns.
    
    Args:
        start: Start date
        end: End date
        location_name: Name for reference
        seed: Random seed
        
    Returns:
        DataFrame with daily synthetic AQI values (0-500 scale)
    """
    import numpy as np
    
    np.random.seed(seed)
    
    dates = pd.date_range(start=start, end=end, freq="D")
    day_of_year = np.array([d.dayofyear for d in dates])
    
    # Higher AQI in winter (seasonal pattern)
    seasonal = 50 + 80 * np.cos(2 * np.pi * day_of_year / 365)
    
    # Add noise and day-of-week effects
    noise = np.random.normal(0, 15, len(dates))
    dow_effect = np.array([10 if d.dayofweek < 5 else -5 for d in dates])  # Higher on weekdays
    
    aqi = seasonal + noise + dow_effect
    aqi = np.clip(aqi, 0, 500)  # AQI typically 0-500
    
    df = pd.DataFrame({
        "date": dates,
        "aqi": aqi,
        "location": location_name,
    })
    
    return df


def merge_forecasting_data(
    temp_df: pd.DataFrame,
    precip_df: pd.DataFrame,
    on: str = "date",
) -> pd.DataFrame:
    """Merge temperature and precipitation data.
    
    Args:
        temp_df: Temperature DataFrame
        precip_df: Precipitation DataFrame
        on: Join key (usually 'date')
        
    Returns:
        Merged DataFrame
    """
    if temp_df.empty or precip_df.empty:
        return pd.DataFrame()
    
    return pd.merge(temp_df, precip_df, on=on, how="inner")

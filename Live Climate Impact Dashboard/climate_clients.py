from __future__ import annotations

from datetime import date
from io import StringIO
import os
from typing import Optional

import pandas as pd
import requests

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NOAA_DAILY_SUMMARIES_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
NOAA_CO2_WEEKLY_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_weekly_mlo.csv"


def _iso_date(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def _compact_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def fetch_nasa_daily_temperature(lat: float, lon: float, start: date, end: date) -> pd.DataFrame:
    """Fetch daily 2m air temperature (T2M) from NASA POWER."""
    params = {
        "parameters": "T2M",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": _compact_date(start),
        "end": _compact_date(end),
        "format": "JSON",
    }

    response = requests.get(NASA_POWER_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    daily = payload.get("properties", {}).get("parameter", {}).get("T2M", {})
    if not daily:
        return pd.DataFrame(columns=["date", "temp_c"])

    frame = pd.DataFrame(
        [{"date": pd.to_datetime(k, format="%Y%m%d"), "temp_c": float(v)} for k, v in daily.items()]
    )
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame


def fetch_noaa_daily_temperature(
    station_id: str,
    start: date,
    end: date,
    token: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch daily temperature summary from NOAA NCEI Daily Summaries API."""
    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": _iso_date(start),
        "endDate": _iso_date(end),
        "dataTypes": "TAVG,TMAX,TMIN",
        "format": "json",
        "units": "metric",
    }

    headers = {}
    if token:
        headers["token"] = token

    response = requests.get(NOAA_DAILY_SUMMARIES_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    records = response.json()

    if not records:
        return pd.DataFrame(columns=["date", "tavg_c", "tmax_c", "tmin_c"])

    frame = pd.DataFrame(records)
    date_col = "DATE" if "DATE" in frame.columns else "date"
    frame["date"] = pd.to_datetime(frame[date_col], errors="coerce")

    for out_col, in_col in [("tavg_c", "TAVG"), ("tmax_c", "TMAX"), ("tmin_c", "TMIN")]:
        if in_col in frame.columns:
            frame[out_col] = pd.to_numeric(frame[in_col], errors="coerce")
        else:
            frame[out_col] = pd.NA

    frame = frame[["date", "tavg_c", "tmax_c", "tmin_c"]].dropna(subset=["date"])
    frame = frame.sort_values("date").reset_index(drop=True)
    return frame


def fetch_noaa_weekly_co2() -> pd.DataFrame:
    """Fetch weekly atmospheric CO2 concentration from NOAA GML (Mauna Loa)."""
    response = requests.get(NOAA_CO2_WEEKLY_URL, timeout=30)
    response.raise_for_status()

    raw = pd.read_csv(StringIO(response.text), comment="#", header=None)

    # Expected columns in NOAA file:
    # year, month, day, decimal_date, average, interpolated, trend, days, ...
    min_expected = 8
    if raw.shape[1] < min_expected:
        return pd.DataFrame(columns=["date", "co2_ppm", "trend_ppm"])

    col_names = [
        "year",
        "month",
        "day",
        "decimal_date",
        "co2_ppm",
        "interpolated_ppm",
        "trend_ppm",
        "days",
    ]
    if raw.shape[1] > len(col_names):
        col_names.extend([f"extra_{i}" for i in range(raw.shape[1] - len(col_names))])

    raw.columns = col_names[: raw.shape[1]]

    frame = raw.copy()
    frame["co2_ppm"] = pd.to_numeric(frame["co2_ppm"], errors="coerce")
    frame["trend_ppm"] = pd.to_numeric(frame["trend_ppm"], errors="coerce")
    frame["date"] = pd.to_datetime(frame[["year", "month", "day"]], errors="coerce")

    # NOAA uses negative placeholders for missing values.
    frame = frame[(frame["co2_ppm"] > 0) & frame["date"].notna()]
    frame = frame[["date", "co2_ppm", "trend_ppm"]].sort_values("date").reset_index(drop=True)
    return frame


def get_noaa_token() -> Optional[str]:
    token = os.getenv("NOAA_TOKEN", "").strip()
    return token or None

from __future__ import annotations

from datetime import date, timedelta
import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from climate_clients import (
    fetch_nasa_daily_temperature,
    fetch_noaa_daily_temperature,
    fetch_noaa_weekly_co2,
    get_noaa_token,
)
from data_fetcher_extended import (
    fetch_open_meteo_historical,
    generate_synthetic_rainfall_data,
    generate_synthetic_aqi_data,
)
from forecasting import (
    prepare_timeseries,
    forecast_arima,
    forecast_sarima,
    forecast_prophet,
    generate_future_dates,
    create_forecast_dataframe,
)

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Live Climate Impact Dashboard",
    page_icon="🌎",
    layout="wide",
)

CITY_PRESETS = {
    "New York, USA": {"lat": 40.7128, "lon": -74.0060, "station": "USW00094728"},
    "Nairobi, Kenya": {"lat": -1.2864, "lon": 36.8172, "station": "HKJK"},
    "Juba, South Sudan": {"lat": 4.8594, "lon": 31.5713, "station": "HSSJ"},
    "London, UK": {"lat": 51.5072, "lon": -0.1276, "station": "EGLL"},
}


def _safe_mean(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return None
    return float(clean.mean())


def plot_forecast_with_actuals(
    historical_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    title: str,
    y_label: str,
    x_col: str = "date",
    y_col: str = "temp_c",
    forecast_col: str = "forecast",
) -> go.Figure:
    """Create a plot with historical data and forecast with confidence intervals."""
    fig = go.Figure()
    
    # Historical data
    if not historical_df.empty:
        fig.add_trace(
            go.Scatter(
                x=historical_df[x_col],
                y=historical_df[y_col],
                mode="lines",
                name="Historical",
                line={"color": "#1f77b4", "width": 2},
            )
        )
    
    # Forecast
    if not forecast_df.empty:
        # Confidence interval as filled area
        fig.add_trace(
            go.Scatter(
                x=list(forecast_df[x_col]) + list(forecast_df[x_col][::-1]),
                y=list(forecast_df["upper_ci"]) + list(forecast_df["lower_ci"][::-1]),
                fill="toself",
                fillcolor="rgba(255, 127, 14, 0.2)",
                line={"color": "rgba(255, 127, 14, 0)"},
                name="95% Confidence Interval",
                hoverinfo="skip",
            )
        )
        
        # Forecast line
        fig.add_trace(
            go.Scatter(
                x=forecast_df[x_col],
                y=forecast_df[forecast_col],
                mode="lines",
                name="Forecast",
                line={"color": "#ff7f0e", "width": 2, "dash": "dash"},
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        height=420,
        hovermode="x unified",
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        legend={"orientation": "h", "y": 1.05, "x": 0},
    )
    
    return fig


@st.cache_data(ttl=1800)
def load_nasa_temperature(lat: float, lon: float, start: date, end: date) -> pd.DataFrame:
    return fetch_nasa_daily_temperature(lat=lat, lon=lon, start=start, end=end)


@st.cache_data(ttl=1800)
def load_noaa_temperature(station: str, start: date, end: date, token: str | None) -> pd.DataFrame:
    return fetch_noaa_daily_temperature(station_id=station, start=start, end=end, token=token)


@st.cache_data(ttl=1800)
def load_noaa_co2() -> pd.DataFrame:
    return fetch_noaa_weekly_co2()


st.title("Live Climate Impact Dashboard")
st.caption("NASA POWER + NOAA data for temperature trends and atmospheric air-quality pressure")

with st.sidebar:
    st.header("Controls")
    preset = st.selectbox("Location", options=list(CITY_PRESETS.keys()) + ["Custom"])

    if preset == "Custom":
        lat = st.number_input("Latitude", value=4.8594, format="%.4f")
        lon = st.number_input("Longitude", value=31.5713, format="%.4f")
        station = st.text_input("NOAA Station ID", value="HSSJ")
    else:
        lat = CITY_PRESETS[preset]["lat"]
        lon = CITY_PRESETS[preset]["lon"]
        station = CITY_PRESETS[preset]["station"]

    today = date.today()
    default_start = today - timedelta(days=180)

    start = st.date_input("Start date", value=default_start)
    end = st.date_input("End date", value=today)

    refresh = st.button("Refresh Data")
    if refresh:
        st.cache_data.clear()

if start > end:
    st.error("Start date cannot be later than end date.")
    st.stop()

noaa_token = get_noaa_token()

left, right = st.columns(2)

with left:
    st.subheader("Temperature Rise Tracker")
    try:
        nasa_df = load_nasa_temperature(lat=float(lat), lon=float(lon), start=start, end=end)
    except Exception as exc:
        st.error(f"NASA data request failed: {exc}")
        nasa_df = pd.DataFrame(columns=["date", "temp_c"])

    try:
        noaa_df = load_noaa_temperature(station=str(station), start=start, end=end, token=noaa_token)
    except Exception as exc:
        st.warning(f"NOAA station data unavailable for {station}: {exc}")
        noaa_df = pd.DataFrame(columns=["date", "tavg_c", "tmax_c", "tmin_c"])

    nasa_mean = _safe_mean(nasa_df.get("temp_c", pd.Series(dtype=float)))
    noaa_mean = _safe_mean(noaa_df.get("tavg_c", pd.Series(dtype=float)))

    col1, col2, col3 = st.columns(3)
    col1.metric("NASA Avg Temp (C)", f"{nasa_mean:.2f}" if nasa_mean is not None else "N/A")
    col2.metric("NOAA Avg Temp (C)", f"{noaa_mean:.2f}" if noaa_mean is not None else "N/A")

    if nasa_mean is not None and noaa_mean is not None:
        col3.metric("NASA - NOAA (C)", f"{(nasa_mean - noaa_mean):+.2f}")
    else:
        col3.metric("NASA - NOAA (C)", "N/A")

    fig_temp = go.Figure()
    if not nasa_df.empty:
        fig_temp.add_trace(
            go.Scatter(
                x=nasa_df["date"],
                y=nasa_df["temp_c"],
                mode="lines",
                name="NASA T2M",
                line={"width": 2},
            )
        )

    if not noaa_df.empty:
        fig_temp.add_trace(
            go.Scatter(
                x=noaa_df["date"],
                y=noaa_df["tavg_c"],
                mode="lines",
                name="NOAA TAVG",
                line={"width": 2},
            )
        )

    fig_temp.update_layout(
        xaxis_title="Date",
        yaxis_title="Temperature (C)",
        height=420,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        legend={"orientation": "h", "y": 1.05, "x": 0},
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with right:
    st.subheader("Air Quality Pressure (NOAA Atmospheric CO2)")
    st.caption("Weekly CO2 concentration from NOAA GML (Mauna Loa), used as a global air-quality pressure proxy")

    try:
        co2_df = load_noaa_co2()
    except Exception as exc:
        st.error(f"NOAA CO2 request failed: {exc}")
        co2_df = pd.DataFrame(columns=["date", "co2_ppm", "trend_ppm"])

    if co2_df.empty:
        st.info("No CO2 data returned.")
    else:
        latest = co2_df.iloc[-1]
        one_year_ago_cutoff = latest["date"] - timedelta(days=365)
        prev_candidates = co2_df[co2_df["date"] <= one_year_ago_cutoff]
        yoy_change = None
        if not prev_candidates.empty:
            yoy_change = float(latest["co2_ppm"] - prev_candidates.iloc[-1]["co2_ppm"])

        m1, m2 = st.columns(2)
        m1.metric("Latest CO2 (ppm)", f"{latest['co2_ppm']:.2f}")
        m2.metric("1Y Change (ppm)", f"{yoy_change:+.2f}" if yoy_change is not None else "N/A")

        fig_co2 = go.Figure()
        fig_co2.add_trace(
            go.Scatter(
                x=co2_df["date"],
                y=co2_df["co2_ppm"],
                mode="lines",
                name="CO2 (weekly)",
                line={"width": 1.5},
            )
        )
        if "trend_ppm" in co2_df.columns and co2_df["trend_ppm"].notna().any():
            fig_co2.add_trace(
                go.Scatter(
                    x=co2_df["date"],
                    y=co2_df["trend_ppm"],
                    mode="lines",
                    name="Trend",
                    line={"width": 3},
                )
            )

        fig_co2.update_layout(
            xaxis_title="Date",
            yaxis_title="CO2 (ppm)",
            height=420,
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            legend={"orientation": "h", "y": 1.05, "x": 0},
        )
        st.plotly_chart(fig_co2, use_container_width=True)

st.divider()
st.markdown(
    "\n".join(
        [
            "**Data Sources**",
            "- NASA POWER Daily API (`T2M`)",
            "- NOAA NCEI Daily Summaries API (`TAVG`, `TMAX`, `TMIN`)",
            "- NOAA GML weekly atmospheric CO2 records",
        ]
    )
)

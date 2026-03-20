from __future__ import annotations

from datetime import date, timedelta
import warnings

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


@st.cache_data(ttl=1800, show_spinner=False)
def load_nasa_temperature(lat: float, lon: float, start: date, end: date) -> pd.DataFrame:
    return fetch_nasa_daily_temperature(lat=lat, lon=lon, start=start, end=end)


@st.cache_data(ttl=1800, show_spinner=False)
def load_noaa_temperature(station_id: str, start: date, end: date, token: str | None) -> pd.DataFrame:
    return fetch_noaa_daily_temperature(station_id=station_id, start=start, end=end, token=token)


@st.cache_data(ttl=3600, show_spinner=False)
def load_weekly_co2() -> pd.DataFrame:
    return fetch_noaa_weekly_co2()


@st.cache_data(ttl=1800, show_spinner=False)
def load_open_meteo(lat: float, lon: float, start: date, end: date) -> pd.DataFrame:
    return fetch_open_meteo_historical(lat=lat, lon=lon, start=start, end=end)


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


st.title("Live Climate Impact Dashboard with Forecasting")
st.caption("🌍 NASA POWER + NOAA data + AI-powered climate predictions (ARIMA, SARIMA, Prophet)")

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

    forecast_days = st.number_input("Forecast horizon (days)", value=30, min_value=7, max_value=90)
    
    forecast_models = st.multiselect(
        "Forecast models",
        options=["ARIMA", "SARIMA", "Prophet"],
        default=["ARIMA", "Prophet"],
    )

    refresh = st.button("Refresh Data")
    if refresh:
        st.cache_data.clear()

if start > end:
    st.error("Start date cannot be later than end date.")
    st.stop()

if not (-90 <= float(lat) <= 90) or not (-180 <= float(lon) <= 180):
    st.error("Latitude must be in [-90, 90] and longitude must be in [-180, 180].")
    st.stop()

station = str(station).strip().upper()

noaa_token = get_noaa_token()

# Load historical data
with st.spinner("Loading historical climate data..."):
    try:
        nasa_df = load_nasa_temperature(lat=float(lat), lon=float(lon), start=start, end=end)
    except Exception as exc:
        st.warning(f"NASA data request failed: {exc}")
        nasa_df = pd.DataFrame(columns=["date", "temp_c"])

    try:
        noaa_df = load_noaa_temperature(station_id=station, start=start, end=end, token=noaa_token)
    except Exception as exc:
        st.warning(f"NOAA station data unavailable for {station}: {exc}")
        noaa_df = pd.DataFrame(columns=["date", "tavg_c", "tmax_c", "tmin_c"])

    try:
        co2_df = load_weekly_co2()
    except Exception as exc:
        st.warning(f"NOAA CO2 request failed: {exc}")
        co2_df = pd.DataFrame(columns=["date", "co2_ppm", "trend_ppm"])
    
    try:
        rainfall_df = load_open_meteo(
            lat=float(lat), lon=float(lon), start=start, end=end
        )
        if rainfall_df.empty:
            rainfall_df = generate_synthetic_rainfall_data(start, end, location_name=preset)
    except Exception as exc:
        st.info(f"Using synthetic rainfall data: {exc}")
        rainfall_df = generate_synthetic_rainfall_data(start, end, location_name=preset)
    
    aqi_df = generate_synthetic_aqi_data(start, end, location_name=preset)

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Historical Overview",
    "🌡️ Temperature Forecast",
    "💧 Rainfall Trends",
    "💨 Air Quality Index",
    "📈 CO2 Trends",
])

with tab1:
    st.subheader("Historical Climate Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Temperature Summary**")
        nasa_mean = _safe_mean(nasa_df.get("temp_c", pd.Series(dtype=float)))
        noaa_mean = _safe_mean(noaa_df.get("tavg_c", pd.Series(dtype=float)))
        st.metric("NASA Avg Temp (C)", f"{nasa_mean:.2f}" if nasa_mean is not None else "N/A")
        st.metric("NOAA Avg Temp (C)", f"{noaa_mean:.2f}" if noaa_mean is not None else "N/A")
    
    with col2:
        st.write("**Precipitation**")
        if not rainfall_df.empty:
            total_precip = rainfall_df["precip_mm"].sum()
            avg_precip = rainfall_df["precip_mm"].mean()
            st.metric("Total Rainfall (mm)", f"{total_precip:.1f}")
            st.metric("Avg Daily (mm)", f"{avg_precip:.2f}")
    
    with col3:
        st.write("**Latest CO2**")
        if not co2_df.empty:
            latest_co2 = co2_df.iloc[-1]["co2_ppm"]
            st.metric("CO2 Level (ppm)", f"{latest_co2:.2f}")
    
    left, right = st.columns(2)
    
    with left:
        st.subheader("Temperature Trends")
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
            height=400,
            hovermode="x unified",
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with right:
        st.subheader("Precipitation Pattern")
        if not rainfall_df.empty:
            fig_rain = go.Figure()
            fig_rain.add_trace(
                go.Bar(
                    x=rainfall_df["date"],
                    y=rainfall_df["precip_mm"],
                    name="Rainfall",
                    marker={"color": "lightblue"},
                )
            )
            fig_rain.update_layout(
                xaxis_title="Date",
                yaxis_title="Precipitation (mm)",
                height=400,
                showlegend=False,
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
            )
            st.plotly_chart(fig_rain, use_container_width=True)

with tab2:
    st.subheader("Temperature Anomaly Forecasting")
    selected_models_caption = ", ".join(forecast_models) if forecast_models else "no selected models"
    st.caption(f"Forecasting {forecast_days} days ahead using {selected_models_caption}")
    
    if nasa_df.empty:
        st.warning("Insufficient historical temperature data for forecasting.")
    else:
        # Prepare data
        ts_df = prepare_timeseries(nasa_df, "temp_c", "date")
        
        if len(ts_df) < 7:
            st.error("Need at least 7 days of historical data to forecast.")
        else:
            if not forecast_models:
                st.info("Select at least one forecast model from the sidebar.")
            else:
                future_dates = generate_future_dates(ts_df["date"].iloc[-1], forecast_days, freq="D")
                timeseries = ts_df["temp_c"]
                
                forecast_results = {}
                metrics_data = []
                
                if "ARIMA" in forecast_models:
                    with st.spinner("Running ARIMA..."):
                        result = forecast_arima(timeseries, periods=forecast_days, order=(1, 1, 1))
                        forecast_results["ARIMA"] = create_forecast_dataframe(result, future_dates, "ARIMA")
                        if result["success"]:
                            metrics_data.append({
                                "Model": "ARIMA",
                                "MAE": f"{result['mae']:.3f}" if result["mae"] is not None else "N/A",
                                "RMSE": f"{result['rmse']:.3f}" if result["rmse"] is not None else "N/A",
                            })
                        else:
                            st.warning(f"ARIMA failed: {result.get('error', 'Unknown error')}")
                
                if "SARIMA" in forecast_models:
                    with st.spinner("Running SARIMA..."):
                        result = forecast_sarima(
                            timeseries,
                            periods=forecast_days,
                            order=(1, 1, 1),
                            seasonal_order=(1, 1, 1, 7),
                        )
                        forecast_results["SARIMA"] = create_forecast_dataframe(result, future_dates, "SARIMA")
                        if result["success"]:
                            metrics_data.append({
                                "Model": "SARIMA",
                                "MAE": f"{result['mae']:.3f}" if result["mae"] is not None else "N/A",
                                "RMSE": f"{result['rmse']:.3f}" if result["rmse"] is not None else "N/A",
                            })
                        else:
                            st.warning(f"SARIMA failed: {result.get('error', 'Unknown error')}")
                
                if "Prophet" in forecast_models:
                    with st.spinner("Running Facebook Prophet..."):
                        prophet_input = ts_df[["date", "temp_c"]].copy()
                        result = forecast_prophet(prophet_input, periods=forecast_days, freq="D")
                        forecast_results["Prophet"] = create_forecast_dataframe(result, future_dates, "Prophet")
                        if result["success"]:
                            metrics_data.append({
                                "Model": "Prophet",
                                "MAE": "Auto-tuned",
                                "RMSE": "Auto-tuned",
                            })
                        else:
                            st.warning(f"Prophet failed: {result.get('error', 'Unknown error')}")
                
                # Model comparison metrics
                if metrics_data:
                    st.write("**Model Performance Metrics (Training Data)**")
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                # Plot forecasts
                left_col, right_col = st.columns(2)
                
                for idx, (model_name, forecast_df) in enumerate(forecast_results.items()):
                    if not forecast_df.empty:
                        fig = plot_forecast_with_actuals(
                            ts_df,
                            forecast_df,
                            title=f"Temperature Forecast: {model_name}",
                            y_label="Temperature (°C)",
                        )
                        if idx % 2 == 0:
                            with left_col:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            with right_col:
                                st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Rainfall Trend Analysis & Forecast")
    st.caption(f"Forecasting {forecast_days} days ahead")
    
    if rainfall_df.empty:
        st.warning("No rainfall data available.")
    else:
        ts_df = prepare_timeseries(rainfall_df, "precip_mm", "date")
        
        if len(ts_df) < 7:
            st.error("Need at least 7 days of historical data.")
        else:
            # Display summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rainfall (mm)", f"{ts_df['precip_mm'].sum():.1f}")
            col2.metric("Average Daily (mm)", f"{ts_df['precip_mm'].mean():.2f}")
            col3.metric("Rainy Days (>1mm)", f"{(ts_df['precip_mm'] > 1).sum()}")
            
            # Plot historical + SARIMA forecast
            future_dates = generate_future_dates(ts_df["date"].iloc[-1], forecast_days, freq="D")
            timeseries = ts_df["precip_mm"]
            
            with st.spinner("Running SARIMA for rainfall..."):
                result = forecast_sarima(
                    timeseries,
                    periods=forecast_days,
                    order=(1, 1, 1),
                    seasonal_order=(1, 1, 1, 7),
                )
                forecast_df = create_forecast_dataframe(result, future_dates, "SARIMA")
                if not result.get("success", False):
                    st.warning(f"Rainfall SARIMA failed: {result.get('error', 'Unknown error')}")
            
            if not forecast_df.empty:
                fig = plot_forecast_with_actuals(
                    ts_df,
                    forecast_df,
                    title="Rainfall Forecast (SARIMA with 7-day seasonality)",
                    y_label="Precipitation (mm)",
                )
                st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Air Quality Index (AQI) Forecast")
    st.caption(f"Forecasting {forecast_days} days ahead")
    
    if aqi_df.empty:
        st.warning("No AQI data available.")
    else:
        ts_df = prepare_timeseries(aqi_df, "aqi", "date")
        
        if len(ts_df) < 7:
            st.error("Need at least 7 days of historical data.")
        else:
            # Display summary
            latest_aqi = ts_df["aqi"].iloc[-1]
            avg_aqi = ts_df["aqi"].mean()
            
            col1, col2 = st.columns(2)
            col1.metric("Latest AQI", f"{latest_aqi:.0f}")
            col2.metric("Average AQI (period)", f"{avg_aqi:.0f}")
            
            st.info("""
            **AQI Scale**: 0-50 (Good) | 51-100 (Moderate) | 101-150 (Unhealthy for Sensitive) | 
            151-200 (Unhealthy) | 201-300 (Very Unhealthy) | 301+ (Hazardous)
            """)
            
            # Plot with Prophet
            future_dates = generate_future_dates(ts_df["date"].iloc[-1], forecast_days, freq="D")
            
            with st.spinner("Running Facebook Prophet for AQI..."):
                prophet_input = ts_df[["date", "aqi"]].copy()
                prophet_input.columns = ["date", "y"]
                result = forecast_prophet(prophet_input, periods=forecast_days, freq="D")
                forecast_df = create_forecast_dataframe(result, future_dates, "Prophet")
                if not result.get("success", False):
                    st.warning(f"AQI Prophet failed: {result.get('error', 'Unknown error')}")
            
            if not forecast_df.empty:
                fig = plot_forecast_with_actuals(
                    ts_df.rename(columns={"aqi": "y"}),
                    forecast_df,
                    title="Air Quality Index Forecast (Prophet)",
                    y_label="AQI",
                    y_col="y",
                )
                st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Atmospheric CO2 Trends & Forecast")
    st.caption("Global atmospheric CO2 concentration (NOAA Mauna Loa)")
    
    if co2_df.empty:
        st.warning("No CO2 data available.")
    else:
        # Display metrics
        latest = co2_df.iloc[-1]
        one_year_ago_cutoff = latest["date"] - timedelta(days=365)
        prev_candidates = co2_df[co2_df["date"] <= one_year_ago_cutoff]
        yoy_change = None
        if not prev_candidates.empty:
            yoy_change = float(latest["co2_ppm"] - prev_candidates.iloc[-1]["co2_ppm"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest CO2 (ppm)", f"{latest['co2_ppm']:.2f}")
        col2.metric("1Y Change (ppm)", f"{yoy_change:+.2f}" if yoy_change is not None else "N/A")
        col3.metric("Data Points", len(co2_df))
        
        # Prepare for forecasting (weekly data)
        ts_df = prepare_timeseries(co2_df, "co2_ppm", "date")
        
        if len(ts_df) >= 12:
            future_dates = generate_future_dates(ts_df["date"].iloc[-1], forecast_days // 7, freq="W")
            timeseries = ts_df["co2_ppm"]
            
            # Use both ARIMA and Prophet for CO2
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.write("**ARIMA Forecast** (Long-term trends)")
                with st.spinner("Running ARIMA..."):
                    result = forecast_arima(timeseries, periods=forecast_days // 7, order=(2, 1, 1))
                    forecast_df_arima = create_forecast_dataframe(result, future_dates, "ARIMA")
                    if not result.get("success", False):
                        st.warning(f"CO2 ARIMA failed: {result.get('error', 'Unknown error')}")
                
                if not forecast_df_arima.empty:
                    fig = plot_forecast_with_actuals(
                        ts_df,
                        forecast_df_arima,
                        title="CO2 Forecast - ARIMA",
                        y_label="CO2 (ppm)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_right:
                st.write("**Prophet Forecast** (Automatic seasonality)")
                with st.spinner("Running Prophet..."):
                    prophet_input = ts_df[["date", "co2_ppm"]].copy()
                    result = forecast_prophet(prophet_input, periods=forecast_days // 7, freq="W")
                    forecast_df_prophet = create_forecast_dataframe(result, future_dates, "Prophet")
                    if not result.get("success", False):
                        st.warning(f"CO2 Prophet failed: {result.get('error', 'Unknown error')}")
                
                if not forecast_df_prophet.empty:
                    fig = plot_forecast_with_actuals(
                        ts_df,
                        forecast_df_prophet,
                        title="CO2 Forecast - Prophet",
                        y_label="CO2 (ppm)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    "\n".join(
        [
            "**Data Sources & Methods**",
            "- **Temperature**: NASA POWER Daily API (`T2M`) + NOAA NCEI Daily Summaries",
            "- **Precipitation**: Open-Meteo Archive API (historical) + synthetic for testing",
            "- **Air Quality**: Synthetic AQI data for demonstration",
            "- **CO2**: NOAA GML weekly atmospheric CO2 records (Mauna Loa)",
            "",
            "**Forecasting Models**",
            "- **ARIMA**: Box-Jenkins autoregressive model, best for non-seasonal trends",
            "- **SARIMA**: Seasonal ARIMA, captures weekly/seasonal patterns",
            "- **Prophet**: Facebook's additive model, auto-handles seasonality & holidays",
        ]
    )
)

"""Time series forecasting models for climate data."""

from __future__ import annotations

from datetime import timedelta
import warnings

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def prepare_timeseries(df: pd.DataFrame, value_col: str, date_col: str = "date") -> pd.DataFrame:
    """Prepare and validate time series data.
    
    Args:
        df: DataFrame with time series data
        value_col: Column name containing values to forecast
        date_col: Column name containing dates
        
    Returns:
        Cleaned DataFrame with date index and no missing values
    """
    result = df[[date_col, value_col]].copy()
    result[date_col] = pd.to_datetime(result[date_col])
    result[value_col] = pd.to_numeric(result[value_col], errors="coerce")
    result = result.dropna()
    result = result.sort_values(date_col).reset_index(drop=True)
    return result


def forecast_arima(
    timeseries: pd.Series, 
    periods: int = 30,
    order: tuple = (1, 1, 1)
) -> dict:
    """ARIMA forecast for non-seasonal data.
    
    Args:
        timeseries: Pandas Series with numeric values
        periods: Number of periods ahead to forecast
        order: ARIMA (p, d, q) parameters
        
    Returns:
        Dict with forecast values, confidence intervals, and metrics
    """
    try:
        model = ARIMA(timeseries, order=order)
        fitted = model.fit()
        
        forecast_result = fitted.get_forecast(steps=periods)
        forecast_values = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        
        # Calculate metrics on training data
        fitted_values = fitted.fittedvalues
        mae = mean_absolute_error(timeseries[len(timeseries) - len(fitted_values):], fitted_values)
        rmse = np.sqrt(mean_squared_error(timeseries[len(timeseries) - len(fitted_values):], fitted_values))
        
        return {
            "forecast": forecast_values.values,
            "lower_ci": conf_int.iloc[:, 0].values,
            "upper_ci": conf_int.iloc[:, 1].values,
            "mae": mae,
            "rmse": rmse,
            "model": "ARIMA",
            "success": True,
        }
    except Exception as e:
        return {
            "forecast": np.full(periods, np.nan),
            "lower_ci": np.full(periods, np.nan),
            "upper_ci": np.full(periods, np.nan),
            "mae": None,
            "rmse": None,
            "model": "ARIMA",
            "success": False,
            "error": str(e),
        }


def forecast_sarima(
    timeseries: pd.Series,
    periods: int = 30,
    order: tuple = (1, 1, 1),
    seasonal_order: tuple = (1, 1, 1, 12),
) -> dict:
    """SARIMA forecast for seasonal data.
    
    Args:
        timeseries: Pandas Series with numeric values
        periods: Number of periods ahead to forecast
        order: ARIMA (p, d, q) parameters
        seasonal_order: (P, D, Q, s) seasonal parameters
        
    Returns:
        Dict with forecast values, confidence intervals, and metrics
    """
    try:
        # Ensure minimum data length
        if len(timeseries) < seasonal_order[-1] * 2:
            return forecast_arima(timeseries, periods, order)
        
        model = SARIMAX(timeseries, order=order, seasonal_order=seasonal_order)
        fitted = model.fit(disp=False)
        
        forecast_result = fitted.get_forecast(steps=periods)
        forecast_values = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        
        # Calculate metrics
        fitted_values = fitted.fittedvalues
        mae = mean_absolute_error(timeseries[len(timeseries) - len(fitted_values):], fitted_values)
        rmse = np.sqrt(mean_squared_error(timeseries[len(timeseries) - len(fitted_values):], fitted_values))
        
        return {
            "forecast": forecast_values.values,
            "lower_ci": conf_int.iloc[:, 0].values,
            "upper_ci": conf_int.iloc[:, 1].values,
            "mae": mae,
            "rmse": rmse,
            "model": "SARIMA",
            "success": True,
        }
    except Exception as e:
        return {
            "forecast": np.full(periods, np.nan),
            "lower_ci": np.full(periods, np.nan),
            "upper_ci": np.full(periods, np.nan),
            "mae": None,
            "rmse": None,
            "model": "SARIMA",
            "success": False,
            "error": str(e),
        }


def forecast_prophet(
    df: pd.DataFrame,
    periods: int = 30,
    freq: str = "D",
) -> dict:
    """Facebook Prophet forecast with automatic seasonality detection.
    
    Args:
        df: DataFrame with 'ds' (date) and 'y' (value) columns
        periods: Number of periods ahead to forecast
        freq: Frequency ('D' for daily, 'W' for weekly, etc.)
        
    Returns:
        Dict with forecast values, confidence intervals, and metrics
    """
    try:
        # Prepare data for Prophet
        prophet_df = df.copy()
        prophet_df.columns = ["ds", "y"]
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
        prophet_df = prophet_df.sort_values("ds").reset_index(drop=True)
        
        if len(prophet_df) < 7:
            return {
                "forecast": np.full(periods, np.nan),
                "lower_ci": np.full(periods, np.nan),
                "upper_ci": np.full(periods, np.nan),
                "mae": None,
                "rmse": None,
                "model": "Prophet",
                "success": False,
                "error": "Insufficient data (minimum 7 points required)",
            }
        
        model = Prophet(
            yearly_seasonality="auto",
            weekly_seasonality="auto",
            daily_seasonality=False,
            interval_width=0.95,
        )
        
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        
        # Extract forecast for future periods only
        future_forecast = forecast.iloc[-periods:]
        
        return {
            "forecast": future_forecast["yhat"].values,
            "lower_ci": future_forecast["yhat_lower"].values,
            "upper_ci": future_forecast["yhat_upper"].values,
            "mae": None,  # Prophet doesn't provide built-in residual metrics easily
            "rmse": None,
            "model": "Prophet",
            "success": True,
        }
    except Exception as e:
        return {
            "forecast": np.full(periods, np.nan),
            "lower_ci": np.full(periods, np.nan),
            "upper_ci": np.full(periods, np.nan),
            "mae": None,
            "rmse": None,
            "model": "Prophet",
            "success": False,
            "error": str(e),
        }


def generate_future_dates(last_date: pd.Timestamp, periods: int, freq: str = "D") -> pd.DatetimeIndex:
    """Generate future date range.
    
    Args:
        last_date: Last date in historical data
        periods: Number of future periods
        freq: Pandas frequency string ('D', 'W', etc.)
        
    Returns:
        DatetimeIndex of future dates
    """
    if freq == "D":
        return pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq="D")
    elif freq == "W":
        return pd.date_range(start=last_date + timedelta(weeks=1), periods=periods, freq="W")
    else:
        return pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq=freq)


def create_forecast_dataframe(
    forecast_dict: dict,
    future_dates: pd.DatetimeIndex,
    model_name: str = None,
) -> pd.DataFrame:
    """Create a DataFrame from forecast results.
    
    Args:
        forecast_dict: Output from forecast function
        future_dates: DatetimeIndex of forecast dates
        model_name: Name to include in output
        
    Returns:
        DataFrame with forecast, upper/lower bounds, and date
    """
    if not forecast_dict.get("success", False):
        return pd.DataFrame()
    
    result = pd.DataFrame({
        "date": future_dates,
        "forecast": forecast_dict["forecast"],
        "lower_ci": forecast_dict["lower_ci"],
        "upper_ci": forecast_dict["upper_ci"],
    })
    
    if model_name:
        result["model"] = model_name
    
    return result

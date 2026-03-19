# Live Climate Impact Dashboard with AI Forecasting

A Streamlit dashboard that combines **live climate data** from NASA and NOAA with **AI-powered time series forecasting** to monitor and predict:

- **Temperature** trends and anomalies (30-90 day forecasts)
- **Rainfall/Precipitation** patterns (seasonal trends)
- **Air Quality Index** (AQI) levels and anomalies
- **Atmospheric CO2** concentration trends

## 🎯 Features

### Data Integration
- **NASA POWER Daily API**: 2m air temperature (T2M) globally
- **NOAA NCEI Daily Summaries**: Station-specific temperature, min/max
- **NOAA GML Weekly CO2**: Global atmospheric CO2 (Mauna Loa reference)
- **Open-Meteo Archive API**: Historical weather with precipitation, wind, pressure
- **Synthetic Data**: AQI and rainfall for demo purposes

### Forecasting Models
- **ARIMA**: Box-Jenkins autoregressive model for trend forecasting
- **SARIMA**: Seasonal ARIMA capturing weekly/monthly patterns
- **Facebook Prophet**: Automatic seasonality detection and holiday effects

### Dashboard Views (Tabbed Interface)
1. **📊 Historical Overview** — Temperature, precipitation, CO2 current state
2. **🌡️ Temperature Forecast** — ARIMA/SARIMA/Prophet 30-90 day prediction with confidence intervals
3. **💧 Rainfall Trends** — SARIMA seasonal precipitation forecast
4. **💨 Air Quality Index** — Prophet-based AQI anomaly prediction
5. **📈 CO2 Trends** — Long-term atmospheric CO2 forecasts with ARIMA & Prophet comparison

## 📋 Project Structure

```
Live Climate Impact Dashboard/
├── app.py                    # Main Streamlit dashboard with tabs & forecasting UI
├── climate_clients.py        # NASA & NOAA API clients
├── data_fetcher_extended.py # Extended fetchers (Open-Meteo, synthetic data)
├── forecasting.py           # Core forecasting functions (ARIMA/SARIMA/Prophet)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Setup

### 1. Create & Activate Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Optional: Set NOAA API Token
For higher NOAA rate limits, set the NOAA_TOKEN environment variable:
```bash
set NOAA_TOKEN=your_token_here    # Windows
export NOAA_TOKEN=your_token_here # Mac/Linux
```

Get your free token from: https://www.ncei.noaa.gov/products/etl-ncei-apis

## 🚀 Run

```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit>=1.36.0` | Web dashboard framework |
| `pandas>=2.2.2` | Data manipulation |
| `plotly>=5.22.0` | Interactive visualizations |
| `statsmodels>=0.14.0` | ARIMA/SARIMA models |
| `prophet>=1.1.5` | Facebook Prophet forecasting |
| `scikit-learn>=1.3.0` | Metrics & preprocessing |
| `requests>=2.32.3` | API calls |
| `python-dateutil>=2.9.0` | Date utilities |

## 📖 Usage Tips

### Selecting Forecasting Models
- Use **ARIMA** for non-seasonal data with clear trends (e.g., CO2, temperature drift)
- Use **SARIMA** for data with weekly/monthly seasonality (e.g., rainfall, AQI)
- Use **Prophet** for automatic seasonality detection (accepts multiple seasonalities)

### Forecast Horizon
- **7-14 days**: High confidence, captures immediate trends
- **30 days**: Moderate confidence, weekly seasonality captures well
- **60+ days**: Lower confidence, useful for seasonal planning only

### Understanding Confidence Intervals
- **95% CI** (shaded area) bounds forecasts
- Wider intervals = higher uncertainty
- Intervals expand further into the future

## 🔴 Common Issues

**"Insufficient data for forecasting"**
- Date range too short; use at least 7 days, preferably 30+ days

**Prophet takes a long time**
- Normal for initial fit (5-15 seconds), uses Bayesian inference internally
- Consider reducing forecast horizon or date range for faster results

**NOAA station data unavailable**
- Some stations lack complete daily summaries; try a different airport/station ID

**API timeouts**
- Network issue or API down; the dashboard gracefully falls back to synthetic data

## 🔗 Data Sources

- **NASA POWER**: https://power.larc.nasa.gov/
- **NOAA NCEI**: https://www.ncei.noaa.gov/
- **NOAA GML**: https://gml.noaa.gov/ccgg/trends/
- **Open-Meteo**: https://open-meteo.com/

## 📝 License & Attribution

- NASA data: Public domain
- NOAA data: Public domain
- Prophet: Developed by Facebook (Meta)

## 🚀 Future Enhancements

- [ ] Multiple location comparison forecasts
- [ ] Historical forecast accuracy evaluation
- [ ] Download forecasts as CSV/PDF
- [ ] Real-time alert system for anomalies
- [ ] Custom model hyperparameter tuning
- [ ] Integration with weather alert APIs
- [ ] Mobile-friendly responsive design


# Live Climate Impact Dashboard

A Streamlit dashboard that combines live climate data from NASA and NOAA to monitor:

- Temperature trends and rises over time
- Air-quality pressure through atmospheric CO2 concentration

## Data Sources

- NASA POWER Daily API (2m air temperature: `T2M`)
- NOAA NCEI Daily Summaries API (`TAVG`, `TMAX`, `TMIN`)
- NOAA GML Weekly CO2 data (Mauna Loa)

## Project Structure

- `app.py` - Streamlit dashboard UI
- `climate_clients.py` - API clients and parsing logic
- `requirements.txt` - Python dependencies
- `.env.example` - Optional NOAA token configuration

## Setup

1. Open a terminal in this folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optional: set a NOAA token if you need higher rate limits:

```bash
set NOAA_TOKEN=your_token_here
```

## Run

```bash
streamlit run app.py
```

## Notes

- The NOAA station can be changed from the sidebar. Some stations may not provide complete daily summaries for all date ranges.
- If NOAA daily temperature is unavailable for a selected station, the dashboard still renders NASA temperature and NOAA CO2 views.

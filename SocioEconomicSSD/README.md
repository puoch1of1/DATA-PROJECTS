# SocioEconomic Indicators Analysis - South Sudan

A comprehensive data pipeline for extracting, cleaning, transforming, and analyzing South Sudan's socioeconomic indicators including population, GDP, and life expectancy trends.

## Project Overview

This project demonstrates a complete ETL (Extract-Transform-Load) workflow for socioeconomic data:
- **Extract**: Load raw CSV data files
- **Transform**: Standardize columns, data types, and missing value handling
- **Load**: Persist cleaned data to SQLite database and CSV export
- **Analyze**: Exploratory data analysis via Jupyter notebooks

## Data Sources

Three primary indicators tracked for South Sudan:

| Indicator | File | Records | Time Period |
|-----------|------|---------|-------------|
| Population | `raw/population.csv` | Country-level annual counts | - |
| GDP (Current US$) | `raw/gdp.csv` | Gross domestic product | - |
| Life Expectancy at Birth | `raw/life_expectancy.csv` | Years from birth | - |

## Project Structure

```
SocioEconomicSSD/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── raw/                         # Source CSV files (raw data)
│   ├── population.csv
│   ├── gdp.csv
│   └── life_expectancy.csv
├── cleaned/                     # Processed CSV outputs
│   └── south_sudan_clean.csv
├── database/                    # SQLite database storage
│   └── south_sudan.db
├── scripts/                     # ETL pipeline components
│   ├── run_pipeline.py          # Main orchestrator
│   ├── extract.py               # Data extraction
│   ├── transform.py             # Data transformation & cleaning
│   └── load.py                  # Database loading
└── analysis/                    # Data exploration
    └── trends.ipynb             # Jupyter notebook for analysis
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone/Navigate to project directory**
   ```bash
   cd SocioEconomicSSD
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or: source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run Complete Pipeline

Execute the full ETL pipeline in one command:

```bash
python scripts/run_pipeline.py --output-csv cleaned/south_sudan_clean.csv
```

**Command-line options:**
- `--output-csv PATH` (default: `cleaned/south_sudan_clean.csv`) - CSV export path
- `--db-path PATH` (default: `database/south_sudan.db`) - SQLite database location
- `--verbose` - Show detailed processing logs
- `--skip-db-load` - Skip database loading (CSV export only)
- `--force` - Overwrite existing outputs

### Run Pipeline Steps Individually

**Extract only:**
```bash
python scripts/run_pipeline.py --extract-only
```

**Transform only:**
```bash
python scripts/run_pipeline.py --transform-only
```

**Load only (database):**
```bash
python scripts/run_pipeline.py --load-only
```

### Example: Verify Pipeline Results

```bash
# Load and inspect cleaned data
python -c "
import pandas as pd
df = pd.read_csv('cleaned/south_sudan_clean.csv')
print(f'Rows: {len(df)}')
print(f'Indicators: {df[\"indicator\"].unique()}')
print(df.head())
"
```

## Data Pipeline Details

### Extract (`extract.py`)
- Loads three raw CSV files from `raw/` directory
- Returns dictionary of indicator dataframes
- Handles file-not-found errors gracefully

### Transform (`transform.py`)
- Standardizes column names (Country/Year/Value)
- Converts year to integer, value to float
- Removes commas and handles non-numeric values
- Drops rows with missing data
- Adds indicator name column
- Combines all indicators into single dataframe

### Load (`load.py`)
- Exports cleaned CSV to `cleaned/` directory
- Creates/upserts SQLite table with schema:
  ```sql
  CREATE TABLE socio_economic_indicators (
      country TEXT,
      year INTEGER,
      indicator TEXT,
      value REAL
  );
  ```
- Returns row count for validation

### Validation
- Confirms extracted vs. transformed row counts
- Validates data types (year: int, value: float)
- Checks for NULL values after loading
- Prints summary statistics

## Output Samples

### CSV Export (`cleaned/south_sudan_clean.csv`)
```
country,year,indicator,value
South Sudan,2015,Population,11381378.0
South Sudan,2015,GDP (current US$),4.2e+09
South Sudan,2015,Life Expectancy at Birth,55.9
...
```

### Database Table (`database/south_sudan.db`)
- Table: `socio_economic_indicators`
- Total records: ~180 (3 indicators × ~60 years each)
- Query example: `SELECT * WHERE indicator='GDP' ORDER BY year DESC LIMIT 10`

## Analysis

Explore the cleaned data using the Jupyter notebook:

```bash
jupyter notebook analysis/trends.ipynb
```

**Suggested analyses:**
- Population growth trends
- GDP per capita expansion
- Life expectancy improvement trajectory
- Correlation between GDP and life expectancy
- Year-over-year growth rates

## Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| pandas | Data manipulation & CSV/SQL I/O | ≥1.0.0 |
| sqlite3 | Database (built-in to Python) | - |

See `requirements.txt` for complete dependency list.

## Troubleshooting

### Error: "File not found: population.csv"
- **Cause**: Raw data files missing from `raw/` directory
- **Solution**: Verify all CSVs are present: `population.csv`, `gdp.csv`, `life_expectancy.csv`

### Error: "duplicate record inserted"
- **Cause**: Database table already populated
- **Solution**: Use `--force` flag to overwrite, or delete `database/south_sudan.db`

### Error: "Column 'Country' not found"
- **Cause**: Unexpected CSV structure or encoding issue
- **Solution**: Check CSV headers match expected format (Country, Year, Value)
- Run with `--verbose` for detailed column mapping

### SQLite database locked
- **Cause**: Another process has database file open
- **Solution**: Close Jupyter/DB browser, or specify different DB path with `--db-path`

## Future Enhancements

- [ ] Add more indicators (inflation, unemployment, HDI components)
- [ ] Implement data update automation (scheduled fetches from World Bank API)
- [ ] Add data visualization dashboard (Streamlit/Plotly)
- [ ] Support for comparative country analysis (regional trends)
- [ ] Export to multiple formats (Excel, Parquet, JSON)

## License

Internal project. For data attribution, see source CSV files.

## Author

Data Projects Team | April 2026

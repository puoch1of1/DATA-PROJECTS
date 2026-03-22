## REST API ETL Project

This project extracts development indicators from the World Bank API, transforms them into an analysis-ready table, and loads the results into SQLite.

### Pipeline flow

1. Extract indicator payloads from World Bank REST API
2. Transform payloads into tidy records (`country`, `year`, `indicator`, `value`, `ingested_at`)
3. Load records into SQLite table `development_indicators`
4. Verify row counts and null quality checks

### Project structure

```text
REST API PROJECT/
├── run_pipeline.py
├── requirements.txt
├── data/
│   ├── south_sudan_population.json
│   └── cleaned/
│       └── south_sudan_clean.csv
├── database/
│   └── worldbank.db
└── scripts/
    ├── extract.py
    ├── transform.py
    ├── load.py
    ├── verify.py
    └── worldbank_client.py
```

### Setup

```bash
pip install -r requirements.txt
```

### Run full pipeline

```bash
python run_pipeline.py
```

Useful options:

```bash
python run_pipeline.py --country SSD --db database/worldbank.db --table development_indicators
python run_pipeline.py --export-csv data/cleaned/south_sudan_clean.csv
python run_pipeline.py --export-csv ""
```

### Run individual stages

```bash
python scripts/extract.py --country SSD --indicator SP.POP.TOTL --output data/south_sudan_population.json
python scripts/transform.py
python scripts/load.py
python scripts/verify.py
```

### Notes

- Loader auto-creates table if missing and syncs the `ingested_at` column if older schema exists.
- Loads are idempotent by business key (`country`, `year`, `indicator`) to avoid duplicate rows.
- `verify.py` prints row totals, null checks, and latest rows for quick QA.

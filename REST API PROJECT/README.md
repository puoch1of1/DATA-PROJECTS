REST API
   ↓
requests (Python)
   ↓
JSON parsing
   ↓
pandas (cleaning & shaping)
   ↓
SQLite (storage)
   ↓
SQL / analysis


FILE STRUCTURE

rest-api-etl/
│
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── data/
│   └── cleaned/
│       └── population.csv
│
├── database/
│   └── worldbank.db
│
└── README.md

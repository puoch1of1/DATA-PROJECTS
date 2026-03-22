import json
from pathlib import Path
from typing import Any

import pandas as pd
import os


def _read_json_file(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_payload(json_data: Any):
    if not isinstance(json_data, list) or len(json_data) < 2:
        raise ValueError("Input JSON must be a 2-item list as returned by World Bank API")

    records = json_data[1]
    if records is None:
        return []

    if not isinstance(records, list):
        raise ValueError("Input JSON records must be a list")

    return records


def transform_population(json_data, indicator_name, ingestion_time):
    records = []

    for row in _validate_payload(json_data):
        if row["value"] is not None:
            records.append({
                "country": row["country"]["value"],
                "year": int(row["date"]),
                "indicator": indicator_name,
                "value": float(row["value"]),
                "ingested_at": ingestion_time
            })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = df.sort_values("year")
    df["year"] = df["year"].astype("int64")

    return df


def transform_indicator(json_data, indicator_name, ingestion_time=None, output_file_path=None):
    """Transform indicator data from a World Bank API JSON payload."""
    df = transform_population(json_data, indicator_name, ingestion_time)

    if output_file_path:
        df.to_csv(output_file_path, index=False)

    return df


def transform_file(json_path: Path, output_path: Path, indicator_name: str, ingestion_time: str):
    payload = _read_json_file(json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return transform_indicator(payload, indicator_name, ingestion_time, output_path)


# Main execution when run directly
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    json_path = Path(project_dir) / "data" / "south_sudan_population.json"
    output_path = Path(project_dir) / "data" / "cleaned" / "south_sudan_clean.csv"

    transformed = transform_file(
        json_path,
        output_path,
        indicator_name="Population",
        ingestion_time=pd.Timestamp.utcnow().isoformat(),
    )
    print(f"Saved {len(transformed)} records to {output_path}")
import pandas as pd
import json
import os

def transform_population(json_data, indicator_name, ingestion_time):
    records = []

    for row in json_data[1]:
        if row["value"] is not None:
            records.append({
                "country": row["country"]["value"],
                "year": int(row["date"]),
                "indicator": indicator_name,
                "value": row["value"], 
                "ingested_at": ingestion_time
            })

    df = pd.DataFrame(records)
    df = df.sort_values("year")
    
    return df

def transform_indicator(json_data, indicator_name, ingestion_time=None, output_file_path=None):
    """Transform population data from JSON"""
    df = transform_population(json_data, indicator_name, ingestion_time)
    
    if output_file_path:
        df.to_csv(output_file_path, index=False)
    
    return df

# Main execution when run directly
if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    json_path = os.path.join(project_dir, "data", "south_sudan_population.json")
    output_path = os.path.join(project_dir, "data", "cleaned", "south_sudan_clean.csv")
    
    transform_indicator(json_path, output_path)
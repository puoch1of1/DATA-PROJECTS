import pandas as pd

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

# Load data from JSON file
with open("../data/south_sudan_population.json") as f:
    import json
    data = json.load(f)

df = transform_population(data)
df.to_csv("../data/cleaned/south_sudan_clean.csv")
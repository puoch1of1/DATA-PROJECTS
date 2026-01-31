import pandas as pd

def transform_population(json_data):
    records = []

    for row in json_data[1]:
        if row["value"] is not None:
            records.append({
                "country": row["country"]["value"],
                "year": int(row["date"]),
                "indicator": "Population",
                "value": row["value"]
            })

    df = pd.DataFrame(records)
    df = df.sort_values("year")
    
    return df

# Load data from JSON file
with open("data/south_sudan_population.json") as f:
    import json
    data = json.load(f)

df = transform_population(data)
df.to_csv("DATA-PROJECTS/REST API PROJECT/data/cleaned/south_sudan_clean.csv")
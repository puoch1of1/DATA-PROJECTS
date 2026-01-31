import pandas as pd

def transform_population(json_data):
    records = []

    for row in json_data[1]:
        if row["value"] is not None:
            records.append({
                "country": row["country"]["value"],
                "year": int(row["date"]),
                "indicator": "Population",
                "value": row["vaue"]
            })

    df = pd.DataFrame(records)
    df = df.sort_values("year")
    
    return df
import requests
import json

url = (
    "https://api.worldbank.org/v2/country/SSD/"
    "indicator/SP.POP.TOTL"
    "?format=json&per_page=1000"
)

response = requests.get(url)
data = response.json()

# Save the extracted data to JSON file
with open("../data/south_sudan_population.json", "w") as f:
    json.dump(data, f, indent=2)
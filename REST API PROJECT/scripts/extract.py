import requests

url = (
    "https://api.worldbank.org/v2/country/SSD/"
    "indicator/SP.POP.TOTL"
    "?format=json&per_page=1000"
)

response = requests.get(url)
data = response.json()
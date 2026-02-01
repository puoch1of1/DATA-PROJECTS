import requests
import time

class WorldBankClient:
    BASE_URL = "https://api.worldbank.org/V2"

    def __init__(self, retries=3, timeout=10):
        self.retries = retries
        self.timeout = timeout

        def fetch_indicator(self, country_code, indicator_code):
            url = (
                f"{self.BASE_URL}/country/{country_code}/indicator/"
                f"{indicator_code}?format=json&per_page=1000"
            )

            for attempt in range(1, self.retries + 1):
                try: 
                    response = requests.get(url, timeout=self.timeout)

                    if response.status_code == 200:
                        return response.json()
                    
                    else: 
                        print(
                            f"Attempt {attempt}: "
                            f"Status {response.status_code}"
                        )
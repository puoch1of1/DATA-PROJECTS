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
            )
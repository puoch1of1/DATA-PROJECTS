import time
from typing import Any

import requests

class WorldBankClient:
    BASE_URL = "https://api.worldbank.org/V2"

    def __init__(self, retries=5, timeout=30, backoff_seconds=2):
        self.retries = retries
        self.timeout = timeout
        self.backoff_seconds = backoff_seconds
        self.session = requests.Session()

    def _validate_payload(self, payload: Any, indicator_code: str):
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(
                f"Unexpected payload for indicator {indicator_code}: expected a 2-item list"
            )

        if payload[1] is None:
            raise ValueError(f"No records returned for indicator {indicator_code}")

        if not isinstance(payload[1], list):
            raise ValueError(
                f"Unexpected records type for indicator {indicator_code}: {type(payload[1]).__name__}"
            )

    def fetch_indicator(self, country_code, indicator_code):
        url = (
            f"{self.BASE_URL}/country/{country_code}/indicator/"
            f"{indicator_code}?format=json&per_page=1000"
        )

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)

                if response.status_code == 200:
                    payload = response.json()
                    self._validate_payload(payload, indicator_code)
                    return payload

                else:
                    print(
                        f"Attempt {attempt}: "
                        f"Status {response.status_code}"
                    )

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt}: {e}")
            except ValueError as e:
                print(f"Attempt {attempt}: {e}")

            if attempt < self.retries:
                time.sleep(self.backoff_seconds * attempt)

        raise RuntimeError(
            f"Failed to fetch {indicator_code} after {self.retries} attempts"
        )
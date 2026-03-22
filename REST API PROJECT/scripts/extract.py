import argparse
import json
from pathlib import Path

from worldbank_client import WorldBankClient


def extract_indicator(country_code: str, indicator_code: str):
    client = WorldBankClient()
    return client.fetch_indicator(country_code, indicator_code)


def save_json(payload, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Extract indicator data from the World Bank API")
    parser.add_argument("--country", default="SSD", help="Country code (default: SSD)")
    parser.add_argument(
        "--indicator",
        default="SP.POP.TOTL",
        help="Indicator code (default: SP.POP.TOTL)",
    )
    parser.add_argument(
        "--output",
        default="data/south_sudan_population.json",
        help="Output JSON path relative to project root",
    )
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent.parent
    output_path = project_dir / args.output

    payload = extract_indicator(args.country, args.indicator)
    save_json(payload, output_path)
    print(f"Saved extracted data to {output_path}")


if __name__ == "__main__":
    main()
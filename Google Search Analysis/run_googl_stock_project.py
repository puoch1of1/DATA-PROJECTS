"""Run the GOOGL stock dataset analysis project end-to-end."""

from __future__ import annotations

from pathlib import Path
import argparse

from googl_stock_project import GOOGLStockAnalyzer


def run_project(input_csv: Path) -> None:
    base_dir = Path(__file__).resolve().parent

    data_output = base_dir / "data" / "googl_enriched.csv"
    kpi_output = base_dir / "reports" / "googl_kpis.json"
    summary_output = base_dir / "reports" / "googl_analysis_summary.txt"
    charts_output = base_dir / "reports"

    analyzer = GOOGLStockAnalyzer(csv_path=input_csv, ticker="GOOGL")
    analyzer.load_data()
    analyzer.engineer_features()

    exported_files = analyzer.export_outputs(
        data_output_path=data_output,
        kpi_output_path=kpi_output,
        summary_output_path=summary_output,
    )
    chart_files = analyzer.generate_charts(output_dir=charts_output)
    kpis = analyzer.calculate_kpis()

    print("\nGOOGL Data Project Completed")
    print("=" * 50)
    print(f"Date range: {kpis.start_date} -> {kpis.end_date}")
    print(f"Trading days: {kpis.trading_days}")
    print(f"Total return: {kpis.total_return_pct}%")
    print(f"CAGR: {kpis.cagr_pct}%")
    print(f"Annualized volatility: {kpis.annualized_volatility_pct}%")
    print(f"Max drawdown: {kpis.max_drawdown_pct}%")
    print(f"Trend signal: {kpis.trend_signal}")

    print("\nGenerated files:")
    for _, path in exported_files.items():
        print(f"- {path}")
    for _, path in chart_files.items():
        print(f"- {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GOOGL stock dataset project runner")
    parser.add_argument(
        "--input",
        default="data/GOOGL.csv",
        help="Path to input GOOGL CSV file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    input_csv = Path(args.input)

    if not input_csv.exists():
        alt = Path(__file__).resolve().parent / args.input
        if alt.exists():
            input_csv = alt

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {args.input}")

    run_project(input_csv=input_csv)

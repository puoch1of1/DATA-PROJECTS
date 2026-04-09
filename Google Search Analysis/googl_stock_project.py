"""GOOGL stock dataset project utilities.

This module loads OHLCV data, engineers core financial features,
computes business-friendly KPIs, and generates report visualizations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252


@dataclass
class StockKPIs:
    """Container for key stock performance indicators."""

    ticker: str
    start_date: str
    end_date: str
    trading_days: int
    start_close: float
    end_close: float
    total_return_pct: float
    cagr_pct: float
    annualized_volatility_pct: float
    max_drawdown_pct: float
    best_day_return_pct: float
    worst_day_return_pct: float
    average_daily_volume: float
    median_daily_volume: float
    latest_20d_sma: float
    latest_50d_sma: float
    latest_200d_sma: float
    trend_signal: str


class GOOGLStockAnalyzer:
    """Analyze historical GOOGL OHLCV data from CSV."""

    def __init__(self, csv_path: str | Path, ticker: str = "GOOGL"):
        self.csv_path = Path(csv_path)
        self.ticker = ticker
        self.data: pd.DataFrame | None = None
        self.enriched_data: pd.DataFrame | None = None

    def load_data(self) -> pd.DataFrame:
        """Load and validate the raw CSV file."""
        required = {"Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"}
        df = pd.read_csv(self.csv_path)

        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=numeric_cols).reset_index(drop=True)
        self.data = df
        return df

    def engineer_features(self) -> pd.DataFrame:
        """Create financial features commonly used in stock analysis."""
        if self.data is None:
            self.load_data()

        assert self.data is not None
        df = self.data.copy()

        df["daily_return"] = df["Adj Close"].pct_change()
        df["log_return"] = np.log(df["Adj Close"] / df["Adj Close"].shift(1))

        df["sma_20"] = df["Adj Close"].rolling(20).mean()
        df["sma_50"] = df["Adj Close"].rolling(50).mean()
        df["sma_200"] = df["Adj Close"].rolling(200).mean()

        df["rolling_vol_30d"] = df["daily_return"].rolling(30).std() * np.sqrt(TRADING_DAYS_PER_YEAR)

        df["cum_return"] = (1 + df["daily_return"].fillna(0)).cumprod() - 1
        df["running_peak"] = df["Adj Close"].cummax()
        df["drawdown"] = (df["Adj Close"] / df["running_peak"]) - 1

        # Volume anomaly score helps flag unusually active trading days.
        volume_mean = df["Volume"].rolling(30).mean()
        volume_std = df["Volume"].rolling(30).std()
        df["volume_zscore_30d"] = (df["Volume"] - volume_mean) / volume_std.replace(0, np.nan)

        self.enriched_data = df
        return df

    def calculate_kpis(self) -> StockKPIs:
        """Compute high-level KPIs useful for executive and analyst reporting."""
        if self.enriched_data is None:
            self.engineer_features()

        assert self.enriched_data is not None
        df = self.enriched_data.dropna(subset=["Adj Close"]).copy()

        if len(df) < 2:
            raise ValueError("Not enough rows to compute KPI metrics.")

        start_close = float(df["Adj Close"].iloc[0])
        end_close = float(df["Adj Close"].iloc[-1])
        total_return = (end_close / start_close) - 1

        days = max((df["Date"].iloc[-1] - df["Date"].iloc[0]).days, 1)
        years = days / 365.25
        cagr = (end_close / start_close) ** (1 / years) - 1 if years > 0 else 0.0

        annualized_vol = float(df["daily_return"].std() * np.sqrt(TRADING_DAYS_PER_YEAR))
        max_drawdown = float(df["drawdown"].min())

        best_day = float(df["daily_return"].max())
        worst_day = float(df["daily_return"].min())

        latest = df.iloc[-1]
        sma20 = float(latest["sma_20"]) if pd.notna(latest["sma_20"]) else float("nan")
        sma50 = float(latest["sma_50"]) if pd.notna(latest["sma_50"]) else float("nan")
        sma200 = float(latest["sma_200"]) if pd.notna(latest["sma_200"]) else float("nan")

        if np.isnan(sma20) or np.isnan(sma50) or np.isnan(sma200):
            trend_signal = "insufficient_sma_history"
        elif sma20 > sma50 > sma200:
            trend_signal = "bullish"
        elif sma20 < sma50 < sma200:
            trend_signal = "bearish"
        else:
            trend_signal = "mixed"

        return StockKPIs(
            ticker=self.ticker,
            start_date=df["Date"].iloc[0].date().isoformat(),
            end_date=df["Date"].iloc[-1].date().isoformat(),
            trading_days=int(len(df)),
            start_close=round(start_close, 4),
            end_close=round(end_close, 4),
            total_return_pct=round(total_return * 100, 2),
            cagr_pct=round(cagr * 100, 2),
            annualized_volatility_pct=round(annualized_vol * 100, 2),
            max_drawdown_pct=round(max_drawdown * 100, 2),
            best_day_return_pct=round(best_day * 100, 2),
            worst_day_return_pct=round(worst_day * 100, 2),
            average_daily_volume=round(float(df["Volume"].mean()), 2),
            median_daily_volume=round(float(df["Volume"].median()), 2),
            latest_20d_sma=round(sma20, 4) if not np.isnan(sma20) else float("nan"),
            latest_50d_sma=round(sma50, 4) if not np.isnan(sma50) else float("nan"),
            latest_200d_sma=round(sma200, 4) if not np.isnan(sma200) else float("nan"),
            trend_signal=trend_signal,
        )

    def export_outputs(
        self,
        data_output_path: str | Path,
        kpi_output_path: str | Path,
        summary_output_path: str | Path,
    ) -> Dict[str, str]:
        """Write enriched data, KPI JSON, and text summary to disk."""
        if self.enriched_data is None:
            self.engineer_features()

        kpis = self.calculate_kpis()

        data_output = Path(data_output_path)
        kpi_output = Path(kpi_output_path)
        summary_output = Path(summary_output_path)

        data_output.parent.mkdir(parents=True, exist_ok=True)
        kpi_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.parent.mkdir(parents=True, exist_ok=True)

        assert self.enriched_data is not None
        self.enriched_data.to_csv(data_output, index=False)

        with kpi_output.open("w", encoding="utf-8") as f:
            json.dump(asdict(kpis), f, indent=2)

        summary_lines = [
            f"Ticker: {kpis.ticker}",
            f"Date range: {kpis.start_date} to {kpis.end_date}",
            f"Trading days: {kpis.trading_days}",
            f"Total return: {kpis.total_return_pct}%",
            f"CAGR: {kpis.cagr_pct}%",
            f"Annualized volatility: {kpis.annualized_volatility_pct}%",
            f"Max drawdown: {kpis.max_drawdown_pct}%",
            f"Best daily return: {kpis.best_day_return_pct}%",
            f"Worst daily return: {kpis.worst_day_return_pct}%",
            f"Average daily volume: {kpis.average_daily_volume}",
            f"Median daily volume: {kpis.median_daily_volume}",
            f"Trend signal (20/50/200 SMA): {kpis.trend_signal}",
        ]

        with summary_output.open("w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines))

        return {
            "enriched_data": str(data_output),
            "kpis_json": str(kpi_output),
            "summary_text": str(summary_output),
        }

    def generate_charts(self, output_dir: str | Path) -> Dict[str, str]:
        """Generate core charts for price trend, returns, and drawdown."""
        if self.enriched_data is None:
            self.engineer_features()

        assert self.enriched_data is not None
        df = self.enriched_data.copy()

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        chart_paths: Dict[str, str] = {}

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Date"], df["Adj Close"], label="Adj Close", linewidth=1.8)
        ax.plot(df["Date"], df["sma_50"], label="SMA 50", linewidth=1.2)
        ax.plot(df["Date"], df["sma_200"], label="SMA 200", linewidth=1.2)
        ax.set_title(f"{self.ticker} Adjusted Close with Moving Averages")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(alpha=0.25)
        price_path = out / "googl_price_trend.png"
        fig.tight_layout()
        fig.savefig(price_path, dpi=220)
        plt.close(fig)
        chart_paths["price_trend"] = str(price_path)

        fig, ax = plt.subplots(figsize=(12, 5))
        returns = df["daily_return"].dropna()
        ax.hist(returns, bins=70, alpha=0.8)
        ax.set_title(f"{self.ticker} Daily Return Distribution")
        ax.set_xlabel("Daily Return")
        ax.set_ylabel("Frequency")
        ax.grid(alpha=0.2)
        returns_path = out / "googl_returns_distribution.png"
        fig.tight_layout()
        fig.savefig(returns_path, dpi=220)
        plt.close(fig)
        chart_paths["returns_distribution"] = str(returns_path)

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.fill_between(df["Date"], df["drawdown"], 0, alpha=0.5)
        ax.set_title(f"{self.ticker} Drawdown Curve")
        ax.set_xlabel("Date")
        ax.set_ylabel("Drawdown")
        ax.grid(alpha=0.2)
        drawdown_path = out / "googl_drawdown.png"
        fig.tight_layout()
        fig.savefig(drawdown_path, dpi=220)
        plt.close(fig)
        chart_paths["drawdown"] = str(drawdown_path)

        return chart_paths

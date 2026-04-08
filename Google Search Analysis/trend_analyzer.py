"""Core Pytrends-based Google Search Trends Analysis Module.

Provides functionality to:
- Fetch trending search queries
- Compare search interest across keywords
- Analyze regional search patterns
- Extract search suggestions and related queries
- Generate trend reports and statistics
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import pytrends
from pytrends.request import TrendReq

from dataclasses import dataclass
from collections import Counter


@dataclass
class TrendMetrics:
    """Statistics for a single search query."""

    keyword: str
    average_interest: float
    peak_interest: int
    peak_date: Optional[str]
    trend_direction: str  # "increasing", "decreasing", "stable"
    volatility: float
    search_count: int


class GoogleTrendAnalyzer:
    """Main class for analyzing Google search trends."""

    def __init__(self, language: str = "en", timeout: int = 10):
        """Initialize the trend analyzer.

        Args:
            language: Language code (default: 'en' for English)
            timeout: Request timeout in seconds
        """
        self.pytrends = TrendReq(hl=language, tz=360, timeout=timeout, retries=3)
        self.language = language
        self.last_query_data: Optional[pd.DataFrame] = None

    def get_trending_searches(self, country: str = "US") -> List[Dict[str, str]]:
        """Fetch current trending searches in a country.

        Args:
            country: ISO country code (US, GB, IN, etc.)

        Returns:
            List of trending search queries with rank and traffic data
        """
        try:
            trending = self.pytrends.trending_searches(pn=country)
            return [
                {
                    "rank": idx + 1,
                    "query": query,
                    "country": country,
                }
                for idx, query in enumerate(trending[0].values)
            ]
        except Exception as e:
            print(f"Error fetching trending searches for {country}: {e}")
            return []

    def get_search_suggestions(self, keyword: str) -> List[str]:
        """Get Google's autocomplete suggestions for a keyword.

        Args:
            keyword: Search keyword

        Returns:
            List of suggested search queries
        """
        try:
            suggestions = self.pytrends.suggestions(keyword)
            return [s["mid"] for s in suggestions if "mid" in s]
        except Exception as e:
            print(f"Error fetching suggestions for '{keyword}': {e}")
            return []

    def get_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str = "today 1-m",
    ) -> pd.DataFrame:
        """Get search interest over time for keywords.

        Args:
            keywords: List of keywords to analyze (max 5)
            timeframe: Timeframe string (e.g., 'today 1-m', 'today 3-m', 'today 12-m')

        Returns:
            DataFrame with dates and interest levels (0-100) for each keyword
        """
        if len(keywords) > 5:
            raise ValueError("Maximum 5 keywords allowed")

        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe)
            data = self.pytrends.interest_over_time()
            data = data.drop(columns=["isPartial"]) if "isPartial" in data.columns else data
            self.last_query_data = data
            return data
        except Exception as e:
            print(f"Error fetching interest over time: {e}")
            return pd.DataFrame()

    def get_interest_by_region(
        self,
        keywords: List[str],
        timeframe: str = "today 1-m",
        resolution: str = "country",
    ) -> pd.DataFrame:
        """Get search interest by geographic region.

        Args:
            keywords: List of keywords to analyze (max 5)
            timeframe: Timeframe string
            resolution: 'country', 'region', or 'metro'

        Returns:
            DataFrame with regions and interest levels for each keyword
        """
        if len(keywords) > 5:
            raise ValueError("Maximum 5 keywords allowed")

        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe)

            if resolution == "country":
                data = self.pytrends.interest_by_country()
            elif resolution == "region":
                data = self.pytrends.interest_by_region()
            else:
                data = self.pytrends.interest_by_region(resolution="metro")

            return data
        except Exception as e:
            print(f"Error fetching interest by region: {e}")
            return pd.DataFrame()

    def get_related_queries(self, keyword: str) -> Dict[str, pd.DataFrame]:
        """Get related queries for a keyword.

        Args:
            keyword: Search keyword

        Returns:
            Dict with 'top' and 'rising' DataFrames of related queries
        """
        try:
            self.pytrends.build_payload([keyword])
            related_queries = self.pytrends.related_queries()

            result = {}
            if keyword in related_queries and related_queries[keyword]:
                top = related_queries[keyword].get("top")
                rising = related_queries[keyword].get("rising")

                result["top"] = top if top is not None else pd.DataFrame()
                result["rising"] = rising if rising is not None else pd.DataFrame()

            return result
        except Exception as e:
            print(f"Error fetching related queries for '{keyword}': {e}")
            return {}

    def compare_keywords(
        self,
        keywords: List[str],
        timeframe: str = "today 1-m",
    ) -> pd.DataFrame:
        """Compare search interest across multiple keywords.

        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Timeframe string

        Returns:
            DataFrame with normalized interest levels for each keyword
        """
        data = self.get_interest_over_time(keywords, timeframe)
        return data

    def calculate_trend_metrics(
        self,
        keyword: str,
        timeframe: str = "today 12-m",
    ) -> TrendMetrics:
        """Calculate detailed metrics for a keyword trend.

        Args:
            keyword: Search keyword
            timeframe: Timeframe string

        Returns:
            TrendMetrics object with statistics
        """
        data = self.get_interest_over_time([keyword], timeframe)

        if data.empty:
            return TrendMetrics(
                keyword=keyword,
                average_interest=0.0,
                peak_interest=0,
                peak_date=None,
                trend_direction="unknown",
                volatility=0.0,
                search_count=0,
            )

        # Extract the keyword column
        series = data[keyword]

        # Calculate metrics
        avg_interest = float(series.mean())
        peak_interest = int(series.max())
        peak_date = str(data[series == peak_interest].index[0].date()) if series.max() > 0 else None

        # Calculate trend direction using linear regression
        values = series.values
        x = range(len(values))
        coefficients = pd.Series(values).rolling(window=3).mean().fillna(0)
        trend_slope = coefficients.iloc[-1] - coefficients.iloc[0] if len(coefficients) > 1 else 0

        if trend_slope > 5:
            trend_direction = "increasing"
        elif trend_slope < -5:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # Calculate volatility (standard deviation)
        volatility = float(series.std())

        return TrendMetrics(
            keyword=keyword,
            average_interest=avg_interest,
            peak_interest=peak_interest,
            peak_date=peak_date,
            trend_direction=trend_direction,
            volatility=volatility,
            search_count=len(data),
        )

    def get_seasonal_trends(self, keyword: str) -> Dict[str, float]:
        """Analyze seasonal patterns in search trends.

        Args:
            keyword: Search keyword

        Returns:
            Dict with month names and average interest levels
        """
        data = self.get_interest_over_time([keyword], timeframe="today 12-m")

        if data.empty:
            return {}

        # Extract month-year and calculate average
        data["month"] = data.index.month
        month_mapping = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        seasonal = data.groupby("month")[keyword].mean().to_dict()
        return {month_mapping.get(k, str(k)): v for k, v in seasonal.items()}

    def get_keyword_comparison_stats(
        self,
        keywords: List[str],
        timeframe: str = "today 12-m",
    ) -> pd.DataFrame:
        """Generate comparison statistics for multiple keywords.

        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Timeframe string

        Returns:
            DataFrame with statistics for each keyword
        """
        stats = []

        for keyword in keywords:
            metrics = self.calculate_trend_metrics(keyword, timeframe)
            stats.append(
                {
                    "keyword": keyword,
                    "avg_interest": round(metrics.average_interest, 2),
                    "peak_interest": metrics.peak_interest,
                    "peak_date": metrics.peak_date,
                    "trend": metrics.trend_direction,
                    "volatility": round(metrics.volatility, 2),
                }
            )

        return pd.DataFrame(stats)

    def export_to_csv(self, data: pd.DataFrame, filename: str) -> None:
        """Export trend data to CSV file.

        Args:
            data: DataFrame to export
            filename: Output CSV filename
        """
        try:
            data.to_csv(filename)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting data: {e}")

    def export_to_json(self, data: pd.DataFrame, filename: str) -> None:
        """Export trend data to JSON file.

        Args:
            data: DataFrame to export
            filename: Output JSON filename
        """
        try:
            data.to_json(filename, orient="table", indent=2)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Error exporting data: {e}")

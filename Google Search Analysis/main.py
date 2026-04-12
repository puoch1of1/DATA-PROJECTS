"""Main Google Trends Analysis Script.

Demonstrates core functionality of the trend analyzer module with interactive features.
"""

from __future__ import annotations

import sys
from typing import List

from trend_analyzer import GoogleTrendAnalyzer
from visualizer import TrendVisualizer


def print_section(title: str) -> None:
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"{title.center(70)}")
    print(f"{'='*70}\n")


def display_trending_searches(analyzer: GoogleTrendAnalyzer) -> None:
    """Display current trending searches by country."""
    print_section("CURRENT TRENDING SEARCHES")

    countries = ["US", "GB", "IN", "CA", "AU"]

    for country in countries:
        print(f"\nTop 10 Trending in {country}:")
        print("-" * 50)

        trending = analyzer.get_trending_searches(country)

        if not trending:
            print("  No data available")
            continue

        for item in trending[:10]:
            print(f"  {item['rank']:2d}. {item['query']}")


def display_keyword_analysis(analyzer: GoogleTrendAnalyzer, keyword: str) -> None:
    """Display detailed analysis for a single keyword."""
    print_section(f"ANALYSIS: {keyword.upper()}")

    print("Fetching trend data...")
    metrics = analyzer.calculate_trend_metrics(keyword, timeframe="today 12-m")

    print(f"\nKeyword Metrics:")
    print(f"  Average Interest:  {metrics.average_interest:.2f}")
    print(f"  Peak Interest:     {metrics.peak_interest}")
    print(f"  Peak Date:         {metrics.peak_date}")
    print(f"  Trend Direction:   {metrics.trend_direction.upper()}")
    print(f"  Volatility (Std):  {metrics.volatility:.2f}")
    print(f"  Data Points:       {metrics.search_count}")

    # Seasonal trends
    print("\nSeasonal Trends (Average Interest by Month):")
    seasonal = analyzer.get_seasonal_trends(keyword)
    for month, interest in seasonal.items():
        bar_length = int(interest / 5)
        print(f"  {month:12s}: {'█' * bar_length} {interest:.1f}")

    # Related queries
    print("\nRelated Queries:")
    related = analyzer.get_related_queries(keyword)

    if "top" in related and not related["top"].empty:
        print("  Top Related Queries:")
        for idx, row in related["top"].head(5).iterrows():
            print(f"    • {row['query']}")

    if "rising" in related and not related["rising"].empty:
        print("  Rising Related Queries:")
        for idx, row in related["rising"].head(5).iterrows():
            print(f"    • {row['query']} (+{row['value']}%)")


def compare_keywords_analysis(analyzer: GoogleTrendAnalyzer, keywords: List[str]) -> None:
    """Compare search interest across multiple keywords."""
    print_section(f"KEYWORD COMPARISON: {', '.join(keywords)}")

    print("Fetching comparison data...")
    stats_df = analyzer.get_keyword_comparison_stats(keywords, timeframe="today 12-m")

    print("\nComparison Statistics:")
    print(stats_df.to_string(index=False))

    # Interest over time
    print("\nFetching interest over time...")
    interest_data = analyzer.get_interest_over_time(keywords, timeframe="today 3-m")

    if not interest_data.empty:
        print("\nLatest Interest Levels (Past 3 Months):")
        latest = interest_data.iloc[-1]
        for keyword in keywords:
            if keyword in latest.index:
                print(f"  {keyword}: {int(latest[keyword])}")


def analyze_by_region(analyzer: GoogleTrendAnalyzer, keyword: str) -> None:
    """Analyze search interest by geographic region."""
    print_section(f"REGIONAL ANALYSIS: {keyword}")

    print("Fetching regional data...")
    regional_data = analyzer.get_interest_by_region([keyword], resolution="country")

    if regional_data.empty:
        print("No regional data available")
        return

    print("\nTop 15 Regions by Interest:")
    print("-" * 50)

    primary_col = regional_data.columns[0]
    ranked = regional_data.sort_values(by=primary_col, ascending=False).head(15)[primary_col]

    for idx, (region, interest) in enumerate(ranked.items(), 1):
        bar_length = int(interest / 5)
        print(f"  {idx:2d}. {region:20s}: {'█' * bar_length} {int(interest)}")


def interactive_menu() -> None:
    """Interactive menu for the analysis tool."""
    print("\n" + "=" * 70)
    print("GOOGLE SEARCH TRENDS ANALYZER".center(70))
    print("=" * 70)

    analyzer = GoogleTrendAnalyzer(language="en")

    while True:
        print("\n" + "-" * 70)
        print("Select an analysis option:")
        print("-" * 70)
        print("  1. View trending searches by country")
        print("  2. Analyze a single keyword")
        print("  3. Compare multiple keywords")
        print("  4. Analyze by region")
        print("  5. Get keyword suggestions")
        print("  6. Exit")
        print("-" * 70)

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            display_trending_searches(analyzer)

        elif choice == "2":
            keyword = input("Enter keyword to analyze: ").strip()
            if keyword:
                display_keyword_analysis(analyzer, keyword)

        elif choice == "3":
            keyword_input = input("Enter keywords (comma-separated, max 5): ").strip()
            keywords = [k.strip() for k in keyword_input.split(",")][:5]
            if keywords:
                compare_keywords_analysis(analyzer, keywords)

        elif choice == "4":
            keyword = input("Enter keyword for regional analysis: ").strip()
            if keyword:
                analyze_by_region(analyzer, keyword)

        elif choice == "5":
            keyword = input("Enter keyword to get suggestions: ").strip()
            if keyword:
                print(f"\nFetching suggestions for '{keyword}'...")
                suggestions = analyzer.get_search_suggestions(keyword)
                if suggestions:
                    print(f"\nTop 10 Suggestions:")
                    for idx, sugg in enumerate(suggestions[:10], 1):
                        print(f"  {idx}. {sugg}")
                else:
                    print("No suggestions found")

        elif choice == "6":
            print("\nThank you for using Google Search Trends Analyzer!")
            break

        else:
            print("Invalid choice. Please try again.")


def run_sample_analysis() -> None:
    """Run a sample analysis with predefined keywords."""
    print_section("SAMPLE ANALYSIS: TECHNOLOGY TRENDS")

    analyzer = GoogleTrendAnalyzer()
    keywords = ["artificial intelligence", "machine learning", "data science"]

    # Compare keywords
    print("Comparing search trends...")
    stats = analyzer.get_keyword_comparison_stats(keywords)
    print("\nKeyword Statistics:")
    print(stats.to_string(index=False))

    # Get interest over time
    print("\nFetching 3-month trend data...")
    interest_data = analyzer.get_interest_over_time(keywords, timeframe="today 3-m")

    if not interest_data.empty:
        print(f"\nData fetched: {len(interest_data)} data points")
        print("\nLatest Interest Levels:")
        print(interest_data.tail(3).to_string())

        # Save data
        analyzer.export_to_csv(interest_data, "data/tech_trends_data.csv")
        analyzer.export_to_json(interest_data, "data/tech_trends_data.json")

        # Create visualizations
        visualizer = TrendVisualizer()
        visualizer.plot_interest_over_time(
            interest_data,
            title="Technology Trends (3 Months)",
            save_path="reports/tech_trends_chart.png",
        )
        visualizer.plot_comparison_heatmap(
            interest_data,
            title="Technology Keywords Heatmap",
            save_path="reports/tech_trends_heatmap.png",
        )

    print("\nSample analysis complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Google Trends Analysis Tool")
    parser.add_argument("--mode", choices=["interactive", "sample"], default="interactive", help="Run mode")

    args = parser.parse_args()

    if args.mode == "sample":
        run_sample_analysis()
    else:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n\nAnalysis interrupted by user.")
        except Exception as e:
            print(f"\nError during analysis: {e}")
            sys.exit(1)

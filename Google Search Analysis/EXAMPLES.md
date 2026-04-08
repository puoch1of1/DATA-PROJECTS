# Google Search Trends Analysis - Sample Usage Examples

This file contains practical examples for common analysis tasks.

## Example 1: Trending Searches Dashboard

```python
from trend_analyzer import GoogleTrendAnalyzer

# Initialize analyzer
analyzer = GoogleTrendAnalyzer()

# Get trending searches in multiple countries
countries = ["US", "GB", "IN", "CA", "AU"]

for country in countries:
    print(f"\n=== Top 10 Trends in {country} ===")
    trending = analyzer.get_trending_searches(country)
    
    for item in trending[:10]:
        print(f"  {item['rank']}. {item['query']}")
```

## Example 2: Deep Keyword Analysis

```python
# Analyze a specific keyword in detail
keyword = "artificial intelligence"

# Get detailed metrics
metrics = analyzer.calculate_trend_metrics(keyword, timeframe="today 12-m")

print(f"Keyword: {keyword}")
print(f"Average Interest: {metrics.average_interest:.2f}")
print(f"Peak Interest: {metrics.peak_interest}")
print(f"Peak Date: {metrics.peak_date}")
print(f"Trend Direction: {metrics.trend_direction}")
print(f"Volatility: {metrics.volatility:.2f}")

# Get related searches
related = analyzer.get_related_queries(keyword)

print(f"\nTop Related Searches:")
for idx, row in related["top"].head(5).iterrows():
    print(f"  • {row['query']}")

print(f"\nRising Related Searches:")
for idx, row in related["rising"].head(5).iterrows():
    print(f"  • {row['query']} (+{row['value']}%)")
```

## Example 3: Keyword Competition Analysis

```python
# Analyze market competition by comparing similar keywords
competitors = ["ChatGPT", "Google Bard", "Claude"]

# Get comparison statistics
print("Competitor Keyword Analysis:")
stats = analyzer.get_keyword_comparison_stats(competitors, timeframe="today 3-m")
print(stats)

# Visualize trends
from visualizer import TrendVisualizer

viz = TrendVisualizer()
interest_data = analyzer.get_interest_over_time(competitors)
viz.plot_interest_over_time(interest_data, title="Chatbot Comparison")
```

## Example 4: Seasonal Trend Analysis

```python
# Analyze seasonal patterns for holiday shopping
keyword = "holiday gifts"

seasonal = analyzer.get_seasonal_trends(keyword)

print(f"Seasonal Trends for '{keyword}':")
for month, interest in seasonal.items():
    bar = "█" * int(interest / 5)
    print(f"  {month:12s}: {bar} {interest:.1f}")

# For planning: identify peak months for content/ads
peak_month = max(seasonal, key=seasonal.get)
print(f"\nBest month for promotion: {peak_month}")
```

## Example 5: Regional Market Research

```python
# Analyze where your keyword is most searched
keyword = "sustainable fashion"

# Get regional distribution
regional_data = analyzer.get_interest_by_region([keyword], resolution="country")

print(f"Regional Interest for '{keyword}':")
for idx, (region, interest) in enumerate(regional_data.head(10).items(), 1):
    print(f"  {idx}. {region}: {int(interest)}/100")

# Visualize
viz = TrendVisualizer()
viz.plot_interest_by_region(regional_data, top_n=15, title=f"{keyword} by Region")
```

## Example 6: Emerging Trend Detection

```python
# Monitor keywords for emerging trends (increasing interest)
keywords_to_monitor = [
    "machine learning",
    "quantum computing", 
    "edge computing",
    "zero knowledge proofs"
]

print("Emerging Trend Analysis:")
for keyword in keywords_to_monitor:
    metrics = analyzer.calculate_trend_metrics(keyword)
    
    status = "🔥" if metrics.trend_direction == "increasing" else "📉" if metrics.trend_direction == "decreasing" else "➡️"
    
    print(f"{status} {keyword}")
    print(f"   Average: {metrics.average_interest:.1f}, Trend: {metrics.trend_direction}, Peak: {metrics.peak_interest}")
```

## Example 7: Content Timing Strategy

```python
# Determine best time to publish content
keyword = "budget meal prep"

# Get 3-month trend with high granularity
interest_data = analyzer.get_interest_over_time([keyword], timeframe="today 3-m")

# Find peaks
peaks = interest_data.nlargest(3, keyword)

print(f"Best times to publish content about '{keyword}':")
for date, interest in peaks.iterrows():
    print(f"  • {date.strftime('%B %d, %Y')}: Interest level {int(interest[keyword])}")
```

## Example 8: Batch Analysis and Export

```python
import pandas as pd
import time

# Analyze multiple keyword groups
keyword_groups = [
    ["python", "javascript", "java"],
    ["machine learning", "deep learning", "neural networks"],
    ["cloud computing", "docker", "kubernetes"]
]

results = []

for idx, keywords in enumerate(keyword_groups):
    print(f"Analyzing group {idx+1}...")
    
    # Get comparison
    stats = analyzer.get_keyword_comparison_stats(keywords)
    results.append(stats)
    
    # Respect rate limits
    time.sleep(2)

# Combine results
all_stats = pd.concat(results, ignore_index=True)

# Export
all_stats.to_csv("data/batch_analysis.csv", index=False)
print("Analysis complete! Exported to batch_analysis.csv")
```

## Example 9: Heatmap Visualization

```python
# Create comparison heatmap for multiple keywords over time
keywords = ["python", "go", "rust", "julia"]

# Get data
interest_data = analyzer.get_interest_over_time(keywords, timeframe="today 12-m")

# Create heatmap
viz = TrendVisualizer()
viz.plot_comparison_heatmap(
    interest_data,
    title="Programming Languages Trend Heatmap",
    save_path="reports/lang_heatmap.png"
)
```

## Example 10: Complete Analysis Report

```python
# Generate comprehensive report for a keyword
def generate_report(keyword):
    print(f"\n{'='*60}")
    print(f"COMPLETE ANALYSIS: {keyword.upper()}")
    print(f"{'='*60}\n")
    
    # Metrics
    metrics = analyzer.calculate_trend_metrics(keyword)
    print("TREND METRICS:")
    print(f"  Average Interest:  {metrics.average_interest:.2f}")
    print(f"  Peak Interest:     {metrics.peak_interest}")
    print(f"  Peak Date:         {metrics.peak_date}")
    print(f"  Trend Direction:   {metrics.trend_direction.upper()}")
    print(f"  Volatility:        {metrics.volatility:.2f}\n")
    
    # Geographic
    regional_data = analyzer.get_interest_by_region([keyword], resolution="country")
    print("TOP REGIONS:")
    for region, interest in regional_data.head(5).items():
        print(f"  {region:20s}: {int(interest)}")
    print()
    
    # Seasonal
    seasonal = analyzer.get_seasonal_trends(keyword)
    print("SEASONAL PATTERNS:")
    peak_month = max(seasonal, key=seasonal.get)
    print(f"  Peak Month: {peak_month}")
    print(f"  Peak Interest: {seasonal[peak_month]:.1f}\n")
    
    # Related
    related = analyzer.get_related_queries(keyword)
    print("TOP RELATED QUERIES:")
    for idx, row in related["top"].head(3).iterrows():
        print(f"  • {row['query']}")
    
    print(f"\n{'='*60}\n")

# Run report
generate_report("machine learning")
```

---

## Tips for Analysis

1. **Compare fairly**: Use same timeframe for all keywords
2. **Understand normalization**: Values are 0-100, not absolute searches
3. **Respect rate limits**: Add delays between API calls
4. **Error handling**: Network timeouts are common, implement retry logic
5. **Cache results**: Save data to avoid repeated API calls

For more examples and advanced usage, see README.md and main.py

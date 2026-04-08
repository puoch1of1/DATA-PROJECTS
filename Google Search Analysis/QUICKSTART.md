# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Interactive CLI
```bash
python main.py
```

### 3. Or Launch Web Dashboard
```bash
streamlit run app.py
```

---

## Common Tasks

### View Trending Searches
```python
from trend_analyzer import GoogleTrendAnalyzer

analyzer = GoogleTrendAnalyzer()
trending = analyzer.get_trending_searches(country="US")

for item in trending[:10]:
    print(f"{item['rank']}. {item['query']}")
```

### Analyze a Keyword
```python
# Get metrics
metrics = analyzer.calculate_trend_metrics("artificial intelligence")

print(f"Average Interest: {metrics.average_interest}")
print(f"Peak Interest: {metrics.peak_interest}")
print(f"Trend: {metrics.trend_direction}")
print(f"Peak Date: {metrics.peak_date}")
```

### Compare Keywords
```python
# Get comparison statistics
keywords = ["python", "java", "javascript"]
stats = analyzer.get_keyword_comparison_stats(keywords)
print(stats)

# Visualize
interest_data = analyzer.get_interest_over_time(keywords)
from visualizer import TrendVisualizer
viz = TrendVisualizer()
viz.plot_interest_over_time(interest_data)
```

### Analyze by Region
```python
# Get regional distribution
regional_data = analyzer.get_interest_by_region(["machine learning"])
print(regional_data)

# Visualize
viz.plot_interest_by_region(regional_data, top_n=15)
```

### Find Related Queries
```python
# Get related searches
related = analyzer.get_related_queries("data science")

# Top related
print("Top Related Queries:")
for idx, row in related["top"].head(5).iterrows():
    print(f"  • {row['query']}")

# Rising related
print("\nRising Related Queries:")
for idx, row in related["rising"].head(5).iterrows():
    print(f"  • {row['query']} (↑{row['value']}%)")
```

### Detect Seasonal Patterns
```python
# Get monthly patterns
seasonal = analyzer.get_seasonal_trends("christmas")

# Visualize
viz.plot_seasonal_trends(seasonal)
```

### Export Data
```python
# Get data
interest_data = analyzer.get_interest_over_time(["AI", "ML"], timeframe="today 12-m")

# Export to CSV
analyzer.export_to_csv(interest_data, "trends.csv")

# Export to JSON
analyzer.export_to_json(interest_data, "trends.json")
```

---

## Tips

- **Max 5 keywords** for fair comparison
- **Use timeframe parameter** for context:
  - `"today 1-m"` - Past month (default)
  - `"today 3-m"` - Past 3 months
  - `"today 12-m"` - Past year
  - `"today 5-y"` - Past 5 years
- **Handle errors**: Pytrends respects Google's rate limits
- **Rate limiting**: Add `time.sleep(2)` between requests if making many calls

---

## Dashboard Features

When running `streamlit run app.py`:

1. **Trending Searches** - Multi-country trend explorer
2. **Keyword Analysis** - Deep metrics + related queries
3. **Compare Keywords** - Side-by-side analysis
4. **Regional Analysis** - Geographic patterns
5. **Seasonal Trends** - Monthly patterns

---

For more information, see README.md

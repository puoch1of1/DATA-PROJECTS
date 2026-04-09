# Google Search Analysis with Python

Comprehensive tool for analyzing and visualizing Google search trends using Pytrends. Discover what people are searching for, identify emerging trends, and understand regional search patterns.

## Dataset Project: GOOGL Historical Stock Analysis

This repository now includes a complete, dataset-driven stock analysis pipeline using `data/GOOGL.csv` (daily OHLCV data).

### What This Project Produces

- Cleaned and enriched stock dataset with engineered features
- KPI report in JSON format for downstream applications
- Text summary report for quick business interpretation
- Visualization set for trend, return distribution, and drawdown

### Engineered Features

- Daily return and log return
- Moving averages (20-day, 50-day, 200-day)
- 30-day rolling annualized volatility
- Cumulative return
- Running peak and drawdown
- 30-day volume z-score (activity anomaly signal)

### KPI Metrics

- Total return (%)
- CAGR (%)
- Annualized volatility (%)
- Maximum drawdown (%)
- Best and worst daily return (%)
- Average and median daily volume
- SMA-based trend signal (`bullish`, `bearish`, `mixed`)

### Run the GOOGL Project

```bash
python run_googl_stock_project.py
```

Optional custom input path:

```bash
python run_googl_stock_project.py --input data/GOOGL.csv
```

### Output Files

- `data/googl_enriched.csv`
- `reports/googl_kpis.json`
- `reports/googl_analysis_summary.txt`
- `reports/googl_price_trend.png`
- `reports/googl_returns_distribution.png`
- `reports/googl_drawdown.png`

## Overview

Google handles over billions of searches every day and trillions of searches each year. This project provides powerful Python tools to access, analyze, and visualize Google Trends data. Use it to:

- **Track trending searches** by country and region
- **Compare keywords** to understand relative search interest
- **Identify patterns** in search behavior over time
- **Analyze seasonality** in search trends
- **Discover related queries** and emerging topics
- **Generate insights** with interactive visualizations

## Key Features

### 1. **Trending Searches Analysis**
- View current trending searches by country
- Multi-country trend comparison (US, UK, India, Canada, Australia, etc.)
- Real-time trending data extraction
- Structured ranking and metadata

### 2. **Keyword Analysis**
- Calculate detailed trend metrics for any keyword:
  - Average interest over time
  - Peak interest level and date
  - Trend direction (increasing/decreasing/stable)
  - Volatility measurement
  - Search count and data density
- Get related search queries (top and rising)
- Discover keyword suggestions from Google's autocomplete

### 3. **Keyword Comparison**
- Compare up to 5 keywords simultaneously
- Normalized interest levels for fair comparison
- Identify which keywords are gaining momentum
- Visualize competition between search terms

### 4. **Regional Analysis**
- Analyze search interest by geographic region
- Compare trends across countries
- Identify regional hotspots for specific keywords
- Export regional data for further analysis

### 5. **Seasonal Trend Detection**
- Identify seasonal patterns in search behavior
- Understand monthly interest variations
- Plan content for seasonal demand peaks
- Recognize recurring trends throughout the year

### 6. **Advanced Visualizations**
- Interactive Plotly charts for exploration
- Time-series trend visualization
- Heatmaps for multi-keyword comparison
- Regional bar charts and maps
- Seasonal pattern graphs
- Trend metrics dashboard

### 7. **Data Export**
- Export to CSV for spreadsheet analysis
- Export to JSON for programmatic use
- Save visualizations as high-quality PNG files
- Generate text reports with summary statistics

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Client** | Pytrends 4.10.0 | Unofficial Google Trends API wrapper |
| **Data Processing** | Pandas 2.1.4 | Data manipulation and analysis |
| **Visualization** | Plotly 5.18.0 | Interactive web-based charts |
| **Static Charts** | Matplotlib 3.7.4 | High-quality static visualizations |
| **Web Dashboard** | Streamlit 1.44.1 | Interactive web interface |
| **Styling** | Seaborn 0.13.1 | Statistical data visualization |

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. **Navigate to project directory:**
```bash
cd "Google Search Analysis"
```

2. **Create virtual environment (optional but recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface (Interactive)

Run the interactive analysis menu:

```bash
python main.py
```

**Available Options:**
1. **View Trending Searches** - See current top searches in multiple countries
2. **Analyze Single Keyword** - Deep dive into a specific keyword's trend
3. **Compare Keywords** - Compare search interest across multiple terms
4. **Regional Analysis** - Analyze search patterns by geography
5. **Keyword Suggestions** - Get Google's autocomplete suggestions
6. **Exit** - Close the application

**Example CLI Session:**
```
GOOGLE SEARCH TRENDS ANALYZER
==============================

Select an analysis option:
  1. View trending searches by country
  2. Analyze a single keyword
  3. Compare multiple keywords
  4. Analyze by region
  5. Get keyword suggestions
  6. Exit

Enter your choice (1-6): 2
Enter keyword to analyze: artificial intelligence

... [Analysis Results] ...

Keyword Metrics:
  Average Interest:  62.35
  Peak Interest:     100
  Peak Date:         2024-11-15
  Trend Direction:   INCREASING
  Volatility (Std):  18.47
  Data Points:       52

Seasonal Trends (Average Interest by Month):
  January   : ████████░░░░░░░░░░░░░░ 45.3
  February  : █████████░░░░░░░░░░░░░░ 48.2
  March     : ██████████████░░░░░░░░░░ 62.1
  ...
```

### Sample Analysis Script

Run a pre-configured analysis with technology keywords:

```bash
python main.py --mode sample
```

This generates:
- CSV and JSON data exports
- PNG visualization files
- Comparative analysis charts

### Web Dashboard (Streamlit)

Launch the interactive web dashboard:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

**Dashboard Features:**
- 🔍 **Trending Searches**: Browse top searches by country
- 📊 **Keyword Analysis**: Deep analysis with metrics and related queries
- 📈 **Compare Keywords**: Side-by-side keyword comparison with charts
- 🗺️ **Regional Analysis**: Geographic distribution of searches
- 📅 **Seasonal Trends**: Monthly pattern analysis
- 📁 **Data Export**: Download analysis results

**Dashboard Sections:**
- Sidebar controls for filtering and timeframe selection
- Interactive charts with hover tooltips
- Real-time metric calculations
- Export options (CSV/JSON)

## Project Structure

```
Google Search Analysis/
├── requirements.txt              # Python dependencies
├── main.py                       # Interactive CLI interface
├── app.py                        # Streamlit web dashboard
├── trend_analyzer.py             # Core analysis module
├── visualizer.py                 # Visualization & reporting
├── data/                         # Data export directory
│   ├── tech_trends_data.csv
│   └── tech_trends_data.json
└── reports/                      # Reports & visualizations
    ├── tech_trends_chart.png
    ├── tech_trends_heatmap.png
    └── trend_report.txt
```

## API Reference

### GoogleTrendAnalyzer Class

**Core Methods:**

```python
from trend_analyzer import GoogleTrendAnalyzer

analyzer = GoogleTrendAnalyzer(language="en", timeout=10)

# Get trending searches
trending = analyzer.get_trending_searches(country="US")

# Analyze single keyword
interest_data = analyzer.get_interest_over_time(
    keywords=["AI", "ML"],
    timeframe="today 3-m"
)

# Compare keywords
comparison = analyzer.compare_keywords(
    keywords=["python", "java", "javascript"]
)

# Regional analysis
regional = analyzer.get_interest_by_region(
    keywords=["machine learning"],
    resolution="country"
)

# Get metrics
metrics = analyzer.calculate_trend_metrics(
    keyword="data science",
    timeframe="today 12-m"
)

# Seasonal patterns
seasonal = analyzer.get_seasonal_trends("christmas")

# Export data
analyzer.export_to_csv(interest_data, "trends.csv")
analyzer.export_to_json(interest_data, "trends.json")
```

### TrendVisualizer Class

```python
from visualizer import TrendVisualizer

viz = TrendVisualizer()

# Line chart
viz.plot_interest_over_time(
    data=interest_data,
    title="Google Trends",
    save_path="trend.png"
)

# Heatmap
viz.plot_comparison_heatmap(data, save_path="heatmap.png")

# Metrics dashboard
viz.plot_trend_metrics(metrics_df)

# Seasonal patterns
viz.plot_seasonal_trends(seasonal_data)

# Interactive Plotly charts
fig = viz.create_interactive_comparison(interest_data)
fig.show()
```

## Common Use Cases

### 1. Marketing Research
```python
# Analyze trending keywords in your industry
keywords = ["sustainable fashion", "eco-friendly", "green business"]
analyzer.get_keyword_comparison_stats(keywords, timeframe="today 12-m")
```

### 2. Content Planning
```python
# Understand seasonal demand
seasonal = analyzer.get_seasonal_trends("holiday gifts")
# Plan content around peak search times
```

### 3. SEO Optimization
```python
# Find related keywords for your content
related = analyzer.get_related_queries("machine learning tutorial")
# Target rising queries for competitive advantage
```

### 4. Market Analysis
```python
# Track emerging trends
metrics = analyzer.calculate_trend_metrics("blockchain", timeframe="today 5-y")
# Monitor increasing/decreasing trends
```

### 5. Competitive Intelligence
```python
# Compare competitor keywords
competitors = ["Competitor A", "Competitor B", "Your Brand"]
analyzer.get_keyword_comparison_stats(competitors)
```

## Timeline Options

Pytrends supports various timeframe parameters:

| Timeframe | Parameter | Use Case |
|-----------|-----------|----------|
| **Past Hour** | `now 1-H` | Real-time trending |
| **Past Day** | `now 1-d` | Daily viral trends |
| **Past Week** | `now 7-d` | Weekly patterns |
| **Past Month** | `today 1-m` | Monthly trends |
| **Past 3 Months** | `today 3-m` | Quarterly analysis |
| **Past Year** | `today 12-m` | Yearly patterns |
| **Past 5 Years** | `today 5-y` | Long-term trends |
| **Custom Range** | `2020-01-01 2024-01-01` | Specific date range |

## Output Examples

### Trend Metrics
```
Keyword Metrics:
  Average Interest:  58.42
  Peak Interest:     100
  Peak Date:         2024-11-20
  Trend Direction:   INCREASING
  Volatility:        22.15
  Data Points:       52
```

### Regional Top 5
```
  1. India               : ███████████████████ 95
  2. United States       : ███████████████░░░░░ 78
  3. United Kingdom      : ███████████░░░░░░░░░ 65
  4. Canada              : ███████████░░░░░░░░░ 64
  5. Australia           : ██████████░░░░░░░░░░ 62
```

### Seasonal Pattern
```
January   : ████ 28.5
February  : █████ 35.2
March     : ██████ 42.1
...
December  : ███████████ 78.9
```

## Tips & Best Practices

1. **Rate Limiting**: Pytrends respects Google's rate limits. Add delays between requests if needed.
2. **Max Keywords**: Compare up to 5 keywords simultaneously for accurate normalization.
3. **Timeframes**: Longer timeframes provide trend context; shorter timeframes show latest trends.
4. **Regions**: Use specific countries/regions for targeted analysis.
5. **Caching**: Save results to avoid repeated API calls.
6. **Error Handling**: Network issues are common; implement retry logic.

## Troubleshooting

### Issue: "Maximum 5 keywords allowed"
**Solution**: Limit your comparison to 5 keywords maximum

### Issue: Empty results for certain keywords
**Solution**: Try common spelling variations or more generic terms; very new or region-specific keywords may have limited data

### Issue: Rate limit errors
**Solution**: Add delays between requests using `time.sleep()`

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Advanced Features

### Custom Timeframe Analysis
```python
# Analyze between specific dates
from datetime import datetime, timedelta

start = "2023-01-01"
end = "2023-12-31"
interest_data = analyzer.get_interest_over_time(
    ["keyword"],
    timeframe=f"{start} {end}"
)
```

### Batch Processing
```python
# Analyze multiple keywords efficiently
import time

keywords_list = [["python", "java", "go"], ["rust", "swift", "kotlin"]]
for batch in keywords_list:
    stats = analyzer.get_keyword_comparison_stats(batch)
    time.sleep(2)  # Respect rate limits
```

### Custom Visualizations
Extend the `TrendVisualizer` class with your own chart types:
```python
class CustomVisualizer(TrendVisualizer):
    def plot_custom_chart(self, data):
        # Your custom visualization logic
        pass
```

## Future Enhancements

- [ ] Machine learning for trend prediction
- [ ] Anomaly detection in search patterns
- [ ] Natural language processing for keyword analysis
- [ ] Integration with Google Analytics
- [ ] Real-time alert system for trending topics
- [ ] Batch API for processing hundreds of keywords
- [ ] Database persistence for historical analysis
- [ ] Multi-language support
- [ ] Mobile app interface

## Limitations

- **Unofficial API**: Pytrends is unofficial and may break with Google changes
- **Normalized Data**: Google provides 0-100 normalized values, not raw search volumes
- **Rate Limiting**: Subject to Google's rate limits
- **Geographic Coverage**: Not all countries/regions available
- **Historical Data**: Limited to ~10+ years of historical data

## Contributing

Contributions welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Improve documentation
- Add new analysis methods
- Optimize performance

## References

- [Pytrends Documentation](https://github.com/GeneralMills/pytrends)
- [Google Trends](https://trends.google.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python)

## License

This project is open source and available for educational and research purposes.

## Disclaimer

This tool uses an unofficial Pytrends API. Google may change or restrict access at any time. Use responsibly and respect Google's Terms of Service.

---

**Last Updated**: July 23, 2025 | **Version**: 1.0.0

Created for comprehensive Google search trend analysis and visualization.

# Configuration Guide

This guide shows how to customize and configure the Google Trends Analysis tool for your specific needs.

## 1. Language Configuration

### Change Analyzer Language
```python
from trend_analyzer import GoogleTrendAnalyzer

# English (default)
analyzer_en = GoogleTrendAnalyzer(language="en")

# German
analyzer_de = GoogleTrendAnalyzer(language="de")

# Spanish
analyzer_es = GoogleTrendAnalyzer(language="es")

# Portuguese
analyzer_pt = GoogleTrendAnalyzer(language="pt")
```

## 2. Timeframe Settings

### Common Timeframe Examples
```python
analyzer = GoogleTrendAnalyzer()

# Recent trends (past 3 days)
recent = analyzer.get_interest_over_time(
    ["keyword"],
    timeframe="now 3-d"
)

# Quarterly analysis
quarterly = analyzer.get_interest_over_time(
    ["keyword"],
    timeframe="today 3-m"
)

# Year-over-year
yearly = analyzer.get_interest_over_time(
    ["keyword"],
    timeframe="today 12-m"
)

# Custom date range
custom = analyzer.get_interest_over_time(
    ["keyword"],
    timeframe="2023-01-01 2024-01-01"
)
```

## 3. Regional Analysis

### Different Resolution Levels
```python
# Country-level (broadest)
country_data = analyzer.get_interest_by_region(
    ["keyword"],
    resolution="country"
)

# Region/State-level (medium)
region_data = analyzer.get_interest_by_region(
    ["keyword"],
    resolution="region"
)

# Metro/City-level (finest)
metro_data = analyzer.get_interest_by_region(
    ["keyword"],
    resolution="metro"
)
```

## 4. Visualization Customization

### Custom Matplotlib Style
```python
from visualizer import TrendVisualizer

# Different styles
viz_dark = TrendVisualizer(style="seaborn-v0_8-darkgrid")
viz_light = TrendVisualizer(style="seaborn-v0_8-whitegrid")
viz_default = TrendVisualizer(style="default")

# Plot with custom settings
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(16, 8))
# Your custom plotting code
```

### Custom Plotly Styling
```python
import plotly.graph_objects as go

# Create custom figure
fig = viz.create_interactive_comparison(interest_data)

# Modify layout
fig.update_layout(
    template="plotly_dark",
    font=dict(family="Arial", size=12),
    height=600,
    showlegend=True
)

fig.show()
```

## 5. Data Processing

### Post-Processing Trends
```python
import pandas as pd

# Get data
data = analyzer.get_interest_over_time(["keyword"])

# Resample to weekly
weekly = data.resample("W").mean()

# Calculate moving average
ma_7 = data.rolling(window=7).mean()
ma_30 = data.rolling(window=30).mean()

# Normalize data
normalized = (data - data.min()) / (data.max() - data.min())

# Year-over-year comparison
data['year'] = data.index.year
yoy = data.groupby('year').apply(lambda x: x.mean())
```

## 6. Batch Processing Configuration

### Process Multiple Keyword Groups
```python
import time

# Configuration
KEYWORDS_GROUPS = [
    ["python", "java", "cpp"],
    ["machine learning", "deep learning", "ai"],
    ["cloud", "kubernetes", "docker"]
]

DELAY_BETWEEN_REQUESTS = 2  # seconds
DELAY_BETWEEN_GROUPS = 5    # seconds
EXPORT_FORMAT = "csv"       # csv or json

# Process
for idx, group in enumerate(KEYWORDS_GROUPS):
    print(f"Processing group {idx+1}/{len(KEYWORDS_GROUPS)}")
    
    try:
        stats = analyzer.get_keyword_comparison_stats(group)
        
        # Export
        if EXPORT_FORMAT == "csv":
            stats.to_csv(f"data/group_{idx}.csv", index=False)
        else:
            stats.to_json(f"data/group_{idx}.json", orient="table")
        
        time.sleep(DELAY_BETWEEN_GROUPS)
        
    except Exception as e:
        print(f"Error processing group {idx}: {e}")
        time.sleep(DELAY_BETWEEN_REQUESTS)
```

## 7. Error Handling Configuration

### Robust Error Management
```python
import time
from contextlib import retry

def safe_analysis(keyword, max_retries=3):
    """Analyze keyword with retry logic."""
    
    for attempt in range(max_retries):
        try:
            metrics = analyzer.calculate_trend_metrics(keyword)
            return metrics
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt+1} failed: {e}")
                wait_time = (attempt + 1) * 2  # exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
                return None

# Usage
metrics = safe_analysis("artificial intelligence")
```

## 8. Output Configuration

### Configure Export Behavior
```python
# Directory settings
import os

DATA_DIR = "data"
REPORT_DIR = "reports"
CHART_DIR = "reports/charts"

# Create directories if needed
for dir_path in [DATA_DIR, REPORT_DIR, CHART_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Export with timestamps
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{DATA_DIR}/trends_{timestamp}.csv"

analyzer.export_to_csv(data, filename)

# Organize by keyword
keyword_dir = f"{DATA_DIR}/{keyword}"
os.makedirs(keyword_dir, exist_ok=True)
analyzer.export_to_csv(data, f"{keyword_dir}/trends.csv")
```

## 9. Logging Configuration

### Set Up Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trends_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log analysis steps
logger.info(f"Starting analysis for keywords: {keywords}")
try:
    results = analyzer.get_keyword_comparison_stats(keywords)
    logger.info(f"Successfully analyzed {len(results)} keywords")
except Exception as e:
    logger.error(f"Analysis failed: {e}")
```

## 10. Performance Optimization

### Configuration for Performance
```python
# Reduce API calls with caching
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_analysis(keyword, timeframe="today 1-m"):
    """Cached trend analysis to avoid duplicate API calls."""
    return analyzer.calculate_trend_metrics(keyword, timeframe)

# Batch operations with delays
import concurrent.futures

def analyze_keywords_parallel(keywords, max_workers=3):
    """Parallel analysis with rate limiting."""
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(cached_analysis, kw): kw 
            for kw in keywords
        }
        
        for future in concurrent.futures.as_completed(futures):
            keyword = futures[future]
            try:
                results[keyword] = future.result()
            except Exception as e:
                print(f"Error analyzing {keyword}: {e}")
    
    return results
```

## 11. Dashboard Configuration (Streamlit)

### Custom Dashboard Layout
```python
# In app.py, configure Streamlit settings:

st.set_page_config(
    page_title="My Trends Dashboard",
    page_icon="📊",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)

# Custom colors
primary_color = "#1f77b4"
secondary_color = "#ff7f0e"
background_color = "#f0f2f6"

# Customize session state
st.session_state.analysis_history = []
st.session_state.saved_keywords = []
```

## 12. Environment Variables

### Configuration via Environment
```python
import os

# Get from environment or use defaults
PYTRENDS_LANGUAGE = os.getenv("PYTRENDS_LANGUAGE", "en")
PYTRENDS_TIMEOUT = int(os.getenv("PYTRENDS_TIMEOUT", "10"))
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "csv")
MAX_KEYWORDS = int(os.getenv("MAX_KEYWORDS", "5"))

# Create .env file
# PYTRENDS_LANGUAGE=en
# PYTRENDS_TIMEOUT=10
# EXPORT_FORMAT=csv
# MAX_KEYWORDS=5

# Usage
analyzer = GoogleTrendAnalyzer(
    language=PYTRENDS_LANGUAGE,
    timeout=PYTRENDS_TIMEOUT
)
```

## 13. Advanced Filtering

### Custom Data Filtering
```python
import pandas as pd

# Get data
data = analyzer.get_interest_over_time(["keyword"], timeframe="today 12-m")

# Filter by interest threshold
high_interest = data[data["keyword"] > 50]

# Filter by date range
start_date = "2024-01-01"
end_date = "2024-06-01"
filtered = data[start_date:end_date]

# Remove weekends
weekdays_only = data[data.index.dayofweek < 5]

# Aggregate by month
monthly = data.resample("M").mean()
```

## 14. Report Generation

### Custom Report Templates
```python
def generate_custom_report(metrics, related_queries, filename="report.txt"):
    """Generate customized analysis report."""
    
    report = f"""
    CUSTOM ANALYSIS REPORT
    Generated: {pd.Timestamp.now()}
    
    ====================
    KEYWORD METRICS
    ====================
    Average Interest: {metrics.average_interest:.2f}
    Peak Interest: {metrics.peak_interest}
    Trend: {metrics.trend_direction}
    
    ====================
    RELATED QUERIES
    ====================
    """
    
    if "top" in related_queries:
        report += "\n\nTop Queries:\n"
        for idx, row in related_queries["top"].head(10).iterrows():
            report += f"  • {row['query']}\n"
    
    # Write report
    with open(filename, "w") as f:
        f.write(report)
    
    print(f"Report saved to {filename}")

# Usage
metrics = analyzer.calculate_trend_metrics("keyword")
related = analyzer.get_related_queries("keyword")
generate_custom_report(metrics, related)
```

---

## Configuration Checklist

- [ ] Set appropriate language
- [ ] Configure timeframe for your analysis
- [ ] Set regional resolution level
- [ ] Choose visualization style
- [ ] Configure export format
- [ ] Set up error handling
- [ ] Configure logging
- [ ] Set up directory structure
- [ ] Configure performance settings
- [ ] Set batch processing parameters
- [ ] Configure rate limiting delays
- [ ] Set up environment variables

---

## Performance Tips

1. **Cache results** to avoid duplicate API calls
2. **Use delays** between requests (1-2 seconds)
3. **Batch analyze** to reduce overhead
4. **Resample data** for faster visualization
5. **Export data** to avoid re-fetching
6. **Use smaller** timeframes for recent data
7. **Limit keywords** to 5 or fewer per request

For more help, see README.md and EXAMPLES.md

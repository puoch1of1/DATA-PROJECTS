# YouTube Channel Data Analysis

A comprehensive data analysis project examining YouTube channel performance, upload patterns, and audience engagement across different content categories.

## 📊 Project Overview

This project analyzes YouTube video statistics and comments data to answer three critical questions:

1. **Which channels/categories grow fastest?**
2. **Does upload frequency affect views?**
3. **Which category gets the most engagement?**

## 🗂️ Project Structure

```
YOUTUBE/
│
├── data/                          # Raw and processed data files
│   ├── videos-stats.csv          # Video statistics dataset
│   └── comments.csv              # Comments and sentiment data
│
├── notebooks/                     # Jupyter notebooks for analysis
│   └── analysis.ipynb            # Main analysis notebook
│
├── src/                          # Python source code
│   ├── cleaning.py               # Data cleaning & preprocessing
│   └── analysis.py               # Analysis functions
│
├── visuals/                      # Generated visualizations
│   ├── channel_growth.png
│   ├── upload_frequency_vs_views.png
│   ├── category_engagement_heatmap.png
│   └── comprehensive_dashboard.png
│
└── README.md                     # Project documentation
```

## 🔍 Analysis Questions & Methodology

### 1. Channel Growth Analysis
- **Metric**: Growth Score (composite metric combining views, likes, comments, engagement)
- **Method**: Aggregated performance metrics by category
- **Output**: Ranked list of fastest-growing channels/categories

### 2. Upload Frequency vs Views
- **Metric**: Correlation coefficient between upload frequency and average views
- **Method**: Time-series analysis by category with correlation analysis
- **Output**: Category-specific correlation values and insights

### 3. Category Engagement
- **Metrics**: 
  - Engagement Rate: (Likes + Comments) / Views × 100
  - Like Rate: Likes / Views × 100
  - Comment Rate: Comments / Views × 100
- **Method**: Aggregated metrics with weighted engagement scoring
- **Output**: Ranked categories by engagement performance

## 📦 Dataset Description

### Videos Dataset
- **Title**: Video title
- **Video ID**: Unique identifier
- **Published At**: Publication date/time
- **Keyword**: Content category/tag
- **Likes**: Number of likes
- **Comments**: Number of comments
- **Views**: Number of views

### Comments Dataset
- **Video ID**: Links to video
- **Comment**: Comment text
- **Likes**: Comment likes
- **Sentiment**: Sentiment score (0=Negative, 1=Neutral, 2=Positive)

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
pandas
numpy
matplotlib
seaborn
jupyter
```

### Installation

1. Clone or download this project

2. Install required packages:
```bash
pip install pandas numpy matplotlib seaborn jupyter
```

3. Navigate to the project directory:
```bash
cd YOUTUBE
```

### Running the Analysis

#### Option 1: Jupyter Notebook (Recommended)
```bash
# Launch Jupyter Notebook
jupyter notebook

# Open notebooks/analysis.ipynb
```

#### Option 2: Python Scripts
```bash
# Run data cleaning
python src/cleaning.py

# Run analysis
python src/analysis.py
```

## 📈 Key Features

### Data Cleaning (`cleaning.py`)
- Handles missing values
- Converts data types (dates, numerics)
- Creates derived metrics (engagement rates)
- Merges multiple datasets
- Exports cleaned data

### Analysis Functions (`analysis.py`)
- `analyze_channel_growth()`: Channel growth metrics
- `analyze_upload_frequency_vs_views()`: Frequency correlation analysis
- `analyze_category_engagement()`: Engagement scoring
- `get_top_performing_videos()`: Top performers identification
- `create_summary_statistics()`: Comprehensive statistics

### Visualizations
- Horizontal bar charts for channel growth
- Scatter plots for upload frequency analysis
- Heatmaps for engagement metrics
- Comprehensive dashboard with multiple subplots

## 📊 Sample Insights

*Note: Run the analysis notebook to generate insights from your specific dataset*

The analysis typically reveals:
- Which content categories attract the most viewers
- Whether posting more frequently increases average views
- Which categories generate the highest audience engagement
- Trends in video performance over time

## 🛠️ Customization

### Modify Analysis Parameters

Edit `src/analysis.py` to adjust:
- Growth score weightings
- Time period granularity
- Engagement score formula
- Number of top results

### Add New Visualizations

In `notebooks/analysis.ipynb`, add new cells with custom plots using:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Your custom visualization code
```

## 📝 Results & Output

All analysis results are saved to:
- **Cleaned Data**: `data/cleaned_youtube_data.csv`
- **Charts**: `visuals/` directory
- **Analysis Output**: Displayed in Jupyter notebook

## 🤝 Contributing

Feel free to fork this project and adapt it for your own YouTube data analysis needs. Potential enhancements:
- Integration with YouTube API for real-time data
- Sentiment analysis on comment text
- Predictive modeling for view forecasting
- A/B testing frameworks for content strategies

## 📄 License

This project is provided as-is for educational and analytical purposes.

## 📧 Contact

For questions or suggestions about this analysis, please open an issue in the repository.

---

**Last Updated**: March 2026

**Analysis Platform**: Python 3.8+ | Pandas | Matplotlib | Seaborn | Jupyter

**Status**: ✅ Complete & Ready to Run

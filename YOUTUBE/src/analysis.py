"""
Analysis Module for YouTube Channel Data
Contains functions to answer key business questions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


def bootstrap_mean_ci(series, n_boot=1000, ci=95, random_state=42):
    """
    Estimate a confidence interval for the mean using bootstrap resampling.

    Args:
        series: 1-D numeric data
        n_boot: Number of bootstrap iterations
        ci: Confidence level percentage
        random_state: Seed for reproducibility

    Returns:
        tuple: (mean, lower_bound, upper_bound)
    """
    values = pd.Series(series).dropna().astype(float).values
    if len(values) == 0:
        return np.nan, np.nan, np.nan

    rng = np.random.default_rng(random_state)
    sample_means = np.empty(n_boot)

    for i in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        sample_means[i] = sample.mean()

    alpha = (100 - ci) / 2
    lower = np.percentile(sample_means, alpha)
    upper = np.percentile(sample_means, 100 - alpha)
    return values.mean(), lower, upper


def permutation_test_correlation(x, y, n_perm=2000, random_state=42):
    """
    Compute a two-sided permutation-test p-value for Pearson correlation.

    Args:
        x: First numeric series
        y: Second numeric series
        n_perm: Number of permutations
        random_state: Seed for reproducibility

    Returns:
        tuple: (observed_corr, p_value)
    """
    x = pd.Series(x).astype(float)
    y = pd.Series(y).astype(float)
    valid = x.notna() & y.notna()
    x = x[valid].values
    y = y[valid].values

    if len(x) < 3:
        return np.nan, np.nan

    observed = np.corrcoef(x, y)[0, 1]
    rng = np.random.default_rng(random_state)

    extreme_count = 0
    for _ in range(n_perm):
        y_perm = rng.permutation(y)
        perm_corr = np.corrcoef(x, y_perm)[0, 1]
        if abs(perm_corr) >= abs(observed):
            extreme_count += 1

    p_value = (extreme_count + 1) / (n_perm + 1)
    return observed, p_value


def analyze_channel_growth(df):
    """
    Analyze which channels/categories grow fastest
    
    Args:
        df: Cleaned videos DataFrame with date information
    
    Returns:
        DataFrame: Channel growth metrics
    """
    # Calculate growth metrics per category
    growth_analysis = df.groupby('Keyword').agg({
        'Views': ['sum', 'mean', 'std'],
        'Likes': ['sum', 'mean'],
        'Comments': ['sum', 'mean'],
        'Title': 'count',
        'Engagement_Rate': 'mean'
    }).round(2)
    
    growth_analysis.columns = ['Total_Views', 'Avg_Views_Per_Video', 'Std_Views',
                                'Total_Likes', 'Avg_Likes',
                                'Total_Comments', 'Avg_Comments',
                                'Video_Count', 'Avg_Engagement_Rate']
    
    # Calculate growth rate (using total views as a proxy)
    growth_analysis['Growth_Score'] = (
        growth_analysis['Total_Views'] * 0.4 +
        growth_analysis['Total_Likes'] * 0.3 +
        growth_analysis['Total_Comments'] * 0.2 +
        growth_analysis['Avg_Engagement_Rate'] * 1000 * 0.1
    )
    
    growth_analysis = growth_analysis.sort_values('Growth_Score', ascending=False)
    
    return growth_analysis.reset_index()


def analyze_upload_frequency_vs_views(df):
    """
    Analyze relationship between upload frequency and views
    
    Args:
        df: Cleaned videos DataFrame with date information
    
    Returns:
        DataFrame: Upload frequency analysis
    """
    # Count videos per category per month/week
    df['Year_Month'] = df['Published At'].dt.to_period('M')
    
    # Calculate upload frequency
    upload_freq = df.groupby(['Keyword', 'Year_Month']).agg({
        'Title': 'count',
        'Views': 'mean',
        'Likes': 'mean',
        'Engagement_Rate': 'mean'
    }).reset_index()
    
    upload_freq.columns = ['Category', 'Period', 'Videos_Uploaded', 
                           'Avg_Views', 'Avg_Likes', 'Avg_Engagement']
    
    # Analyze correlation by category
    correlation_analysis = upload_freq.groupby('Category').apply(
        lambda x: pd.Series({
            'Avg_Upload_Frequency': x['Videos_Uploaded'].mean(),
            'Avg_Views': x['Avg_Views'].mean(),
            'Correlation_Freq_Views': x['Videos_Uploaded'].corr(x['Avg_Views']) if len(x) > 1 else np.nan
        })
    ).round(2)
    
    return correlation_analysis.reset_index(), upload_freq


def analyze_category_engagement(df, comments_df=None):
    """
    Analyze which category gets the most engagement
    
    Args:
        df: Cleaned videos DataFrame
        comments_df: Optional comments DataFrame for deeper analysis
    
    Returns:
        DataFrame: Category engagement metrics
    """
    # Aggregate engagement metrics by category
    engagement = df.groupby('Keyword').agg({
        'Views': ['sum', 'mean'],
        'Likes': ['sum', 'mean'],
        'Comments': ['sum', 'mean'],
        'Engagement_Rate': 'mean',
        'Like_Rate': 'mean',
        'Comment_Rate': 'mean',
        'Title': 'count'
    }).round(2)
    
    engagement.columns = ['Total_Views', 'Avg_Views',
                          'Total_Likes', 'Avg_Likes',
                          'Total_Comments', 'Avg_Comments',
                          'Avg_Engagement_Rate',
                          'Avg_Like_Rate',
                          'Avg_Comment_Rate',
                          'Video_Count']
    
    # Calculate overall engagement score
    engagement['Engagement_Score'] = (
        engagement['Avg_Engagement_Rate'] * 0.4 +
        engagement['Avg_Like_Rate'] * 0.3 +
        engagement['Avg_Comment_Rate'] * 0.3
    )
    
    engagement = engagement.sort_values('Engagement_Score', ascending=False)
    
    return engagement.reset_index()


def get_top_performing_videos(df, n=10, metric='Views'):
    """
    Get top N performing videos by specified metric
    
    Args:
        df: Cleaned videos DataFrame
        n: Number of top videos to return
        metric: Metric to sort by (Views, Likes, Comments, Engagement_Rate)
    
    Returns:
        DataFrame: Top performing videos
    """
    top_videos = df.nlargest(n, metric)[
        ['Title', 'Keyword', 'Published At', 'Views', 'Likes', 
         'Comments', 'Engagement_Rate']
    ]
    
    return top_videos


def analyze_sentiment_by_category(comments_df, videos_df):
    """
    Analyze sentiment distribution across categories
    
    Args:
        comments_df: Cleaned comments DataFrame
        videos_df: Cleaned videos DataFrame
    
    Returns:
        DataFrame: Sentiment analysis by category
    """
    # Merge to get category information
    merged = comments_df.merge(
        videos_df[['Video ID', 'Keyword']], 
        on='Video ID', 
        how='left'
    )
    
    # Aggregate sentiment by category
    sentiment_analysis = merged.groupby(['Keyword', 'Sentiment_Label']).size().unstack(fill_value=0)
    
    # Calculate percentages
    sentiment_pct = sentiment_analysis.div(sentiment_analysis.sum(axis=1), axis=0) * 100
    sentiment_pct = sentiment_pct.round(2)
    
    # Add average sentiment score
    avg_sentiment = merged.groupby('Keyword')['Sentiment'].mean().round(2)
    sentiment_pct['Avg_Sentiment_Score'] = avg_sentiment
    
    return sentiment_pct.reset_index()


def calculate_video_performance_trends(df):
    """
    Calculate performance trends over time
    
    Args:
        df: Cleaned videos DataFrame
    
    Returns:
        DataFrame: Time-based performance metrics
    """
    # Group by month and category
    trends = df.groupby(['Year', 'Month', 'Keyword']).agg({
        'Views': 'mean',
        'Likes': 'mean',
        'Comments': 'mean',
        'Engagement_Rate': 'mean',
        'Title': 'count'
    }).reset_index()
    
    trends.columns = ['Year', 'Month', 'Category', 'Avg_Views', 
                      'Avg_Likes', 'Avg_Comments', 'Avg_Engagement', 'Video_Count']
    
    return trends


def detect_viral_outliers(df, view_quantile=0.95):
    """
    Detect high-performing outlier videos using a quantile threshold.

    Args:
        df: Cleaned videos DataFrame
        view_quantile: Quantile threshold for viral videos

    Returns:
        DataFrame: Outlier videos with key metrics
    """
    threshold = df['Views'].quantile(view_quantile)
    outliers = df[df['Views'] >= threshold].copy()
    outliers['View_to_Median_Ratio'] = outliers['Views'] / max(df['Views'].median(), 1)
    return outliers.sort_values('Views', ascending=False)


def build_category_scorecard(df):
    """
    Build a normalized multi-metric scorecard for category benchmarking.

    Args:
        df: Cleaned videos DataFrame

    Returns:
        DataFrame: Category scorecard with consistency and composite score
    """
    category = df.groupby('Keyword').agg({
        'Views': ['mean', 'std'],
        'Likes': 'mean',
        'Comments': 'mean',
        'Engagement_Rate': 'mean',
        'Title': 'count'
    }).reset_index()

    category.columns = [
        'Keyword', 'Avg_Views', 'Std_Views', 'Avg_Likes',
        'Avg_Comments', 'Avg_Engagement_Rate', 'Video_Count'
    ]

    # Lower variability is better, so consistency score is inverse of CV.
    category['Views_CV'] = category['Std_Views'] / category['Avg_Views'].replace(0, np.nan)
    category['Consistency_Score'] = 1 / (1 + category['Views_CV'].fillna(category['Views_CV'].max()))

    metric_cols = ['Avg_Views', 'Avg_Likes', 'Avg_Comments', 'Avg_Engagement_Rate', 'Consistency_Score']
    for col in metric_cols:
        min_v = category[col].min()
        max_v = category[col].max()
        if max_v - min_v == 0:
            category[f'Norm_{col}'] = 0.5
        else:
            category[f'Norm_{col}'] = (category[col] - min_v) / (max_v - min_v)

    category['Composite_Score'] = (
        category['Norm_Avg_Views'] * 0.30 +
        category['Norm_Avg_Likes'] * 0.20 +
        category['Norm_Avg_Comments'] * 0.20 +
        category['Norm_Avg_Engagement_Rate'] * 0.20 +
        category['Norm_Consistency_Score'] * 0.10
    )

    return category.sort_values('Composite_Score', ascending=False).reset_index(drop=True)


def forecast_next_month_category_performance(df, min_points=3):
    """
    Forecast next-month average views and engagement by category.

    Uses a simple linear trend on monthly averages per category.

    Args:
        df: Cleaned videos DataFrame
        min_points: Minimum monthly points required to build a trend

    Returns:
        DataFrame: Forecast table by category
    """
    monthly = (
        df.assign(Year_Month=df['Published At'].dt.to_period('M').astype(str))
        .groupby(['Keyword', 'Year_Month'])
        .agg(
            Avg_Views=('Views', 'mean'),
            Avg_Engagement=('Engagement_Rate', 'mean'),
            Video_Count=('Video ID', 'count')
        )
        .reset_index()
    )

    rows = []
    for category, grp in monthly.groupby('Keyword'):
        grp = grp.sort_values('Year_Month').reset_index(drop=True)
        n = len(grp)
        if n < min_points:
            continue

        x = np.arange(n)
        v_coef = np.polyfit(x, grp['Avg_Views'].values, 1)
        e_coef = np.polyfit(x, grp['Avg_Engagement'].values, 1)

        next_x = n
        pred_views = max(0, np.polyval(v_coef, next_x))
        pred_eng = max(0, np.polyval(e_coef, next_x))

        last_views = grp['Avg_Views'].iloc[-1]
        last_eng = grp['Avg_Engagement'].iloc[-1]

        rows.append({
            'Keyword': category,
            'Months_Used': n,
            'Last_Month_Avg_Views': last_views,
            'Forecast_Next_Month_Avg_Views': pred_views,
            'Views_Forecast_Change_Pct': ((pred_views - last_views) / max(last_views, 1)) * 100,
            'Last_Month_Avg_Engagement': last_eng,
            'Forecast_Next_Month_Avg_Engagement': pred_eng,
            'Engagement_Forecast_Change_Pct': ((pred_eng - last_eng) / max(last_eng, 1e-6)) * 100,
            'Trend_Slope_Views': v_coef[0],
            'Trend_Slope_Engagement': e_coef[0]
        })

    forecast = pd.DataFrame(rows)
    if forecast.empty:
        return forecast

    forecast['Forecast_Momentum_Score'] = (
        forecast['Views_Forecast_Change_Pct'] * 0.7 +
        forecast['Engagement_Forecast_Change_Pct'] * 0.3
    )

    return forecast.sort_values('Forecast_Momentum_Score', ascending=False).reset_index(drop=True)


def create_summary_statistics(df):
    """
    Generate comprehensive summary statistics
    
    Args:
        df: Cleaned videos DataFrame
    
    Returns:
        dict: Summary statistics
    """
    summary = {
        'total_videos': len(df),
        'total_views': df['Views'].sum(),
        'total_likes': df['Likes'].sum(),
        'total_comments': df['Comments'].sum(),
        'avg_views': df['Views'].mean(),
        'avg_likes': df['Likes'].mean(),
        'avg_comments': df['Comments'].mean(),
        'avg_engagement_rate': df['Engagement_Rate'].mean(),
        'categories_count': df['Keyword'].nunique(),
        'date_range': f"{df['Published At'].min()} to {df['Published At'].max()}"
    }
    
    return summary


if __name__ == "__main__":
    from cleaning import load_data, clean_videos_data, clean_comments_data
    
    print("Loading and cleaning data...")
    videos_df, comments_df = load_data()
    videos_clean = clean_videos_data(videos_df)
    comments_clean = clean_comments_data(comments_df)
    
    print("\n=== ANALYSIS RESULTS ===\n")
    
    print("1. CHANNEL GROWTH ANALYSIS")
    growth = analyze_channel_growth(videos_clean)
    print(growth.head())
    
    print("\n2. UPLOAD FREQUENCY VS VIEWS")
    freq_correlation, freq_data = analyze_upload_frequency_vs_views(videos_clean)
    print(freq_correlation)
    
    print("\n3. CATEGORY ENGAGEMENT")
    engagement = analyze_category_engagement(videos_clean)
    print(engagement.head())
    
    print("\n4. SUMMARY STATISTICS")
    summary = create_summary_statistics(videos_clean)
    for key, value in summary.items():
        print(f"{key}: {value}")

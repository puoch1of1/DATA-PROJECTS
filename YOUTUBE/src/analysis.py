"""
Analysis Module for YouTube Channel Data
Contains functions to answer key business questions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
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
    local_df = df.copy()
    local_df['Year_Month'] = local_df['Published At'].dt.to_period('M')
    
    # Calculate upload frequency
    upload_freq = local_df.groupby(['Keyword', 'Year_Month']).agg({
        'Title': 'count',
        'Views': 'mean',
        'Likes': 'mean',
        'Engagement_Rate': 'mean'
    }).reset_index()
    
    upload_freq.columns = ['Category', 'Period', 'Videos_Uploaded', 
                           'Avg_Views', 'Avg_Likes', 'Avg_Engagement']
    
    # Analyze correlation by category
    def _corr_row(group):
        corr, p_val = permutation_test_correlation(
            group['Videos_Uploaded'],
            group['Avg_Views'],
            n_perm=1000
        )

        if pd.notna(p_val):
            if p_val < 0.01:
                significance = 'Very Strong Evidence'
            elif p_val < 0.05:
                significance = 'Strong Evidence'
            elif p_val < 0.10:
                significance = 'Weak Evidence'
            else:
                significance = 'No Reliable Evidence'
        else:
            significance = 'Insufficient Data'

        return pd.Series({
            'Avg_Upload_Frequency': group['Videos_Uploaded'].mean(),
            'Avg_Views': group['Avg_Views'].mean(),
            'Correlation_Freq_Views': corr,
            'P_Value': p_val,
            'Significance': significance
        })

    correlation_analysis = upload_freq.groupby('Category').apply(_corr_row).round(4)
    
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


def analyze_publish_timing(df, min_videos=3):
    """
    Identify the best publish windows by category and day-of-week.

    Args:
        df: Cleaned videos DataFrame
        min_videos: Minimum number of videos required per bucket

    Returns:
        DataFrame: Ranked timing opportunities
    """
    timing = (
        df.groupby(['Keyword', 'Day_of_Week'])
        .agg(
            Video_Count=('Video ID', 'count'),
            Avg_Views=('Views', 'mean'),
            Avg_Engagement=('Engagement_Rate', 'mean'),
            Median_Views=('Views', 'median')
        )
        .reset_index()
    )

    timing = timing[timing['Video_Count'] >= min_videos].copy()
    if timing.empty:
        return timing

    for col in ['Avg_Views', 'Avg_Engagement', 'Video_Count']:
        min_v = timing[col].min()
        max_v = timing[col].max()
        if max_v - min_v == 0:
            timing[f'Norm_{col}'] = 0.5
        else:
            timing[f'Norm_{col}'] = (timing[col] - min_v) / (max_v - min_v)

    timing['Timing_Opportunity_Score'] = (
        timing['Norm_Avg_Views'] * 0.45 +
        timing['Norm_Avg_Engagement'] * 0.45 +
        timing['Norm_Video_Count'] * 0.10
    )

    return timing.sort_values('Timing_Opportunity_Score', ascending=False).reset_index(drop=True)


def build_engagement_confidence_intervals(df, min_videos=3):
    """
    Build bootstrap confidence intervals for engagement by category.

    Args:
        df: Cleaned videos DataFrame
        min_videos: Minimum number of videos required in a category

    Returns:
        DataFrame: Mean engagement with confidence intervals
    """
    rows = []
    for keyword, group in df.groupby('Keyword'):
        if len(group) < min_videos:
            continue
        mean_val, lower, upper = bootstrap_mean_ci(group['Engagement_Rate'], n_boot=1500, ci=95)
        rows.append({
            'Keyword': keyword,
            'Video_Count': len(group),
            'Engagement_Mean': mean_val,
            'Engagement_CI_Lower': lower,
            'Engagement_CI_Upper': upper,
            'Engagement_CI_Width': upper - lower
        })

    ci_df = pd.DataFrame(rows)
    if ci_df.empty:
        return ci_df

    return ci_df.sort_values('Engagement_Mean', ascending=False).reset_index(drop=True)


def generate_content_strategy_recommendations(df, comments_df=None, min_videos=5):
    """
    Generate category-level strategy recommendations from multiple signals.

    Args:
        df: Cleaned videos DataFrame
        comments_df: Optional cleaned comments DataFrame
        min_videos: Minimum videos required for recommendation eligibility

    Returns:
        DataFrame: Actionable strategy recommendations by category
    """
    scorecard = build_category_scorecard(df)
    engagement = analyze_category_engagement(df)
    forecast = forecast_next_month_category_performance(df)
    timing = analyze_publish_timing(df, min_videos=3)

    base = scorecard.merge(
        engagement[['Keyword', 'Engagement_Score', 'Avg_Engagement_Rate', 'Video_Count']],
        on='Keyword',
        how='left',
        suffixes=('', '_eng')
    )

    if not forecast.empty:
        base = base.merge(
            forecast[['Keyword', 'Views_Forecast_Change_Pct', 'Engagement_Forecast_Change_Pct', 'Forecast_Momentum_Score']],
            on='Keyword',
            how='left'
        )
    else:
        base['Views_Forecast_Change_Pct'] = np.nan
        base['Engagement_Forecast_Change_Pct'] = np.nan
        base['Forecast_Momentum_Score'] = np.nan

    top_timing = pd.DataFrame(columns=['Keyword', 'Best_Publish_Day', 'Best_Publish_Day_Score'])
    if not timing.empty:
        top_timing = (
            timing.sort_values('Timing_Opportunity_Score', ascending=False)
            .groupby('Keyword')
            .head(1)
            .rename(columns={
                'Day_of_Week': 'Best_Publish_Day',
                'Timing_Opportunity_Score': 'Best_Publish_Day_Score'
            })[['Keyword', 'Best_Publish_Day', 'Best_Publish_Day_Score']]
        )

    base = base.merge(top_timing, on='Keyword', how='left')

    if comments_df is not None and len(comments_df) > 0:
        sentiment = analyze_sentiment_by_category(comments_df, df)
        base = base.merge(
            sentiment[['Keyword', 'Avg_Sentiment_Score']],
            on='Keyword',
            how='left'
        )
    else:
        base['Avg_Sentiment_Score'] = np.nan

    base = base[base['Video_Count'] >= min_videos].copy()
    if base.empty:
        return base

    def _strategy_theme(row):
        momentum = row.get('Forecast_Momentum_Score', np.nan)
        if row['Composite_Score'] >= 0.70 and pd.notna(momentum) and momentum > 10:
            return 'Scale Aggressively'
        if row['Avg_Views'] >= base['Avg_Views'].median() and row['Avg_Engagement_Rate'] < base['Avg_Engagement_Rate'].median():
            return 'Improve Engagement Quality'
        if row['Avg_Engagement_Rate'] >= base['Avg_Engagement_Rate'].quantile(0.75):
            return 'Niche Community Expansion'
        return 'Defend and Optimize'

    def _action(row):
        day = row['Best_Publish_Day'] if pd.notna(row['Best_Publish_Day']) else 'peak audience day'
        if row['Strategy_Theme'] == 'Scale Aggressively':
            return f"Increase posting frequency and prioritize {day} releases with repeatable formats."
        if row['Strategy_Theme'] == 'Improve Engagement Quality':
            return f"Keep reach-oriented topics but add stronger hooks/CTAs and publish on {day}."
        if row['Strategy_Theme'] == 'Niche Community Expansion':
            return f"Expand this niche with series-based content and audience prompts on {day}."
        return f"Maintain cadence, refine thumbnails/titles, and test one new format on {day}."

    base['Strategy_Theme'] = base.apply(_strategy_theme, axis=1)
    base['Primary_Action'] = base.apply(_action, axis=1)

    base['Risk_Level'] = np.where(
        base['Views_CV'] > base['Views_CV'].quantile(0.75),
        'High Volatility',
        'Moderate'
    )

    return base.sort_values('Composite_Score', ascending=False).reset_index(drop=True)


def export_advanced_outputs(df, comments_df=None, output_dir='../data'):
    """
    Export a richer set of analytics artifacts for decision making.

    Args:
        df: Cleaned videos DataFrame
        comments_df: Optional cleaned comments DataFrame
        output_dir: Directory for output CSV/JSON files

    Returns:
        dict: Named output file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    scorecard = build_category_scorecard(df)
    forecast = forecast_next_month_category_performance(df)
    viral = detect_viral_outliers(df, view_quantile=0.95)
    engagement_ci = build_engagement_confidence_intervals(df)
    strategy = generate_content_strategy_recommendations(df, comments_df=comments_df)
    timing = analyze_publish_timing(df)
    freq_sig, _ = analyze_upload_frequency_vs_views(df)

    files = {
        'category_scorecard': output_path / 'category_scorecard.csv',
        'next_month_forecast': output_path / 'next_month_category_forecast.csv',
        'viral_videos_95pct': output_path / 'viral_videos_95pct.csv',
        'engagement_ci': output_path / 'engagement_ci_by_category.csv',
        'strategy': output_path / 'strategy_recommendations.csv',
        'publish_timing': output_path / 'publish_timing_recommendations.csv',
        'upload_frequency_significance': output_path / 'upload_frequency_significance.csv',
        'summary_json': output_path / 'analysis_summary.json'
    }

    scorecard.to_csv(files['category_scorecard'], index=False)
    forecast.to_csv(files['next_month_forecast'], index=False)
    viral.to_csv(files['viral_videos_95pct'], index=False)
    engagement_ci.to_csv(files['engagement_ci'], index=False)
    strategy.to_csv(files['strategy'], index=False)
    timing.to_csv(files['publish_timing'], index=False)
    freq_sig.to_csv(files['upload_frequency_significance'], index=False)

    summary = create_summary_statistics(df)
    summary['generated_at_utc'] = datetime.utcnow().isoformat()
    summary['top_strategy_categories'] = strategy['Keyword'].head(5).tolist() if not strategy.empty else []
    with open(files['summary_json'], 'w', encoding='utf-8') as fp:
        json.dump(summary, fp, indent=2, default=str)

    return {name: str(path) for name, path in files.items()}


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

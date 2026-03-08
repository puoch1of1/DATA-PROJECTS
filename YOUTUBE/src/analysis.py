"""
Analysis Module for YouTube Channel Data
Contains functions to answer key business questions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


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

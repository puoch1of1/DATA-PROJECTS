"""
Data Cleaning Module for YouTube Channel Analysis
Handles data preprocessing, cleaning, and validation
"""

import pandas as pd
import numpy as np
from datetime import datetime


def load_data(videos_path='../data/videos-stats.csv', comments_path='../data/comments.csv'):
    """
    Load YouTube videos and comments data
    
    Args:
        videos_path: Path to videos stats CSV file
        comments_path: Path to comments CSV file
    
    Returns:
        tuple: (videos_df, comments_df)
    """
    videos_df = pd.read_csv(videos_path)
    comments_df = pd.read_csv(comments_path)
    return videos_df, comments_df


def clean_videos_data(df):
    """
    Clean and preprocess videos statistics data
    
    Args:
        df: Raw videos DataFrame
    
    Returns:
        DataFrame: Cleaned videos data
    """
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Drop the unnamed index column if it exists
    if 'Unnamed: 0' in df_clean.columns:
        df_clean = df_clean.drop('Unnamed: 0', axis=1)
    
    # Convert 'Published At' to datetime
    df_clean['Published At'] = pd.to_datetime(df_clean['Published At'])
    
    # Extract date components for time series analysis
    df_clean['Year'] = df_clean['Published At'].dt.year
    df_clean['Month'] = df_clean['Published At'].dt.month
    df_clean['Day'] = df_clean['Published At'].dt.day
    df_clean['Day_of_Week'] = df_clean['Published At'].dt.day_name()
    
    # Handle missing values
    df_clean['Likes'] = df_clean['Likes'].fillna(0)
    df_clean['Comments'] = df_clean['Comments'].fillna(0)
    df_clean['Views'] = df_clean['Views'].fillna(0)
    
    # Calculate engagement metrics
    df_clean['Engagement_Rate'] = (df_clean['Likes'] + df_clean['Comments']) / (df_clean['Views'] + 1) * 100
    df_clean['Like_Rate'] = df_clean['Likes'] / (df_clean['Views'] + 1) * 100
    df_clean['Comment_Rate'] = df_clean['Comments'] / (df_clean['Views'] + 1) * 100
    
    # Clean category/keyword column
    df_clean['Keyword'] = df_clean['Keyword'].str.strip().str.lower()
    
    return df_clean


def clean_comments_data(df):
    """
    Clean and preprocess comments data
    
    Args:
        df: Raw comments DataFrame
    
    Returns:
        DataFrame: Cleaned comments data
    """
    # Create a copy
    df_clean = df.copy()
    
    # Drop the unnamed index column if it exists
    if 'Unnamed: 0' in df_clean.columns:
        df_clean = df_clean.drop('Unnamed: 0', axis=1)
    
    # Handle missing values
    df_clean['Likes'] = df_clean['Likes'].fillna(0)
    df_clean['Sentiment'] = df_clean['Sentiment'].fillna(1)  # Default to neutral
    
    # Remove duplicate comments
    df_clean = df_clean.drop_duplicates(subset=['Video ID', 'Comment'])
    
    # Map sentiment to descriptive labels
    sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    df_clean['Sentiment_Label'] = df_clean['Sentiment'].map(sentiment_map)
    
    return df_clean


def merge_data(videos_df, comments_df):
    """
    Merge videos and comments data
    
    Args:
        videos_df: Cleaned videos DataFrame
        comments_df: Cleaned comments DataFrame
    
    Returns:
        DataFrame: Merged dataset
    """
    # Aggregate comments by video
    comments_agg = comments_df.groupby('Video ID').agg({
        'Comment': 'count',
        'Likes': 'sum',
        'Sentiment': 'mean'
    }).rename(columns={
        'Comment': 'Total_Comments',
        'Likes': 'Total_Comment_Likes',
        'Sentiment': 'Avg_Sentiment'
    }).reset_index()
    
    # Merge with videos data
    merged_df = videos_df.merge(comments_agg, on='Video ID', how='left')
    
    return merged_df


def get_channel_stats(df):
    """
    Extract channel-level statistics from video titles
    Note: This is a simplified version. In production, you'd use YouTube API
    
    Args:
        df: Videos DataFrame
    
    Returns:
        DataFrame: Channel statistics
    """
    # Group by keyword (category) as a proxy for channels
    channel_stats = df.groupby('Keyword').agg({
        'Title': 'count',
        'Views': ['sum', 'mean'],
        'Likes': ['sum', 'mean'],
        'Comments': ['sum', 'mean'],
        'Engagement_Rate': 'mean'
    }).round(2)
    
    channel_stats.columns = ['Video_Count', 'Total_Views', 'Avg_Views', 
                              'Total_Likes', 'Avg_Likes', 
                              'Total_Comments', 'Avg_Comments',
                              'Avg_Engagement_Rate']
    
    return channel_stats.reset_index()


def save_cleaned_data(df, output_path='../data/cleaned_youtube_data.csv'):
    """
    Save cleaned data to CSV
    
    Args:
        df: Cleaned DataFrame
        output_path: Path to save cleaned data
    """
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    print("Loading data...")
    videos_df, comments_df = load_data()
    
    print("Cleaning videos data...")
    videos_clean = clean_videos_data(videos_df)
    
    print("Cleaning comments data...")
    comments_clean = clean_comments_data(comments_df)
    
    print("Merging datasets...")
    merged_data = merge_data(videos_clean, comments_clean)
    
    print("Saving cleaned data...")
    save_cleaned_data(merged_data)
    
    print("\nData cleaning complete!")
    print(f"Total videos: {len(merged_data)}")
    print(f"Total comments: {len(comments_clean)}")

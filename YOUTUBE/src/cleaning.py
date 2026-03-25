"""
Data Cleaning Module for YouTube Channel Analysis.
Handles data preprocessing, cleaning, and validation.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEOS_PATH = Path("data/videos-stats.csv")
DEFAULT_COMMENTS_PATH = Path("data/comments.csv")
REQUIRED_VIDEO_COLUMNS = {
    "Title",
    "Video ID",
    "Published At",
    "Keyword",
    "Likes",
    "Comments",
    "Views",
}
REQUIRED_COMMENT_COLUMNS = {
    "Video ID",
    "Comment",
    "Likes",
    "Sentiment",
}


def resolve_project_path(path_like):
    """
    Resolve a project file path.

    Relative paths are checked against the current working directory first,
    then against the project root so the pipeline works from different launch
    locations.
    """
    path = Path(path_like).expanduser()
    if path.is_absolute():
        return path

    cwd_candidate = path.resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    return (PROJECT_ROOT / path).resolve()


def _standardize_columns(df):
    df = df.copy()
    rename_map = {}
    drop_columns = []

    for column in df.columns:
        normalized = str(column).strip()
        if not normalized or normalized.lower().startswith("unnamed:"):
            drop_columns.append(column)
        elif normalized != column:
            rename_map[column] = normalized

    if rename_map:
        df = df.rename(columns=rename_map)
    if drop_columns:
        df = df.drop(columns=drop_columns)

    return df


def _validate_required_columns(df, required_columns, dataset_name):
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: {', '.join(missing_columns)}"
        )


def _coerce_numeric_columns(df, columns):
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def load_data(videos_path=DEFAULT_VIDEOS_PATH, comments_path=DEFAULT_COMMENTS_PATH):
    """
    Load YouTube videos and comments data.

    Args:
        videos_path: Path to videos stats CSV file
        comments_path: Path to comments CSV file

    Returns:
        tuple: (videos_df, comments_df)
    """
    videos_df = pd.read_csv(resolve_project_path(videos_path))
    comments_df = pd.read_csv(resolve_project_path(comments_path))
    return videos_df, comments_df


def clean_videos_data(df):
    """
    Clean and preprocess videos statistics data.

    Args:
        df: Raw videos DataFrame

    Returns:
        DataFrame: Cleaned videos data
    """
    df_clean = _standardize_columns(df)
    _validate_required_columns(df_clean, REQUIRED_VIDEO_COLUMNS, "Videos dataset")

    df_clean["Video ID"] = df_clean["Video ID"].fillna("").astype(str).str.strip()
    df_clean["Title"] = df_clean["Title"].fillna("").astype(str).str.strip()
    df_clean["Keyword"] = (
        df_clean["Keyword"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace("", "unknown")
    )

    df_clean = _coerce_numeric_columns(df_clean, ["Likes", "Comments", "Views"])
    for column in ["Likes", "Comments", "Views"]:
        df_clean[column] = df_clean[column].fillna(0).clip(lower=0)

    df_clean["Published At"] = pd.to_datetime(df_clean["Published At"], errors="coerce")
    df_clean = df_clean.dropna(subset=["Published At"]).copy()
    df_clean = df_clean[df_clean["Video ID"] != ""].copy()

    df_clean["Year"] = df_clean["Published At"].dt.year
    df_clean["Month"] = df_clean["Published At"].dt.month
    df_clean["Day"] = df_clean["Published At"].dt.day
    df_clean["Day_of_Week"] = df_clean["Published At"].dt.day_name()

    denominator = df_clean["Views"] + 1
    df_clean["Engagement_Rate"] = (df_clean["Likes"] + df_clean["Comments"]) / denominator * 100
    df_clean["Like_Rate"] = df_clean["Likes"] / denominator * 100
    df_clean["Comment_Rate"] = df_clean["Comments"] / denominator * 100

    return df_clean.reset_index(drop=True)


def clean_comments_data(df):
    """
    Clean and preprocess comments data.

    Args:
        df: Raw comments DataFrame

    Returns:
        DataFrame: Cleaned comments data
    """
    df_clean = _standardize_columns(df)
    _validate_required_columns(df_clean, REQUIRED_COMMENT_COLUMNS, "Comments dataset")

    df_clean["Video ID"] = df_clean["Video ID"].fillna("").astype(str).str.strip()
    df_clean["Comment"] = df_clean["Comment"].fillna("").astype(str).str.strip()
    df_clean = df_clean[(df_clean["Video ID"] != "") & (df_clean["Comment"] != "")].copy()

    df_clean = _coerce_numeric_columns(df_clean, ["Likes", "Sentiment"])
    df_clean["Likes"] = df_clean["Likes"].fillna(0).clip(lower=0)
    df_clean["Sentiment"] = (
        df_clean["Sentiment"]
        .where(df_clean["Sentiment"].isin([0, 1, 2]), 1)
        .fillna(1)
        .astype(int)
    )

    df_clean = df_clean.drop_duplicates(subset=["Video ID", "Comment"]).copy()

    sentiment_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
    df_clean["Sentiment_Label"] = df_clean["Sentiment"].map(sentiment_map).fillna("Neutral")

    return df_clean.reset_index(drop=True)


def merge_data(videos_df, comments_df):
    """
    Merge videos and comments data.

    Args:
        videos_df: Cleaned videos DataFrame
        comments_df: Cleaned comments DataFrame

    Returns:
        DataFrame: Merged dataset
    """
    comments_agg = (
        comments_df.groupby("Video ID")
        .agg(
            Total_Comments=("Comment", "count"),
            Total_Comment_Likes=("Likes", "sum"),
            Avg_Sentiment=("Sentiment", "mean"),
        )
        .reset_index()
    )

    merged_df = videos_df.merge(comments_agg, on="Video ID", how="left")

    return merged_df


def get_channel_stats(df):
    """
    Extract channel-level statistics from video titles.
    Note: This is a simplified version. In production, you'd use YouTube API.

    Args:
        df: Videos DataFrame

    Returns:
        DataFrame: Channel statistics
    """
    channel_stats = df.groupby("Keyword").agg(
        {
            "Title": "count",
            "Views": ["sum", "mean"],
            "Likes": ["sum", "mean"],
            "Comments": ["sum", "mean"],
            "Engagement_Rate": "mean",
        }
    ).round(2)

    channel_stats.columns = [
        "Video_Count",
        "Total_Views",
        "Avg_Views",
        "Total_Likes",
        "Avg_Likes",
        "Total_Comments",
        "Avg_Comments",
        "Avg_Engagement_Rate",
    ]

    return channel_stats.reset_index()


def save_cleaned_data(df, output_path="data/cleaned_youtube_data.csv"):
    """
    Save cleaned data to CSV.

    Args:
        df: Cleaned DataFrame
        output_path: Path to save cleaned data
    """
    resolved_output_path = resolve_project_path(output_path)
    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(resolved_output_path, index=False)
    print(f"Cleaned data saved to {resolved_output_path}")


if __name__ == "__main__":
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

"""
Run the full YouTube analytics pipeline from the command line.
"""

import argparse

from cleaning import (
    PROJECT_ROOT,
    clean_comments_data,
    clean_videos_data,
    load_data,
    merge_data,
    resolve_project_path,
    save_cleaned_data,
)
from analysis import (
    analyze_category_engagement,
    analyze_channel_growth,
    create_summary_statistics,
    export_advanced_outputs,
)


def build_parser():
    parser = argparse.ArgumentParser(description="Run YouTube analysis pipeline")
    parser.add_argument(
        "--videos-path",
        default="data/videos-stats.csv",
        help="Path to videos CSV file",
    )
    parser.add_argument(
        "--comments-path",
        default="data/comments.csv",
        help="Path to comments CSV file",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where output artifacts will be written",
    )
    parser.add_argument(
        "--cleaned-output",
        default="data/cleaned_youtube_data.csv",
        help="Path to save the cleaned merged dataset",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    output_dir = resolve_project_path(args.output_dir)
    cleaned_output = resolve_project_path(args.cleaned_output)

    print("Loading raw datasets...")
    videos_raw, comments_raw = load_data(args.videos_path, args.comments_path)

    print("Cleaning datasets...")
    videos_clean = clean_videos_data(videos_raw)
    comments_clean = clean_comments_data(comments_raw)
    merged_clean = merge_data(videos_clean, comments_clean)
    save_cleaned_data(merged_clean, cleaned_output)

    print("Running core analysis...")
    growth = analyze_channel_growth(videos_clean)
    engagement = analyze_category_engagement(videos_clean)
    summary = create_summary_statistics(videos_clean)

    print("Exporting advanced outputs...")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = export_advanced_outputs(
        videos_clean,
        comments_df=comments_clean,
        output_dir=output_dir,
    )

    growth_path = output_dir / "channel_growth_summary.csv"
    engagement_path = output_dir / "category_engagement_summary.csv"
    growth.to_csv(growth_path, index=False)
    engagement.to_csv(engagement_path, index=False)

    print("\nPipeline complete.")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Videos analyzed: {summary['total_videos']:,}")
    print(f"Comments analyzed: {len(comments_clean):,}")
    print(f"Categories analyzed: {summary['categories_count']}")
    print("Output files:")
    print(f"- {cleaned_output}")
    print(f"- {growth_path}")
    print(f"- {engagement_path}")
    for _, path in output_files.items():
        print(f"- {path}")


if __name__ == "__main__":
    main()

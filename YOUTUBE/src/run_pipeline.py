"""
Run the full YouTube analytics pipeline from the command line.
"""

import argparse
from pathlib import Path

from cleaning import load_data, clean_videos_data, clean_comments_data
from analysis import (
    create_summary_statistics,
    analyze_channel_growth,
    analyze_category_engagement,
    export_advanced_outputs,
)


def build_parser():
    parser = argparse.ArgumentParser(description="Run YouTube analysis pipeline")
    parser.add_argument(
        "--videos-path",
        default="../data/videos-stats.csv",
        help="Path to videos CSV file",
    )
    parser.add_argument(
        "--comments-path",
        default="../data/comments.csv",
        help="Path to comments CSV file",
    )
    parser.add_argument(
        "--output-dir",
        default="../data",
        help="Directory where output artifacts will be written",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print("Loading raw datasets...")
    videos_raw, comments_raw = load_data(args.videos_path, args.comments_path)

    print("Cleaning datasets...")
    videos_clean = clean_videos_data(videos_raw)
    comments_clean = clean_comments_data(comments_raw)

    print("Running core analysis...")
    growth = analyze_channel_growth(videos_clean)
    engagement = analyze_category_engagement(videos_clean)
    summary = create_summary_statistics(videos_clean)

    print("Exporting advanced outputs...")
    output_files = export_advanced_outputs(
        videos_clean,
        comments_df=comments_clean,
        output_dir=args.output_dir,
    )

    output_dir = Path(args.output_dir)
    growth_path = output_dir / "channel_growth_summary.csv"
    engagement_path = output_dir / "category_engagement_summary.csv"
    growth.to_csv(growth_path, index=False)
    engagement.to_csv(engagement_path, index=False)

    print("\nPipeline complete.")
    print(f"Videos analyzed: {summary['total_videos']:,}")
    print(f"Categories analyzed: {summary['categories_count']}")
    print("Output files:")
    print(f"- {growth_path}")
    print(f"- {engagement_path}")
    for _, path in output_files.items():
        print(f"- {path}")


if __name__ == "__main__":
    main()

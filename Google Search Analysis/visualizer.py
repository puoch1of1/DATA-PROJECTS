"""Visualization and Reporting Module for Google Trends Analysis.

Generates charts, graphs, and reports from trend data.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


class TrendVisualizer:
    """Generate visualizations for trend analysis."""

    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """Initialize visualizer with matplotlib style.

        Args:
            style: Matplotlib style name
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use("default")
        sns.set_palette("husl")

    def plot_interest_over_time(
        self,
        data: pd.DataFrame,
        title: str = "Search Interest Over Time",
        save_path: Optional[str] = None,
    ) -> None:
        """Plot search interest trends over time.

        Args:
            data: DataFrame with dates as index and keywords as columns
            title: Chart title
            save_path: Optional path to save the figure
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        for column in data.columns:
            if column != "isPartial":
                ax.plot(data.index, data[column], marker="o", label=column, linewidth=2)

        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Interest Level (0-100)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Chart saved to {save_path}")
        plt.show()

    def plot_interest_by_region(
        self,
        data: pd.DataFrame,
        title: str = "Search Interest by Region",
        top_n: int = 15,
        save_path: Optional[str] = None,
    ) -> None:
        """Plot search interest by region.

        Args:
            data: DataFrame with regions and interest values
            title: Chart title
            top_n: Number of top regions to display
            save_path: Optional path to save the figure
        """
        top_regions = data.iloc[:top_n]

        fig, ax = plt.subplots(figsize=(12, 8))
        colors = sns.color_palette("coolwarm", len(top_regions))
        bars = ax.barh(range(len(top_regions)), top_regions.iloc[:, 0], color=colors)

        ax.set_yticks(range(len(top_regions)))
        ax.set_yticklabels(top_regions.index)
        ax.set_xlabel("Interest Level (0-100)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f"{int(width)}", ha="left", va="center")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Chart saved to {save_path}")
        plt.show()

    def plot_comparison_heatmap(
        self,
        data: pd.DataFrame,
        title: str = "Keyword Interest Heatmap",
        save_path: Optional[str] = None,
    ) -> None:
        """Create heatmap comparing multiple keywords over time.

        Args:
            data: DataFrame with dates as index and keywords as columns
            title: Chart title
            save_path: Optional path to save the figure
        """
        # Resample to weekly data for better visualization
        weekly_data = data.resample("W").mean()

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(weekly_data.T, cmap="YlOrRd", annot=False, cbar_kws={"label": "Interest Level"}, ax=ax)

        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Keywords", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Chart saved to {save_path}")
        plt.show()

    def plot_trend_metrics(
        self,
        metrics_df: pd.DataFrame,
        save_path: Optional[str] = None,
    ) -> None:
        """Create multi-panel visualization of trend metrics.

        Args:
            metrics_df: DataFrame with trend metrics for multiple keywords
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Trend Analysis Metrics", fontsize=16, fontweight="bold")

        # Average Interest
        axes[0, 0].barh(metrics_df["keyword"], metrics_df["avg_interest"], color="skyblue")
        axes[0, 0].set_xlabel("Average Interest")
        axes[0, 0].set_title("Average Interest Over Time")
        axes[0, 0].grid(axis="x", alpha=0.3)

        # Peak Interest
        axes[0, 1].barh(metrics_df["keyword"], metrics_df["peak_interest"], color="lightcoral")
        axes[0, 1].set_xlabel("Peak Interest")
        axes[0, 1].set_title("Peak Interest Level")
        axes[0, 1].grid(axis="x", alpha=0.3)

        # Volatility
        axes[1, 0].barh(metrics_df["keyword"], metrics_df["volatility"], color="lightgreen")
        axes[1, 0].set_xlabel("Volatility (Std Dev)")
        axes[1, 0].set_title("Interest Volatility")
        axes[1, 0].grid(axis="x", alpha=0.3)

        # Trend Direction (text)
        axes[1, 1].axis("off")
        trend_text = "Trend Directions:\n\n"
        colors_map = {"increasing": "green", "decreasing": "red", "stable": "gray"}
        for idx, row in metrics_df.iterrows():
            color = colors_map.get(row["trend"], "black")
            trend_text += f"• {row['keyword']}: {row['trend'].upper()}\n"

        axes[1, 1].text(0.5, 0.5, trend_text, ha="center", va="center", fontsize=11, family="monospace")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Chart saved to {save_path}")
        plt.show()

    def plot_seasonal_trends(
        self,
        seasonal_data: Dict[str, float],
        title: str = "Seasonal Trend Analysis",
        save_path: Optional[str] = None,
    ) -> None:
        """Plot seasonal patterns in search trends.

        Args:
            seasonal_data: Dict with month names and average interest
            title: Chart title
            save_path: Optional path to save the figure
        """
        months = list(seasonal_data.keys())
        values = list(seasonal_data.values())

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(months, values, marker="o", linewidth=2, markersize=10, color="steelblue")
        ax.fill_between(range(len(months)), values, alpha=0.3, color="steelblue")

        ax.set_ylabel("Average Interest Level", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Chart saved to {save_path}")
        plt.show()

    def create_interactive_comparison(
        self,
        data: pd.DataFrame,
        title: str = "Interactive Trend Comparison",
    ) -> go.Figure:
        """Create interactive Plotly visualization of trends.

        Args:
            data: DataFrame with dates as index and keywords as columns
            title: Chart title

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        for column in data.columns:
            if column != "isPartial":
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[column],
                        mode="lines+markers",
                        name=column,
                        hovertemplate="<b>%{fullData.name}</b><br>Date: %{x}<br>Interest: %{y}<extra></extra>",
                    )
                )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Interest Level (0-100)",
            hovermode="x unified",
            height=500,
            template="plotly_white",
        )

        return fig

    def create_interactive_regional(
        self,
        data: pd.DataFrame,
        title: str = "Interactive Regional Interest",
    ) -> go.Figure:
        """Create interactive regional comparison chart.

        Args:
            data: DataFrame with regions and interest values
            title: Chart title

        Returns:
            Plotly figure object
        """
        data = data.sort_values(by=data.columns[0], ascending=True).tail(20)

        fig = go.Figure(data=[go.Bar(x=data.iloc[:, 0], y=data.index)])

        fig.update_layout(
            title=title,
            xaxis_title="Interest Level (0-100)",
            yaxis_title="Region",
            height=600,
            template="plotly_white",
        )

        return fig


def generate_text_report(
    keyword: str,
    metrics: Dict,
    trending_searches: List[Dict],
    filename: str = "trend_report.txt",
) -> None:
    """Generate a text report of trend analysis.

    Args:
        keyword: Search keyword analyzed
        metrics: Dictionary of calculated metrics
        trending_searches: List of trending searches
        filename: Output filename
    """
    report = f"""
{'='*70}
GOOGLE SEARCH TRENDS ANALYSIS REPORT
{'='*70}

ANALYSIS KEYWORD: {keyword}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

{'-'*70}
TREND METRICS
{'-'*70}

Average Interest Level: {metrics.get('average_interest', 'N/A')}
Peak Interest Level:    {metrics.get('peak_interest', 'N/A')}
Peak Date:              {metrics.get('peak_date', 'N/A')}
Trend Direction:        {metrics.get('trend_direction', 'N/A')}
Volatility (Std Dev):   {metrics.get('volatility', 'N/A')}

{'-'*70}
TRENDING SEARCHES (SNAPSHOT)
{'-'*70}

"""

    if trending_searches:
        for item in trending_searches[:10]:
            report += f"\n{item.get('rank', 'N/A')}. {item.get('query', 'N/A')} ({item.get('country', 'N/A')})"
    else:
        report += "\nNo trending data available."

    report += f"\n\n{'='*70}\nEND OF REPORT\n{'='*70}\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to {filename}")

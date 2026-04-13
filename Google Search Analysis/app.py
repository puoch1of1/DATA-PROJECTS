"""
STREAMLIT WEB DASHBOARD
=======================
Interactive web interface for Google Trends analysis and GOOGL stock data.

Use this for:
  • Visual exploration of search trends
  • Interactive charts and comparisons
  • Sharing results via web interface
  • Real-time metric calculations

To run:
  streamlit run app.py

Then open browser to: http://localhost:8501

NOTE: If you prefer command-line interaction, use main.py instead.
      If you need batch processing, use run_googl_stock_project.py.

Streamlit Web Dashboard for Google Search Trends Analysis.

Interactive dashboard for exploring and visualizing Google search trends.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import plotly.graph_objects as go

from googl_stock_project import GOOGLStockAnalyzer
from trend_analyzer import GoogleTrendAnalyzer
from visualizer import TrendVisualizer


BASE_DIR = Path(__file__).resolve().parent
GOOGL_RAW_PATH = BASE_DIR / "data" / "GOOGL.csv"
GOOGL_ENRICHED_PATH = BASE_DIR / "data" / "googl_enriched.csv"
GOOGL_KPI_PATH = BASE_DIR / "reports" / "googl_kpis.json"
GOOGL_SUMMARY_PATH = BASE_DIR / "reports" / "googl_analysis_summary.txt"

# Page configuration
st.set_page_config(
    page_title="Google Search Trends Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "analyzer" not in st.session_state:
    st.session_state.analyzer = GoogleTrendAnalyzer()

if "visualizer" not in st.session_state:
    st.session_state.visualizer = TrendVisualizer()

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = {}


def normalize_keywords(raw_input: str, max_items: int = 5) -> list[str]:
    """Normalize comma-separated keyword input into unique non-empty items."""
    keywords: list[str] = []
    seen: set[str] = set()

    for item in raw_input.split(","):
        keyword = item.strip()
        key = keyword.lower()
        if keyword and key not in seen:
            seen.add(key)
            keywords.append(keyword)

    return keywords[:max_items]


def render_export_section(data: pd.DataFrame, export_format: str, base_name: str) -> None:
    """Render a download button for DataFrame content in selected format."""
    if data.empty:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if export_format == "CSV":
        payload = data.to_csv(index=True).encode("utf-8")
        mime = "text/csv"
        filename = f"{base_name}_{timestamp}.csv"
    else:
        payload = data.to_json(orient="records", date_format="iso", indent=2).encode("utf-8")
        mime = "application/json"
        filename = f"{base_name}_{timestamp}.json"

    st.download_button(
        label=f"Download {export_format}",
        data=payload,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )


def load_googl_outputs() -> tuple[pd.DataFrame, dict]:
    """Load GOOGL enriched data and KPI JSON produced by the stock project."""
    if not GOOGL_ENRICHED_PATH.exists() or not GOOGL_KPI_PATH.exists():
        return pd.DataFrame(), {}

    df = pd.read_csv(GOOGL_ENRICHED_PATH)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    with GOOGL_KPI_PATH.open("r", encoding="utf-8") as f:
        kpis = json.load(f)

    return df, kpis


def rebuild_googl_outputs() -> None:
    """Re-run the dataset project so dashboard data and charts are fresh."""
    if not GOOGL_RAW_PATH.exists():
        raise FileNotFoundError(f"Missing input dataset at {GOOGL_RAW_PATH}")

    analyzer = GOOGLStockAnalyzer(csv_path=GOOGL_RAW_PATH, ticker="GOOGL")
    analyzer.load_data()
    analyzer.engineer_features()
    analyzer.export_outputs(
        data_output_path=GOOGL_ENRICHED_PATH,
        kpi_output_path=GOOGL_KPI_PATH,
        summary_output_path=GOOGL_SUMMARY_PATH,
    )
    analyzer.generate_charts(output_dir=BASE_DIR / "reports")


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_trending(country: str) -> list[dict[str, str]]:
    return st.session_state.analyzer.get_trending_searches(country)


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_interest_over_time(keywords: tuple[str, ...], timeframe: str) -> pd.DataFrame:
    return st.session_state.analyzer.get_interest_over_time(list(keywords), timeframe)


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_seasonal(keyword: str) -> dict[str, float]:
    return st.session_state.analyzer.get_seasonal_trends(keyword)


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_related_queries(keyword: str) -> dict[str, pd.DataFrame]:
    return st.session_state.analyzer.get_related_queries(keyword)


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_comparison_stats(keywords: tuple[str, ...], timeframe: str) -> pd.DataFrame:
    return st.session_state.analyzer.get_keyword_comparison_stats(list(keywords), timeframe)


@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_region(keywords: tuple[str, ...], resolution: str, timeframe: str) -> pd.DataFrame:
    return st.session_state.analyzer.get_interest_by_region(list(keywords), resolution=resolution, timeframe=timeframe)

# Main title
st.write('<div class="main-header">🔍 Google Search Trends Dashboard</div>', unsafe_allow_html=True)
st.caption("Explore search trends, compare keywords, and discover what people are searching for")

# Sidebar for navigation
with st.sidebar:
    st.header("⚙️ Controls & Settings")

    analysis_type = st.radio(
        "Select Analysis Type",
        [
            "Trending Searches",
            "Keyword Analysis",
            "Compare Keywords",
            "Regional Analysis",
            "Seasonal Trends",
            "GOOGL Stock Project",
        ]
    )

    st.divider()

    # Timeframe selection
    timeframe_options = {
        "Past Month": "today 1-m",
        "Past 3 Months": "today 3-m",
        "Past Year": "today 12-m",
        "Past 5 Years": "today 5-y",
    }

    timeframe_label = st.selectbox("Select Timeframe", list(timeframe_options.keys()))
    timeframe = timeframe_options[timeframe_label]

    st.divider()

    # Export options
    st.subheader("Export Options")
    export_format = st.radio("Export Format", ["CSV", "JSON"])

# Main content area
if analysis_type == "Trending Searches":
    st.header("Currently Trending Searches")

    col1, col2 = st.columns(2)

    with col1:
        countries = st.multiselect(
            "Select Countries",
            ["US", "GB", "IN", "CA", "AU", "DE", "FR", "JP", "BR", "MX"],
            default=["US", "GB", "IN"]
        )

    with col2:
        st.write("")  # Spacing

    if countries:
        with st.spinner("Fetching trending searches..."):
            all_trends: list[dict[str, str]] = []
            for country in countries:
                st.subheader(f"Top Trends in {country}")
                try:
                    trending = get_cached_trending(country)
                    if trending:
                        all_trends.extend(trending)
                        cols = st.columns(2)
                        for idx, item in enumerate(trending[:20]):
                            col = cols[idx % 2]
                            with col:
                                st.write(f"**#{item['rank']}** {item['query']}")
                    else:
                        st.warning("No data available for this country")
                except Exception as exc:
                    st.error(f"Unable to fetch trends for {country}: {exc}")

            if all_trends:
                st.subheader("Export Trending Results")
                trends_df = pd.DataFrame(all_trends)
                render_export_section(trends_df, export_format, "trending_searches")

elif analysis_type == "Keyword Analysis":
    st.header("Single Keyword Analysis")

    keyword = st.text_input("Enter keyword to analyze", placeholder="e.g., artificial intelligence")

    if keyword:
        with st.spinner(f"Analyzing '{keyword}'..."):
            try:
                metrics = st.session_state.analyzer.calculate_trend_metrics(keyword, timeframe)
            except Exception as exc:
                st.error(f"Keyword analysis failed: {exc}")
                st.stop()

            # Display metrics in columns
            metric_cols = st.columns(5)

            with metric_cols[0]:
                st.metric("Average Interest", f"{metrics.average_interest:.1f}")

            with metric_cols[1]:
                st.metric("Peak Interest", metrics.peak_interest)

            with metric_cols[2]:
                st.metric("Trend", metrics.trend_direction.title())

            with metric_cols[3]:
                st.metric("Volatility", f"{metrics.volatility:.2f}")

            with metric_cols[4]:
                st.metric("Data Points", metrics.search_count)

            if metrics.peak_date:
                st.info(f"🔝 Peak interest on: **{metrics.peak_date}**")

            # Interest over time
            st.subheader("Interest Over Time")
            interest_data = get_cached_interest_over_time((keyword,), timeframe)

            if not interest_data.empty:
                fig = st.session_state.visualizer.create_interactive_comparison(interest_data)
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Export Interest Data")
                render_export_section(interest_data, export_format, f"interest_over_time_{keyword.replace(' ', '_')}")
            else:
                st.warning("No trend data returned for this keyword and timeframe.")

            # Seasonal trends
            st.subheader("Seasonal Patterns")
            seasonal = get_cached_seasonal(keyword)

            if seasonal:
                seasonal_df = pd.DataFrame(list(seasonal.items()), columns=["Month", "Interest"])
                fig = go.Figure(data=[go.Scatter(x=seasonal_df["Month"], y=seasonal_df["Interest"], mode="lines+markers")])
                fig.update_layout(title="Interest by Month", xaxis_title="Month", yaxis_title="Interest Level")
                st.plotly_chart(fig, use_container_width=True)
                render_export_section(seasonal_df, export_format, f"seasonal_patterns_{keyword.replace(' ', '_')}")

            # Related queries
            st.subheader("Related Queries")
            related = get_cached_related_queries(keyword)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Top Related Queries**")
                if "top" in related and not related["top"].empty:
                    for idx, row in related["top"].head(10).iterrows():
                        st.write(f"• {row['query']}")
                else:
                    st.caption("No top related queries returned")

            with col2:
                st.write("**Rising Related Queries**")
                if "rising" in related and not related["rising"].empty:
                    for idx, row in related["rising"].head(10).iterrows():
                        st.write(f"• {row['query']} (+{row['value']}%)")
                else:
                    st.caption("No rising related queries returned")

            if related:
                export_related = {}
                if "top" in related and isinstance(related["top"], pd.DataFrame) and not related["top"].empty:
                    export_related["top"] = related["top"].to_dict(orient="records")
                if "rising" in related and isinstance(related["rising"], pd.DataFrame) and not related["rising"].empty:
                    export_related["rising"] = related["rising"].to_dict(orient="records")

                if export_related and export_format == "JSON":
                    st.download_button(
                        "Download Related Queries JSON",
                        data=json.dumps(export_related, indent=2),
                        file_name=f"related_queries_{keyword.replace(' ', '_')}.json",
                        mime="application/json",
                        use_container_width=True,
                    )

            st.session_state.last_analysis = {
                "keyword": keyword,
                "metrics": metrics,
                "data": interest_data
            }

elif analysis_type == "Compare Keywords":
    st.header("Compare Multiple Keywords")

    keyword_input = st.text_input(
        "Enter keywords to compare (comma-separated, max 5)",
        placeholder="e.g., python, java, javascript"
    )

    if keyword_input:
        keywords = normalize_keywords(keyword_input, max_items=5)

        if not keywords:
            st.warning("Enter at least one valid keyword.")
            st.stop()

        if len(keywords) == 1:
            st.info("Add more keywords for a richer comparison.")

        with st.spinner("Comparing keywords..."):
            # Get comparison statistics
            stats_df = get_cached_comparison_stats(tuple(keywords), timeframe)

            st.subheader("Comparison Statistics")
            st.dataframe(stats_df, use_container_width=True)
            render_export_section(stats_df, export_format, "keyword_comparison_stats")

            # Interest over time
            st.subheader("Interest Trends")
            interest_data = get_cached_interest_over_time(tuple(keywords), timeframe)

            if not interest_data.empty:
                fig = st.session_state.visualizer.create_interactive_comparison(interest_data)
                st.plotly_chart(fig, use_container_width=True)
                render_export_section(interest_data, export_format, "keyword_comparison_interest")

                # Heatmap
                st.subheader("Trend Heatmap")
                weekly_data = interest_data.resample("W").mean()
                fig_heatmap = go.Figure(data=go.Heatmap(z=weekly_data.T.values, x=weekly_data.index, y=weekly_data.columns))
                fig_heatmap.update_layout(title="Keyword Interest Heatmap", height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.warning("No comparison trend data available for the selected keywords.")

elif analysis_type == "Regional Analysis":
    st.header("Regional Search Interest")

    keyword = st.text_input("Enter keyword to analyze by region", placeholder="e.g., machine learning")

    if keyword:
        with st.spinner(f"Analyzing regional trends for '{keyword}'..."):
            regional_data = get_cached_region((keyword,), resolution="country", timeframe=timeframe)

            if not regional_data.empty:
                st.subheader("Top 15 Regions")

                # Bar chart
                top_regions = regional_data.head(15)
                fig = go.Figure(data=[go.Bar(x=top_regions.iloc[:, 0].values, y=top_regions.index)])
                fig.update_layout(
                    title="Interest by Region",
                    xaxis_title="Interest Level (0-100)",
                    yaxis_title="Region",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Full Regional Data")
                st.dataframe(regional_data.sort_values(by=regional_data.columns[0], ascending=False), use_container_width=True)
                st.subheader("Export Regional Data")
                render_export_section(regional_data, export_format, f"regional_interest_{keyword.replace(' ', '_')}")
            else:
                st.warning("No regional data available for this keyword.")

elif analysis_type == "Seasonal Trends":
    st.header("Seasonal Trend Analysis")

    keyword = st.text_input("Enter keyword to analyze seasonal patterns", placeholder="e.g., christmas")

    if keyword:
        with st.spinner(f"Analyzing seasonal trends for '{keyword}'..."):
            seasonal = get_cached_seasonal(keyword)

            if seasonal:
                seasonal_df = pd.DataFrame(list(seasonal.items()), columns=["Month", "Interest"])

                # Line chart
                fig = go.Figure(data=[
                    go.Scatter(x=seasonal_df["Month"], y=seasonal_df["Interest"], mode="lines+markers+text", 
                              text=seasonal_df["Interest"].round(1), textposition="top center")
                ])
                fig.update_layout(
                    title="Seasonal Interest Pattern",
                    xaxis_title="Month",
                    yaxis_title="Average Interest Level",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

                # Statistics
                st.subheader("Statistics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Peak Month", seasonal_df.loc[seasonal_df["Interest"].idxmax(), "Month"])

                with col2:
                    st.metric("Peak Interest", f"{seasonal_df['Interest'].max():.1f}")

                with col3:
                    st.metric("Lowest Month", seasonal_df.loc[seasonal_df["Interest"].idxmin(), "Month"])

                st.dataframe(seasonal_df, use_container_width=True, hide_index=True)
                st.subheader("Export Seasonal Data")
                render_export_section(seasonal_df, export_format, f"seasonal_trends_{keyword.replace(' ', '_')}")
            else:
                st.warning("No seasonal trend data returned for this keyword.")

elif analysis_type == "GOOGL Stock Project":
    st.header("GOOGL Stock Analysis Project")
    st.caption("Interactive view of KPI outputs, enriched features, and project charts from data/GOOGL.csv")

    toolbar_left, toolbar_right = st.columns([3, 1])
    with toolbar_left:
        st.write("Use the button to rebuild outputs from the latest CSV before exploring metrics and charts.")
    with toolbar_right:
        if st.button("Rebuild Outputs", use_container_width=True):
            with st.spinner("Recomputing GOOGL project outputs..."):
                try:
                    rebuild_googl_outputs()
                    st.success("Outputs rebuilt successfully.")
                except Exception as exc:
                    st.error(f"Failed to rebuild outputs: {exc}")

    googl_df, googl_kpis = load_googl_outputs()

    if googl_df.empty or not googl_kpis:
        st.warning("GOOGL outputs were not found. Click 'Rebuild Outputs' to generate them from data/GOOGL.csv.")
        st.stop()

    metric_cols_top = st.columns(4)
    with metric_cols_top[0]:
        st.metric("Total Return", f"{googl_kpis.get('total_return_pct', 0)}%")
    with metric_cols_top[1]:
        st.metric("CAGR", f"{googl_kpis.get('cagr_pct', 0)}%")
    with metric_cols_top[2]:
        st.metric("Annualized Volatility", f"{googl_kpis.get('annualized_volatility_pct', 0)}%")
    with metric_cols_top[3]:
        st.metric("Max Drawdown", f"{googl_kpis.get('max_drawdown_pct', 0)}%")

    metric_cols_bottom = st.columns(4)
    with metric_cols_bottom[0]:
        st.metric("Best Day", f"{googl_kpis.get('best_day_return_pct', 0)}%")
    with metric_cols_bottom[1]:
        st.metric("Worst Day", f"{googl_kpis.get('worst_day_return_pct', 0)}%")
    with metric_cols_bottom[2]:
        st.metric("Trading Days", int(googl_kpis.get("trading_days", 0)))
    with metric_cols_bottom[3]:
        st.metric("Trend Signal", str(googl_kpis.get("trend_signal", "N/A")).upper())

    min_date = googl_df["Date"].min().date()
    max_date = googl_df["Date"].max().date()
    selected_range = st.date_input(
        "Filter Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = min_date, max_date

    filtered = googl_df[(googl_df["Date"].dt.date >= start_date) & (googl_df["Date"].dt.date <= end_date)].copy()

    if filtered.empty:
        st.warning("No rows in the selected date range.")
        st.stop()

    st.subheader("Price Trend with Moving Averages")
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["Adj Close"], mode="lines", name="Adj Close"))
    price_fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["sma_20"], mode="lines", name="SMA 20"))
    price_fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["sma_50"], mode="lines", name="SMA 50"))
    price_fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["sma_200"], mode="lines", name="SMA 200"))
    price_fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Price", hovermode="x unified")
    st.plotly_chart(price_fig, use_container_width=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Daily Return Distribution")
        returns = filtered["daily_return"].dropna()
        hist_fig = go.Figure(data=[go.Histogram(x=returns, nbinsx=70)])
        hist_fig.update_layout(height=400, xaxis_title="Daily Return", yaxis_title="Frequency")
        st.plotly_chart(hist_fig, use_container_width=True)

    with chart_col2:
        st.subheader("Drawdown Curve")
        dd_fig = go.Figure()
        dd_fig.add_trace(
            go.Scatter(
                x=filtered["Date"],
                y=filtered["drawdown"],
                mode="lines",
                fill="tozeroy",
                name="Drawdown",
            )
        )
        dd_fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Drawdown")
        st.plotly_chart(dd_fig, use_container_width=True)

    st.subheader("Volume and 30D Volume Z-Score")
    volume_fig = go.Figure()
    volume_fig.add_trace(go.Bar(x=filtered["Date"], y=filtered["Volume"], name="Volume", opacity=0.55))
    volume_fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["volume_zscore_30d"], mode="lines", name="Volume Z-Score (30D)", yaxis="y2"))
    volume_fig.update_layout(
        height=420,
        xaxis_title="Date",
        yaxis=dict(title="Volume"),
        yaxis2=dict(title="Z-Score", overlaying="y", side="right"),
        hovermode="x unified",
    )
    st.plotly_chart(volume_fig, use_container_width=True)

    st.subheader("Filtered Enriched Dataset")
    st.dataframe(filtered, use_container_width=True)
    render_export_section(filtered, export_format, "googl_enriched_filtered")

    if GOOGL_SUMMARY_PATH.exists():
        st.subheader("Text Summary")
        st.text(GOOGL_SUMMARY_PATH.read_text(encoding="utf-8"))

    png_candidates = [
        BASE_DIR / "reports" / "googl_price_trend.png",
        BASE_DIR / "reports" / "googl_returns_distribution.png",
        BASE_DIR / "reports" / "googl_drawdown.png",
    ]
    existing_pngs = [p for p in png_candidates if p.exists()]
    if existing_pngs:
        st.subheader("Generated PNG Reports")
        for path in existing_pngs:
            st.image(str(path), caption=path.name, use_container_width=True)

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by Pytrends")

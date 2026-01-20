import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_market_period_cards(metrics, label):
    """UI for Period Averages with perfect grid alignment."""
    st.markdown(f"#### 📊 {label}")

    with st.container(border=True):
        # We use 3 columns for both rows to maintain vertical alignment
        col1, col2, col3 = st.columns(3)

        # Row 1
        col1.metric("Avg Value", f"৳{metrics['total_value']:,.2f}M")
        col2.metric("Avg Volume", f"{metrics['total_volume']:,.0f}")
        col3.metric("Avg Return", f"{metrics['market_return']:+.3f}%")

        # Row 2 - Avg Breadth aligns with Avg Value; Volatility aligns with Avg Volume
        col1.metric("Avg Breadth", f"{metrics['breadth_pct']:.2f}%")
        col2.metric("Avg Volatility", f"{metrics['market_volatility']:.3f}%")
        # col3 is left empty to maintain the grid

def render_market_daily_timeline(daily_df, label):
    """UI for 'Daily' - Timeline of all 5 metrics"""
    st.markdown(f"#### {label} Daily Timeline")

    # Create a 5-row subplot
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("Value (Mn)", "Volume", "Return (%)", "Breadth (%)", "Volatility (%)")
    )

    metrics = [
        ('total_value', '#00CC96', 1),
        ('total_volume', '#636EFA', 2),
        ('market_return', '#EF553B', 3),
        ('breadth_pct', '#AB63FA', 4),
        ('market_volatility', '#FFA15A', 5)
    ]

    for col_name, color, row_idx in metrics:
        fig.add_trace(
            go.Scatter(x=daily_df['date'], y=daily_df[col_name], name=col_name, line=dict(color=color)),
            row=row_idx, col=1
        )

    fig.update_layout(height=900, showlegend=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_market_comparison_timeline(dfs_with_labels):
    """
    Overlays DSEX and DS30 with high visual distinction.
    dfs_with_labels: List of tuples [(df, label, color, dash_style), ...]
    """
    st.markdown("#### ⚖️ Market Comparison: DSEX vs DS30")

    # Define the 5 rows for the subplots
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=(
            "Total Value (Mn BDT)",
            "Total Volume",
            "Index Return (%)",
            "Market Breadth (% Positive)",
            "Volatility (%)"
        )
    )

    # Configuration for columns to plot
    metrics_config = [
        ('total_value', 1), ('total_volume', 2), ('market_return', 3),
        ('breadth_pct', 4), ('market_volatility', 5)
    ]

    # Plot each dataset
    for df, label, color, dash_style in dfs_with_labels:
        for col_name, row_idx in metrics_config:
            # Add trace with distinction
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df[col_name],
                    name=label,
                    legendgroup=label,
                    showlegend=(row_idx == 1),
                    line=dict(color=color, width=2.5, dash=dash_style),
                    # Add a subtle area fill for the first item (DSEX) to anchor it
                    fill='tozeroy' if (label == "DSEX" and row_idx != 3) else None,
                    fillcolor=f"rgba(99, 110, 250, 0.1)" if label == "DSEX" else None
                ),
                row=row_idx, col=1
            )

    # Enhance layout for readability
    fig.update_layout(
        height=1100,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=14)
        )
    )

    # Add a zero-line for Returns to distinguish Gainers from Losers
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1, row=3, col=1)
    # Add a 50% line for Breadth to distinguish Bullish vs Bearish sentiment
    fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1, row=4, col=1)

    st.plotly_chart(fig, use_container_width=True, key="market_comparison_distinguishable")
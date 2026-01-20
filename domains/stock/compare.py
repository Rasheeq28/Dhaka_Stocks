import streamlit as st


def get_relative_metrics(target_stats, benchmark_stats):
    """Calculates the performance delta for the Period Average view."""
    return {
        "Relative Return": target_stats['Avg Return'] - benchmark_stats['Avg Return'],
        "Volatility Gap": target_stats['Volatility'] - benchmark_stats['Volatility'],
        "Breadth Lead": target_stats['Pos. Days'] - benchmark_stats['Pos. Days']
    }


import streamlit as st


def render_relative_verdict(target_stats, bench_stats):
    """Displays the relative return verdict as requested."""
    rel_return = target_stats['Avg Return'] - bench_stats['Avg Return']

    if rel_return > 0:
        st.success(
            f"🚀 **{target_stats['Entity']}** is outperforming **{bench_stats['Entity']}** by **{rel_return:.2f}%** (Geometric Mean) over this period.")
    elif rel_return < 0:
        st.error(
            f"⚠️ **{target_stats['Entity']}** is underperforming **{bench_stats['Entity']}** by **{abs(rel_return):.2f}%** (Geometric Mean) over this period.")
    else:
        st.info(f"⚖️ **{target_stats['Entity']}** is performing exactly at par with **{bench_stats['Entity']}**.")
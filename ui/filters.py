
# ui/filters.py

import streamlit as st
from datetime import datetime, timedelta

def render_global_filters():
    st.sidebar.header("📅 Global Filters")

    today = datetime.now().date()
    default_start = today - timedelta(days=30)

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(default_start, today),
        help="Filter data across all tabs"
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    return {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d')
    }
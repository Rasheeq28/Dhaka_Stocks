import streamlit as st
from ui.filters import render_global_filters
from data.base_queries import fetch_market_data
from domains.market.compute import compute_daily_market_metrics, compute_period_averages
from domains.market.visuals import render_market_period_cards,render_market_daily_timeline
from domains.sector.compute import compute_daily_sector_category_metrics, \
compute_period_averages_grouped
from domains.sector.visuals import render_grouped_period_cards, render_grouped_timeline
from domains.stock.compute import calculate_stock_daily_timeline, calculate_period_comparison
from domains.stock.visuals import render_stock_daily_charts, render_comparison_cards
from domains.stock.compare import render_relative_verdict
# Standardized DS30 List
DS30_SYMBOLS = [
    'BATBC', 'BEACONPHAR', 'BRACBANK', 'BSC', 'BSCPLC',
    'BXPHARMA', 'CITYBANK', 'DELTALIFE', 'EBL', 'GP',
    'GPHISPAT', 'HEIDELBCEM', 'IDLC', 'JAMUNAOIL', 'KBPPWBIL',
    'KOHINOOR', 'LANKABAFIN', 'LHB', 'LINDEBD', 'LOVELLO',
    'MJLBD', 'OLYMPIC', 'PADMAOIL', 'PRIMEBANK', 'PUBALIBANK',
    'RENATA', 'ROBI', 'SQURPHARMA', 'UNIQUEHRL', 'WALTONHIL'
]


def main():
    st.set_page_config(page_title="dsex | Market Insights", layout="wide")
    st.title("📊 dsex Market Insights")

    # 1. Global Date Filters
    filters = render_global_filters()

    # 2. Index Scope Selection (Now the only toggle)
    # st.sidebar.subheader("Analysis Scope")
    # index_choice = st.sidebar.radio(
    #     "Select Index Group",
    #     ["DSEX (Full)", "DS30", "DSEX vs DS30"],
    #     help="Filter metrics for the entire market or the blue-chip DS30 list."
    # )

    # 3. Data Fetching
    raw_data = fetch_market_data(filters['start_date'], filters['end_date'])

    tab_market, tab_sector, tab_stock = st.tabs(["Market Overview", "Sector & Category Performance", "Stock Analysis"])
    with tab_market:
        # 1. Local Market Filters
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            market_choice = st.selectbox("Choose Market", ["DSEX", "DS30", "DSEX vs DS30"])
        with m_col2:
            # Unique key to prevent conflict with Stock tab
            calc_type = st.radio("Calculation Type", ["Period Average", "Daily"], horizontal=True, key="mkt_calc_type")

        if raw_data.empty:
            st.warning("No data available.")
        else:
            from domains.market.visuals import (
                render_market_period_cards,
                render_market_daily_timeline,
                render_market_comparison_timeline
            )

            # Execution Logic
            if market_choice == "DSEX":
                daily = compute_daily_market_metrics(raw_data, None)
                if calc_type == "Period Average":
                    avg = compute_period_averages(daily)
                    render_market_period_cards(avg, "DSEX Overall")
                else:
                    render_market_daily_timeline(daily, "DSEX Overall")

            elif market_choice == "DS30":
                daily = compute_daily_market_metrics(raw_data, DS30_SYMBOLS)
                if calc_type == "Period Average":
                    avg = compute_period_averages(daily)
                    render_market_period_cards(avg, "DS30 Index")
                else:
                    render_market_daily_timeline(daily, "DS30 Index")



            elif market_choice == "DSEX vs DS30":

                daily_dsex = compute_daily_market_metrics(raw_data, None)

                daily_ds30 = compute_daily_market_metrics(raw_data, DS30_SYMBOLS)

                if calc_type == "Daily":

                    render_market_comparison_timeline([

                        (daily_dsex, "DSEX", "#636EFA", "solid"),

                        (daily_ds30, "DS30", "#EF553B", "dash")

                    ])

                else:

                    # Use Vertical stacking with clear headers for comparison

                    # This ensures the numbers like "৳3,450.21M" have room to breathe

                    avg_dsex = compute_period_averages(daily_dsex)

                    avg_ds30 = compute_period_averages(daily_ds30)

                    # Render DSEX

                    render_market_period_cards(avg_dsex, "DSEX Overall")

                    st.markdown("---")  # Visual separator

                    # Render DS30

                    render_market_period_cards(avg_ds30, "DS30 Index")
    # Inside tab_sector
    with tab_sector:
        if raw_data.empty:
            st.warning("No data found.")
        else:
            # 1. Local Sector/Category Filters
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                market_choice = st.selectbox("Choose Market", ["DSEX", "DS30", "DSEX vs DS30"], key="sec_mkt")
            with s_col2:
                calc_type = st.radio("Calculation Type", ["Period Average", "Daily"], horizontal=True, key="sec_calc")

            sub_tab_sec, sub_tab_cat = st.tabs(["Sector Analytics", "Category Analytics"])

            # Define processing helper
            def process_sector_category(df, group_type, key):
                daily = compute_daily_sector_category_metrics(df, group_col=group_type)

                if calc_type == "Period Average":
                    avg = compute_period_averages_grouped(daily, group_col=group_type)
                    render_grouped_period_cards(avg, group_col=group_type)
                else:
                    render_grouped_timeline(daily, group_col=group_type, key_suffix=key)

            # --- SECTOR TAB ---
            with sub_tab_sec:
                if market_choice == "DSEX":
                    process_sector_category(raw_data, 'sector', 'dsex_sec')
                elif market_choice == "DS30":
                    ds30_data = raw_data[raw_data['trading_code'].isin(DS30_SYMBOLS)]
                    process_sector_category(ds30_data, 'sector', 'ds30_sec')
                else:  # Comparison
                    ds30_data = raw_data[raw_data['trading_code'].isin(DS30_SYMBOLS)]
                    st.subheader("DSEX (Full Market)")
                    process_sector_category(raw_data, 'sector', 'vs_dsex_sec')
                    st.divider()
                    st.subheader("DS30 (Blue-Chips)")
                    process_sector_category(ds30_data, 'sector', 'vs_ds30_sec')

            # --- CATEGORY TAB ---
            with sub_tab_cat:
                if market_choice == "DSEX":
                    process_sector_category(raw_data, 'category', 'dsex_cat')
                elif market_choice == "DS30":
                    ds30_data = raw_data[raw_data['trading_code'].isin(DS30_SYMBOLS)]
                    process_sector_category(ds30_data, 'category', 'ds30_cat')
                else:  # Comparison
                    ds30_data = raw_data[raw_data['trading_code'].isin(DS30_SYMBOLS)]
                    st.subheader("DSEX Categories")
                    process_sector_category(raw_data, 'category', 'vs_dsex_cat')
                    st.divider()
                    st.subheader("DS30 Categories")
                    process_sector_category(ds30_data, 'category', 'vs_ds30_cat')

    with tab_stock:
        if raw_data.empty:
            st.warning("No data found.")
        else:
            # --- 1. CONFIGURATION SECTION ---
            st.subheader("🛠️ Configure Analysis")

            f1, f2, f3 = st.columns(3)
            with f1:
                sel_sec = st.multiselect("Filter by Sector", sorted(raw_data['sector'].unique()))
            with f2:
                sel_cat = st.multiselect("Filter by Category", sorted(raw_data['category'].unique()))
            with f3:
                from domains.stock.queries import get_filtered_stock_list
                stock_list = get_filtered_stock_list(raw_data, sel_sec, sel_cat)
                target_stock = st.selectbox("Select Target Stock", stock_list)

            # --- 2. DYNAMIC BENCHMARK SELECTION ---
            c1, c2 = st.columns([2, 1])
            with c1:
                t_rows = raw_data[raw_data['trading_code'] == target_stock]
                t_info = t_rows.iloc[0] if not t_rows.empty else None

                # Build the list of potential benchmarks
                # 1. Broad Indices
                bench_opts = ["DSEX", "DS30"]

                # 2. Contextual Benchmarks (Sector/Category)
                if t_info is not None:
                    bench_opts.append(f"Sector: {t_info['sector']}")
                    bench_opts.append(f"Category: {t_info['category']}")

                # 3. Individual Stocks (Peer Comparison)
                all_tickers = sorted(raw_data['trading_code'].unique())
                # Remove target_stock from the peer list to avoid comparing a stock to itself
                if target_stock in all_tickers:
                    all_tickers.remove(target_stock)

                # Format peers so we can parse them easily
                peer_opts = [f"Stock: {t}" for t in all_tickers]
                bench_opts.extend(peer_opts)

                selected_bench = st.selectbox("Compare With (Benchmark / Peer)", bench_opts)

            with c2:
                calc_type = st.radio(
                    "Calculation Type",
                    ["Period Average", "Daily"],
                    horizontal=True,
                    key="stock_analysis_calc_type"
                )

            st.divider()

            # --- 3. PARSING & EXECUTION ---
            from domains.stock.compute import calculate_stock_daily_timeline, calculate_period_comparison
            from domains.stock.visuals import render_stock_daily_charts, render_comparison_cards
            from domains.stock.compare import render_relative_verdict

            # Parsing logic for all 4 types: Index, Sector, Category, and Peer Stock
            if ":" in selected_bench:
                parts = selected_bench.split(": ")
                b_type = parts[0].lower()  # 'sector', 'category', or 'stock'
                b_name = parts[1]
            else:
                b_type = "index"
                b_name = selected_bench  # 'DSEX' or 'DS30'

            # Inside tab_stock execution block
            if calc_type == "Daily":
                timeline_df = calculate_stock_daily_timeline(raw_data, target_stock, b_name, b_type)
                # Now passing b_name to show labels in the chart
                render_stock_daily_charts(timeline_df, target_stock, b_name)
            else:
                target_stats = calculate_period_comparison(raw_data, target_stock, "stock")
                bench_stats = calculate_period_comparison(raw_data, b_name, b_type)
                render_relative_verdict(target_stats, bench_stats)
                render_comparison_cards(target_stats, bench_stats)
if __name__ == "__main__":
    main()

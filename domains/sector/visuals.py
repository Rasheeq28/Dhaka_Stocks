# import streamlit as st
# import plotly.express as px
#
# # --- SECTOR ANALYSIS FUNCTIONS ---
#
# def render_sector_analysis(df, key_suffix=""):
#     """
#     Renders the static Period Average view (Treemap + Scorecard).
#     Used for single index views or within comparison columns.
#     """
#     if df.empty:
#         st.info("No data available for this selection.")
#         return
#
#     st.subheader("🎯 Sector Allocation (Period Average)")
#
#     # 1. Treemap
#     from domains.sector.compute import calculate_period_sector_metrics
#     metrics = calculate_period_sector_metrics(df)
#
#     fig_tree = px.treemap(
#         metrics,
#         path=['sector'],
#         values='total_value',
#         color='avg_return',
#         color_continuous_scale='RdYlGn',
#         title="Sector Value Share & Performance"
#     )
#     st.plotly_chart(fig_tree, use_container_width=True)
#
#     # 2. Scorecard
#     st.write("### Sector Scorecard")
#     sort_col = st.selectbox(
#         "Sort Scorecard By:",
#         ['avg_return', 'total_value', 'value_share', 'total_volume'],
#         key=f"sort_sec_{key_suffix}"
#     )
#
#     display_df = metrics.sort_values(sort_col, ascending=False)
#
#     styled_df = display_df.style.background_gradient(
#         subset=['avg_return', 'value_share'],
#         cmap='RdYlGn'
#     ).format({
#         'avg_return': '{:.2f}%',
#         'total_value': '{:.2f}M',
#         'value_share': '{:.2f}%',
#         'ad_ratio': '{:.2f}',
#         'total_volume': '{:,.0f}'
#     })
#     st.dataframe(styled_df, use_container_width=True, hide_index=True)
#
#
# def render_sector_timeline(daily_df_input, label="Market", key_suffix=""):
#     """
#     Renders sector timeline.
#     daily_df_input: Can be a single DataFrame or a list [df_dsex, df_ds30]
#     """
#     st.subheader(f"⏳ Sector Timeline: {label}")
#
#     # 1. Logic for Filters (Populated from the first/only DF)
#     ref_df = daily_df_input[0] if isinstance(daily_df_input, list) else daily_df_input
#     all_sectors = sorted(ref_df['sector'].unique())
#
#     col1, col2 = st.columns([2, 1])
#     with col1:
#         user_selection = st.multiselect(
#             "Select Sectors",
#             options=["Select All"] + all_sectors,
#             default=all_sectors[:3],
#             key=f"sel_sec_{key_suffix}"
#         )
#         final_sectors = all_sectors if "Select All" in user_selection else user_selection
#
#     with col2:
#         metrics_map = {
#             "Average Return (%)": "avg_return",
#             "Total Value (MN)": "total_value",
#             "Value Share (%)": "value_share",
#             "A/D Ratio": "ad_ratio",
#             "Total Volume": "total_volume"
#         }
#         sel_metric = st.selectbox("Metric", list(metrics_map.keys()), key=f"met_sec_{key_suffix}")
#         col_name = metrics_map[sel_metric]
#
#     # Plotting Helper
#     def plot_chart(df, title):
#         filtered = df[df['sector'].isin(final_sectors)]
#         if filtered.empty:
#             st.warning(f"No data for selected sectors in {title}")
#             return
#         fig = px.line(filtered, x='date', y=col_name, color='sector', markers=True, title=title)
#         fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
#         st.plotly_chart(fig, use_container_width=True)
#
#     # 2. Layout Logic
#     if isinstance(daily_df_input, list):
#         c1, c2 = st.columns(2)
#         with c1: plot_chart(daily_df_input[0], "DSEX Timeline")
#         with c2: plot_chart(daily_df_input[1], "DS30 Timeline")
#     else:
#         plot_chart(daily_df_input, f"{label} Timeline")
#
#
# def render_period_comparison(df_input, label="Sector", key_suffix=""):
#     """
#     Wrapper to handle the side-by-side Snapshot view for DSEX vs DS30.
#     """
#     if isinstance(df_input, list):
#         col1, col2 = st.columns(2)
#         with col1:
#             st.caption("🌐 DSEX Analysis")
#             render_sector_analysis(df_input[0], key_suffix=f"dsex_{key_suffix}")
#         with col2:
#             st.caption("💎 DS30 Analysis")
#             render_sector_analysis(df_input[1], key_suffix=f"ds30_{key_suffix}")
#     else:
#         render_sector_analysis(df_input, key_suffix=f"single_{key_suffix}")
#
#
# # --- CATEGORY ANALYSIS FUNCTIONS ---
#
# def render_category_timeline(daily_df_input, label="Market", key_suffix=""):
#     """
#     Renders category timeline for 'Throughout' mode.
#     """
#     st.subheader(f"⏳ Category Timeline: {label}")
#
#     ref_df = daily_df_input[0] if isinstance(daily_df_input, list) else daily_df_input
#     all_cats = sorted(ref_df['category'].unique())
#
#     col1, col2 = st.columns([2, 1])
#     with col1:
#         user_sel = st.multiselect(
#             "Select Categories",
#             options=["Select All"] + all_cats,
#             default=all_cats,
#             key=f"cat_sel_{key_suffix}"
#         )
#         final_cats = all_cats if "Select All" in user_sel else user_sel
#
#     with col2:
#         metrics_map = {
#             "Average Return (%)": "avg_return",
#             "Total Value (Daily)": "total_value",
#             "Value Share (%)": "value_share",
#             "A/D Ratio (Daily)": "ad_ratio",
#             "Total Daily Volume": "total_volume"
#         }
#         sel_metric = st.selectbox("Metric", list(metrics_map.keys()), key=f"cat_met_{key_suffix}")
#         col_name = metrics_map[sel_metric]
#
#     def plot_cat_chart(df, title):
#         filtered = df[df['category'].isin(final_cats)]
#         if filtered.empty:
#             st.warning(f"No data for categories in {title}")
#             return
#         fig = px.line(filtered, x='date', y=col_name, color='category', markers=True, title=title)
#         fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
#         st.plotly_chart(fig, use_container_width=True)
#
#     if isinstance(daily_df_input, list):
#         c1, c2 = st.columns(2)
#         with c1: plot_cat_chart(daily_df_input[0], "DSEX Category Trend")
#         with c2: plot_cat_chart(daily_df_input[1], "DS30 Category Trend")
#     else:
#         plot_cat_chart(daily_df_input, f"{label} Category Trend")
#
#
# def render_category_period_view(df, key_suffix=""):
#     """
#     Renders the card-style summary and scorecard for Categories.
#     """
#     if df.empty:
#         st.info("No data available.")
#         return
#
#     from domains.sector.compute import calculate_period_category_metrics
#     metrics = calculate_period_category_metrics(df)
#
#     # 1. Metric Cards
#     st.write("### Category Summary")
#     card_cols = st.columns(len(metrics))
#     for i, row in metrics.iterrows():
#         with card_cols[i]:
#             st.metric(
#                 label=f"Category {row['category']}",
#                 value=f"{row['avg_return']:.2f}%",
#                 delta=f"{row['value_share']:.1f}% Share"
#             )
#             st.caption(f"Val: {row['total_value']:.1f}M | Vol: {row['total_volume']:,.0f}")
#
#     # 2. Scorecard Table
#     st.write("---")
#     styled_df = metrics.style.background_gradient(subset=['avg_return'], cmap='RdYlGn').format({
#         'avg_return': '{:.2f}%',
#         'value_share': '{:.2f}%',
#         'total_value': '{:.2f}M',
#         'total_volume': '{:,.0f}',
#         'ad_ratio': '{:.2f}'
#     })
#     st.dataframe(styled_df, use_container_width=True, hide_index=True)


import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_grouped_period_cards(avg_df, group_col='sector'):
    """Displays avg metrics in a scannable format."""
    st.markdown(f"### {group_col.title()} Performance (Period Average)")

    for _, row in avg_df.iterrows():
        with st.expander(f"{group_col.title()}: {row[group_col]}", expanded=False):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Avg Value", f"{row['total_value']:.2f}M")
            c2.metric("Avg Return", f"{row['avg_return']:.2f}%")
            c3.metric("Weight", f"{row['value_share']:.1f}%")
            c4.metric("Breadth", f"{row['breadth_pct']:.1f}%")
            c5.metric("Volatility", f"{row['volatility']:.2f}%")


def render_grouped_timeline(daily_df, group_col='sector', key_suffix=""):
    """Interactive line charts for daily metrics."""
    groups = sorted(daily_df[group_col].unique())

    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.multiselect(f"Select {group_col.title()}", groups, default=groups[:3], key=f"sel_{key_suffix}")
    with col2:
        metric = st.selectbox("Select Metric",
                              ["avg_return", "total_value", "value_share", "breadth_pct", "volatility"],
                              key=f"met_{key_suffix}")

    filtered = daily_df[daily_df[group_col].isin(selected)]

    if not filtered.empty:
        fig = px.line(filtered, x='date', y=metric, color=group_col, markers=True,
                      title=f"Daily {metric.replace('_', ' ').title()} by {group_col.title()}")
        fig.update_layout(hovermode="x unified", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
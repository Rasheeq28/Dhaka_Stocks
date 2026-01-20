import pandas as pd
from scipy.stats import gmean


def compute_daily_sector_category_metrics(df, group_col='sector'):
    """Calculates daily metrics for either sector or category."""
    if df.empty: return pd.DataFrame()

    working_df = df.copy()
    working_df = working_df[working_df['ycp'] > 0].dropna(subset=['ltp', 'ycp'])
    working_df['stock_return'] = (working_df['ltp'] - working_df['ycp']) / working_df['ycp']

    def aggregate_group(group):
        total_unique = group['trading_code'].nunique()
        advancers = (group['stock_return'] > 0).sum()

        return pd.Series({
            "total_value": group['value_mn'].sum(),
            "total_volume": group['volume'].sum(),
            "avg_return": group['stock_return'].mean() * 100,
            "breadth_pct": (advancers / total_unique * 100) if total_unique > 0 else 0,
            "volatility": group['stock_return'].std() * 100,
            "stock_count": total_unique
        })

    # Group by Date AND the dimension (Sector/Category)
    daily_stats = working_df.groupby(['date', group_col]).apply(aggregate_group).reset_index()

    # Calculate Value Share per day
    daily_stats['mkt_total'] = daily_stats.groupby('date')['total_value'].transform('sum')
    daily_stats['value_share'] = (daily_stats['total_value'] / daily_stats['mkt_total']) * 100

    return daily_stats


def compute_period_averages_grouped(daily_df, group_col='sector'):
    """Averages the daily metrics over the period for each group."""
    if daily_df.empty: return pd.DataFrame()

    def summarize(group):
        # Geometric Mean Return
        returns_decimal = (group['avg_return'] / 100) + 1
        geo_mean = (gmean(returns_decimal[returns_decimal > 0]) - 1) * 100 if not group.empty else 0

        return pd.Series({
            "total_value": group['total_value'].mean(),
            "total_volume": group['total_volume'].mean(),
            "avg_return": geo_mean,
            "breadth_pct": group['breadth_pct'].mean(),
            "volatility": group['avg_return'].std(),  # Std dev of daily returns
            "value_share": group['value_share'].mean()
        })

    return daily_df.groupby(group_col).apply(summarize).reset_index()
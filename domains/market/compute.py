

import pandas as pd
import numpy as np
from scipy.stats import gmean

def compute_daily_market_metrics(df, stock_list=None):
    if df.empty:
        return pd.DataFrame()

    working_df = df.copy()
    if stock_list:
        working_df = working_df[working_df['trading_code'].isin(stock_list)]

    # Clean data
    working_df = working_df[working_df['ycp'] > 0].dropna(subset=['ltp', 'ycp'])
    working_df['stock_return'] = (working_df['ltp'] - working_df['ycp']) / working_df['ycp']

    def aggregate_day(group):
        total_unique_stocks = group['trading_code'].nunique()
        advancers = (group['stock_return'] > 0).sum()

        return pd.Series({
            "total_value": group['value_mn'].sum(),
            "total_volume": group['volume'].sum(),
            "market_return": group['stock_return'].mean() * 100,
            "breadth_pct": (advancers / total_unique_stocks * 100) if total_unique_stocks > 0 else 0,
            # This restores the column the chart is looking for:
            "market_volatility": group['stock_return'].std() * 100,
            "stock_count": total_unique_stocks
        })

    daily_metrics = working_df.groupby('date').apply(aggregate_day).reset_index()
    return daily_metrics

def compute_period_averages(daily_df):
    if daily_df.empty:
        return None

    # 1. Period Market Volatility (Standard deviation of the Market's daily returns)
    # This is the "True" volatility of the market as an index
    period_vol = daily_df['market_return'].std()

    # 2. Geometric Mean for the period
    returns_decimal = (daily_df['market_return'] / 100) + 1
    if (returns_decimal <= 0).any():
        geo_mean_return = np.nan
    else:
        geo_mean_return = (gmean(returns_decimal) - 1) * 100

    # 3. Arithmetic Averages for other metrics
    other_stats = daily_df[['total_value', 'total_volume', 'breadth_pct']].mean()

    return {
        "market_return": geo_mean_return,
        "market_volatility": period_vol, # This satisfies the 'market_period_cards'
        "total_value": other_stats['total_value'],
        "total_volume": other_stats['total_volume'],
        "breadth_pct": other_stats['breadth_pct']
    }
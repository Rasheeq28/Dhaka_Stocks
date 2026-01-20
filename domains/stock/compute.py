import pandas as pd
from scipy.stats import gmean

# Standardized DS30 List for internal filtering
DS30_SYMBOLS = [
    'BATBC', 'BEACONPHAR', 'BRACBANK', 'BSC', 'BSCPLC',
    'BXPHARMA', 'CITYBANK', 'DELTALIFE', 'EBL', 'GP',
    'GPHISPAT', 'HEIDELBCEM', 'IDLC', 'JAMUNAOIL', 'KBPPWBIL',
    'KOHINOOR', 'LANKABAFIN', 'LHB', 'LINDEBD', 'LOVELLO',
    'MJLBD', 'OLYMPIC', 'PADMAOIL', 'PRIMEBANK', 'PUBALIBANK',
    'RENATA', 'ROBI', 'SQURPHARMA', 'UNIQUEHRL', 'WALTONHIL'
]


def get_benchmark_df(df, name, b_type):
    """Helper to filter the dataframe based on benchmark selection."""
    if b_type == "index":
        if name == "DS30":
            return df[df['trading_code'].isin(DS30_SYMBOLS)]
        return df  # Default to DSEX (full market)
    elif b_type == "sector":
        return df[df['sector'] == name]
    elif b_type == "category":
        return df[df['category'] == name]
    elif b_type == "stock":
        # Handle individual stock as benchmark
        return df[df['trading_code'] == name]
    return df



def calculate_stock_daily_timeline(df, target_stock, benchmark_name, benchmark_type):
    # 1. Filter Target
    stock_df = df[df['trading_code'] == target_stock].copy().sort_values('date')
    stock_adtv = stock_df['value_mn'].mean()

    # 2. Daily Market Total (DSEX) for Liquidity Share
    market_total = df.groupby('date')['value_mn'].sum().rename('mkt_val')

    # 3. Filter Benchmark and calculate its daily metrics
    bench_df = get_benchmark_df(df, benchmark_name, benchmark_type)

    # Calculate Benchmark Daily stats (Aggregated if Sector/Index, individual if Stock)
    bench_daily = bench_df.groupby('date').agg(
        bench_ret=('ltp', lambda x: ((x - bench_df.loc[x.index, 'ycp']) / bench_df.loc[x.index, 'ycp']).mean() * 100),
        bench_val=('value_mn', 'sum')
    ).reset_index()

    bench_adtv = bench_daily['bench_val'].mean()

    # 4. Combine everything
    merged = stock_df.merge(market_total, on='date', how='left')
    merged = merged.merge(bench_daily, on='date', how='left')

    # 5. Build Timeline
    timeline = pd.DataFrame({
        'date': merged['date'],
        'Daily Return': ((merged['ltp'] - merged['ycp']) / merged['ycp']) * 100,
        'Bench Return': merged['bench_ret'],
        'Daily Traded Value': merged['value_mn'],
        'Bench Traded Value': merged['bench_val'],
        'Liquidity Share': (merged['value_mn'] / merged['mkt_val'] * 100),
        'Excess Return vs Market': (((merged['ltp'] - merged['ycp']) / merged['ycp']) * 100) - merged['bench_ret'],
        'Participation Index': (merged['value_mn'] / stock_adtv) if stock_adtv > 0 else 0,
        'Bench Participation Index': (merged['bench_val'] / bench_adtv) if bench_adtv > 0 else 0
    })

    return timeline
# def calculate_period_comparison(df, entity_name, entity_type):
#     """Calculates Period Average pillars for Stock, Sector, Category, or Index."""
#     # Robust filtering logic
#     if entity_type == "stock":
#         work_df = df[df['trading_code'] == entity_name].copy()
#     else:
#         # Use the helper to handle DS30, Sector, and Category correctly
#         work_df = get_benchmark_df(df, entity_name, entity_type)
#
#     if work_df.empty:
#         return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}
#
#     # Group by date to get daily average metrics for the entity group
#     daily_stats = work_df.groupby('date').agg(
#         ret_ratio=('ltp', lambda x: (x / work_df.loc[x.index, 'ycp']).mean()),
#         val=('value_mn', 'sum')
#     )
#
#     return {
#         "Entity": entity_name,
#         "Avg Return": (daily_stats['ret_ratio'].prod() ** (1 / len(daily_stats)) - 1) * 100,
#         "Volatility": (daily_stats['ret_ratio'] - 1).std() * 100,
#         "Pos. Days": (daily_stats['ret_ratio'] > 1).mean() * 100,
#         "ADTV": daily_stats['val'].mean(),
#         "Total Volume": work_df['volume'].sum()
#     }

# def calculate_period_comparison(df, entity_name, entity_type):
#     """Calculates Period Average pillars using the Market Logic (Standard Dev + GMean)."""
#
#     # 1. Robust filtering logic
#     if entity_type == "stock":
#         work_df = df[df['trading_code'] == entity_name].copy()
#     else:
#         work_df = get_benchmark_df(df, entity_name, entity_type)
#
#     if work_df.empty:
#         return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}
#
#     # 2. Daily Aggregation (Matches compute_daily_market_metrics theory)
#     # First, calculate individual daily returns for all stocks in the working set
#     work_df = work_df[work_df['ycp'] > 0].copy()
#     work_df['daily_ret_pct'] = ((work_df['ltp'] - work_df['ycp']) / work_df['ycp']) * 100
#
#     # Group by date to get the "Entity's Market Return" for that day
#     daily_stats = work_df.groupby('date').agg(
#         market_return=('daily_ret_pct', 'mean'),
#         total_val=('value_mn', 'sum'),
#         total_vol=('volume', 'sum')
#     ).reset_index()
#
#     if daily_stats.empty:
#         return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}
#
#     # 3. Apply Period Average Logic (Matches compute_period_averages theory)
#
#     # A. Volatility: Standard deviation of the daily percentage returns
#     period_vol = daily_stats['market_return'].std()
#
#     # B. Geometric Mean: Convert % to decimal (1.0x) and use gmean
#     returns_decimal = (daily_stats['market_return'] / 100) + 1
#
#     # Safety check for non-positive values before gmean
#     if (returns_decimal <= 0).any():
#         geo_mean_return = 0  # Or np.nan
#     else:
#         # Using scipy.stats.gmean as in your market code
#         geo_mean_return = (gmean(returns_decimal) - 1) * 100
#
#     return {
#         "Entity": entity_name,
#         "Avg Return": geo_mean_return,
#         "Volatility": period_vol,
#         "Pos. Days": (daily_stats['market_return'] > 0).mean() * 100,
#         "ADTV": daily_stats['total_val'].mean(),
#         "Total Volume": work_df['volume'].sum()
#     }

def calculate_period_comparison(df, entity_name, entity_type):
    """Calculates Period Average pillars using exactly the same theory as market/compute.py."""

    # 1. Standardize the data filtering
    if entity_type == "stock":
        working_df = df[df['trading_code'] == entity_name].copy()
    else:
        # Use your helper to get the group (Sector/Index/Category)
        working_df = get_benchmark_df(df, entity_name, entity_type)

    if working_df.empty:
        return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}

    # 2. Daily Market Metrics Step (Mirroring compute_daily_market_metrics)
    # Filter out bad data like the market code does
    working_df = working_df[working_df['ycp'] > 0].dropna(subset=['ltp', 'ycp'])
    working_df['stock_return'] = (working_df['ltp'] - working_df['ycp']) / working_df['ycp']

    # Group by date to get the "Daily Market Return" for this entity
    daily_df = working_df.groupby('date').agg(
        market_return=('stock_return', lambda x: x.mean() * 100),  # Convert to %
        total_value=('value_mn', 'sum'),
        total_volume=('volume', 'sum')
    ).reset_index()

    if daily_df.empty:
        return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}

    # 3. Period Average Step (Mirroring compute_period_averages)

    # A. Volatility: Standard deviation of the daily percentage returns
    period_vol = daily_df['market_return'].std()

    # B. Geometric Mean: Convert % back to decimal (1.0x) for gmean
    returns_decimal = (daily_df['market_return'] / 100) + 1

    if (returns_decimal <= 0).any():
        geo_mean_return = 0
    else:
        # Matches your working theory perfectly
        geo_mean_return = (gmean(returns_decimal) - 1) * 100

    return {
        "Entity": entity_name,
        "Avg Return": geo_mean_return,
        "Volatility": period_vol,
        "Pos. Days": (daily_df['market_return'] > 0).mean() * 100,
        "ADTV": daily_df['total_value'].mean(),
        "Total Volume": working_df['volume'].sum()
    }
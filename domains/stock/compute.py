import pandas as pd

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

def calculate_period_comparison(df, entity_name, entity_type):
    """Calculates Period Average pillars with safety checks for inf/nan."""
    if entity_type == "stock":
        work_df = df[df['trading_code'] == entity_name].copy()
    else:
        work_df = get_benchmark_df(df, entity_name, entity_type)

    if work_df.empty:
        return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}

    # Group by date to get daily average metrics
    # We use a lambda that filters out zero YCP to prevent 'inf'
    daily_stats = work_df.groupby('date').agg(
        ret_ratio=('ltp', lambda x: (x / work_df.loc[x.index, 'ycp'].replace(0, np.nan)).mean()),
        val=('value_mn', 'sum')
    ).dropna()  # Remove any dates that resulted in NaN/Inf

    if daily_stats.empty:
        return {"Entity": entity_name, "Avg Return": 0, "Volatility": 0, "Pos. Days": 0, "ADTV": 0}

    # Calculation with safety checks
    try:
        # Geometric mean calculation
        product = daily_stats['ret_ratio'].prod()
        avg_ret = (product ** (1 / len(daily_stats)) - 1) * 100 if product > 0 else 0

        # Volatility check
        vol = (daily_stats['ret_ratio'] - 1).std() * 100
        if np.isnan(vol): vol = 0

    except Exception:
        avg_ret, vol = 0, 0

    return {
        "Entity": entity_name,
        "Avg Return": avg_ret,
        "Volatility": vol,
        "Pos. Days": (daily_stats['ret_ratio'] > 1).mean() * 100,
        "ADTV": daily_stats['val'].mean(),
        "Total Volume": work_df['volume'].sum()
    }
import pandas as pd
import time
from data.client import supabase_client
import streamlit as st

def fetch_market_data(start_date: str, end_date: str):
    """
    Fetches data from the partitioned dsex_prices table.
    Postgres automatically prunes partitions based on the .gte() and .lte() date filters.
    """
    all_rows = []
    page_size = 1000
    start_index = 0
    max_retries = 3

    while True:
        success = False
        for attempt in range(max_retries):
            try:
                # IMPORTANT: Keep the table name as 'dsex_prices' if you renamed the
                # partitioned table to 'dsex_prices' in the SQL swap step.
                response = (
                    supabase_client.table("dsex_prices")
                    .select("date, openp,ltp, closep, ycp, value_mn, volume, value_mn, trade,  dsex_mapper(trading_code, category, sector)")
                    .gte("date", start_date)  # These two lines trigger 'Partition Pruning'
                    .lte("date", end_date)
                    .order("date", desc=False)
                    .range(start_index, start_index + page_size - 1)
                    .execute()
                )
                data = response.data
                success = True
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    st.error(f"Database Connection Error: {e}")
                    return pd.DataFrame()

        if not data:
            break

        all_rows.extend(data)
        if len(data) < page_size:
            break

        start_index += page_size
        time.sleep(0.05)  # Reduced sleep since partitioning is faster

    df = pd.DataFrame(all_rows)

    if not df.empty:
        # Flattening nested join data
        if not df.empty:
            df['trading_code'] = df['dsex_mapper'].apply(
                lambda x: x.get('trading_code') if isinstance(x, dict) else None)
            df['sector'] = df['dsex_mapper'].apply(lambda x: x.get('sector') if isinstance(x, dict) else None)
            # ADD THIS LINE:
            df['category'] = df['dsex_mapper'].apply(lambda x: x.get('category') if isinstance(x, dict) else None)

            df.drop(columns=['dsex_mapper'], inplace=True)
        numeric_cols = ['ltp', 'closep', 'ycp', 'value_mn']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')

    return df
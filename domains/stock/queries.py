def get_filtered_stock_list(df, sectors=None, categories=None):
    if df.empty: return []
    temp_df = df.copy()
    if sectors:
        temp_df = temp_df[temp_df['sector'].isin(sectors)]
    if categories:
        temp_df = temp_df[temp_df['category'].isin(categories)]
    return sorted(temp_df['trading_code'].unique())
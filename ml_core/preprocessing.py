import pandas as pd
import numpy as np
import os

def load_data(data_dir='data'):
    """Loads the three datasets."""
    print("Loading datasets...")
    try:
        df_high = pd.read_csv(os.path.join(data_dir, 'water-level_turbidity-high.csv'))
        df_medium = pd.read_csv(os.path.join(data_dir, 'water-level_turbidity-medium.csv'))
        df_low = pd.read_csv(os.path.join(data_dir, 'water-level_turbidity-low.csv'))
        return df_high, df_medium, df_low
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def clean_and_tag_data(df, turbidity_label):
    """Cleans and tags a single dataset."""
    df = df.dropna().drop_duplicates()
    df['turbidity_category'] = turbidity_label
    return df

def prepare_master_dataset(df_high, df_medium, df_low):
    """Balances and merges datasets."""
    # Balancing
    min_len = min(len(df_high), len(df_medium), len(df_low))
    print(f"Balancing data to {min_len} samples per class...")
    df_high = df_high.sample(n=min_len, random_state=42)
    df_medium = df_medium.sample(n=min_len, random_state=42)
    df_low = df_low.sample(n=min_len, random_state=42)
    
    # Merge
    master_df = pd.concat([df_high, df_medium, df_low], ignore_index=True)
    return master_df

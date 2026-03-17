import pandas as pd
import logging
import numpy as np
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_zomato_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and preprocesses the raw Zomato DataFrame.
    
    Steps:
    1. Extract relevant columns.
    2. Handle missing or inconsistent values.
    3. Clean and parse 'rate' and 'approx_cost(for two people)'.
    4. Remove duplicate records.
    """
    logger.info("Starting data cleaning and preprocessing...")
    
    # 1. Keep only necessary columns
    columns_to_keep = [
        'name', 'url', 'location', 'rate', 
        'approx_cost(for two people)', 'cuisines', 'votes'
    ]
    df = df[columns_to_keep].copy()
    
    # Rename columns for easier access
    df.rename(columns={
        'approx_cost(for two people)': 'cost_for_two',
        'rate': 'rating'
    }, inplace=True)
    
    # 2. Handle missing values
    # We strictly need location, rating, and cuisines
    initial_len = len(df)
    df.dropna(subset=['location', 'rating', 'cuisines', 'cost_for_two'], inplace=True)
    logger.info(f"Dropped {initial_len - len(df)} rows with missing critical data.")
    
    # 3. Clean 'rating' column (e.g., '4.1/5', 'NEW', '-')
    def parse_rating(r):
        if pd.isna(r) or r == 'NEW' or r == '-':
            return np.nan
        try:
            # Extract out the 4.1 from '4.1/5' 
            return float(str(r).split('/')[0].strip())
        except Exception:
            return np.nan
            
    df['rating'] = df['rating'].apply(parse_rating)
    df.dropna(subset=['rating'], inplace=True) # Drop rows where rating was 'NEW' or '-'
    
    # 4. Clean 'cost_for_two' (e.g., '1,200', '800')
    def parse_cost(c):
        if pd.isna(c):
            return np.nan
        try:
            return float(str(c).replace(',', '').strip())
        except Exception:
            return np.nan
            
    df['cost_for_two'] = df['cost_for_two'].apply(parse_cost)
    df.dropna(subset=['cost_for_two'], inplace=True)
    
    # Normalize cuisines (lowercase)
    df['cuisines'] = df['cuisines'].str.lower()
    
    # Convert votes to integer
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    
    # 5. Drop Duplicates
    # Restaurants with the same name and location are considered duplicates
    before_dedup = len(df)
    df.drop_duplicates(subset=['name', 'location'], keep='first', inplace=True)
    logger.info(f"Dropped {before_dedup - len(df)} duplicate records based on name and location.")
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    logger.info(f"Data cleaning complete. Output contains {len(df)} records.")
    return df

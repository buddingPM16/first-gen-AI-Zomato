import pandas as pd
import numpy as np
import pytest
from data_preprocessor import clean_zomato_data

def test_clean_zomato_data():
    """
    Test Phase 2: Data Cleaning and Preprocessing.
    """
    # Create dummy raw dataframe
    raw_data = pd.DataFrame({
        'name': ['Spice Elephant', 'Spice Elephant', 'Jalsa', 'Unknown', 'Bad Cost Data', 'Bad Rating Data'],
        'url': ['url1', 'url1', 'url2', 'url3', 'url4', 'url5'],
        'location': ['Banashankari', 'Banashankari', 'Jayanagar', np.nan, 'Indiranagar', 'Koramangala'],
        'rate': ['4.1/5', '4.1/5', '3.8/5', '4.0/5', '3.0/5', 'NEW'],
        'approx_cost(for two people)': ['800', '800', '1,200', '500', 'one thousand', '600'],
        'cuisines': ['North Indian, Chinese', 'North Indian, Chinese', 'North Indian', 'South Indian', 'Italian', 'Cafe'],
        'votes': [77, 77, 50, 20, 10, 5],
        'extra_column': ['drop_me', 'drop_me', 'drop_me', 'drop_me', 'drop_me', 'drop_me']
    })
    
    cleaned_df = clean_zomato_data(raw_data)
    
    # 1. Check if extra columns are dropped
    assert 'extra_column' not in cleaned_df.columns
    assert 'cost_for_two' in cleaned_df.columns
    assert 'rating' in cleaned_df.columns
    
    # 2. Check duplicate removal (Spice Elephant is duplicated)
    assert len(cleaned_df[cleaned_df['name'] == 'Spice Elephant']) == 1
    
    # 3. Check missing handling (Unknown drops due to no location)
    assert 'Unknown' not in cleaned_df['name'].values
    
    # 4. Check parsing logic (rate should be float, cost should be correctly parsed ignoring commas, bad data dropped)
    # Jalsa rating should be 3.8
    jalsa = cleaned_df[cleaned_df['name'] == 'Jalsa'].iloc[0]
    assert jalsa['rating'] == 3.8
    assert jalsa['cost_for_two'] == 1200.0
    
    # Check that 'NEW' rating was dropped
    assert 'Bad Rating Data' not in cleaned_df['name'].values
    
    # Check that bad cost data 'one thousand' was dropped
    assert 'Bad Cost Data' not in cleaned_df['name'].values
    
    # 5. Check cuisines lowercasing
    assert jalsa['cuisines'] == 'north indian'
    
    # Final length should be exactly 2 (Spice Elephant, Jalsa)
    assert len(cleaned_df) == 2

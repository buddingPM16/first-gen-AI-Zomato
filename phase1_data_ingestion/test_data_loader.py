import pytest
from data_loader import load_zomato_dataset

def test_load_zomato_dataset():
    """
    Test Phase 1: Data Ingestion.
    Ensures that the dataset can be successfully downloaded and converted to a Pandas DataFrame.
    """
    df = load_zomato_dataset()
    
    # Check that the result is not None and not empty
    assert df is not None
    assert not df.empty, "DataFrame should not be empty."
    
    # Check that we have a significant number of rows
    assert len(df) > 0, "DataFrame should contain records."
    
    # Check that it has columns
    assert len(df.columns) > 0, "DataFrame should have columns."
    
    # Typical check to see it downloaded successfully by checking if it resolved into a dataframe object
    assert hasattr(df, 'head'), "Object should be a pandas DataFrame."

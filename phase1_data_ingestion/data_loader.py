import pandas as pd
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_zomato_dataset() -> pd.DataFrame:
    """
    Downloads and loads the Zomato Restaurant Recommendation dataset from Hugging Face.
    Returns:
        pd.DataFrame: The loaded dataset as a pandas DataFrame.
    """
    logger.info("Loading dataset 'ManikaSaini/zomato-restaurant-recommendation' from Hugging Face...")
    try:
        # Load dataset from Hugging Face Hub
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
        
        # Datasets typically have a 'train' split if there's only one split
        df = dataset['train'].to_pandas()
        
        logger.info(f"Successfully loaded dataset with {len(df)} records.")
        return df
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise

if __name__ == "__main__":
    df = load_zomato_dataset()
    print("\nDataset Info:")
    print(df.info())
    print("\nDataset Head:")
    print(df.head())

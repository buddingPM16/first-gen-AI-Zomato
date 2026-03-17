import sqlite3
import pandas as pd
import logging
import os
import sys

# Adding previous phases to path to reuse their functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from phase1_data_ingestion.data_loader import load_zomato_dataset
from phase2_data_cleaning.data_preprocessor import clean_zomato_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'zomato.db')

def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """
    Runs the full pipeline to download, clean, and store the Zomato data in SQLite.
    Also creates appropriate indices for fast querying.
    """
    logger.info("Starting Phase 3: Setup SQLite Database...")
    
    # Run Phase 1
    raw_df = load_zomato_dataset()
    
    # Run Phase 2
    clean_df = clean_zomato_data(raw_df)
    
    logger.info(f"Saving {len(clean_df)} records to SQLite DB at {DB_PATH}...")
    
    # Connect to DB and save
    conn = get_db_connection()
    clean_df.to_sql('restaurants', conn, if_exists='replace', index=False)
    
    # Create Indexes for fast querying (location, cuisines, rating, cost)
    cursor = conn.cursor()
    logger.info("Creating database indexes for quick filtering...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON restaurants(location);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON restaurants(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost ON restaurants(cost_for_two);")
    
    # Note: Cuisines is a comma-separated string, so we'll likely use LIKE '%cuisine%' for querying,
    # which doesn't directly benefit from standard B-Tree indexing, but we'll add it anyway just in case.
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cuisines ON restaurants(cuisines);")
    
    conn.commit()
    conn.close()
    logger.info("Phase 3 Database setup complete!")

from typing import Optional

def query_restaurants(place: str, cuisine: str, max_price: Optional[float] = None, min_rating: Optional[float] = None, top_n: int = 5):
    """
    Sample function to query the database given the user constraints.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT * FROM restaurants
    WHERE location LIKE ? 
      AND cuisines LIKE ?
    """
    params = [f"%{place}%", f"%{cuisine}%"]
    
    if max_price is not None:
        query += "  AND cost_for_two <= ?\n"
        params.append(max_price)
        
    if min_rating is not None:
        query += "  AND rating >= ?\n"
        params.append(min_rating)
        
    query += "ORDER BY rating DESC, votes DESC\nLIMIT ?"
    params.append(top_n)
    
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

if __name__ == "__main__":
    setup_database()
    
    # Test a quick query to verify it works
    logger.info("\nTesting a sample query: Italian in Indiranagar under 1500 with rating >= 4.0")
    results = query_restaurants(place="Indiranagar", cuisine="italian", max_price=1500, min_rating=4.0)
    for r in results:
        print(f"{r['name']} - {r['location']} - Rating: {r['rating']} - Cost: {r['cost_for_two']} - Cuisines: {r['cuisines']}")

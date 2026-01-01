#!/usr/bin/env python3
"""
Load NYC 311 CSV data into Postgres database.
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.config import get_database_url


def load_311_to_postgres():
    """
    Load NYC 311 data from CSV into Postgres.
    """
    # Read DATABASE_URL from environment or Streamlit secrets
    try:
        database_url = get_database_url()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    csv_path = "data/raw/311.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please run scripts/fetch_311.py first to download the data.")
        sys.exit(1)
    
    print(f"Loading data from {csv_path}...")
    
    # Load CSV with pandas
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df):,} rows from CSV")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Convert date columns to datetime
    print("Converting date columns...")
    df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
    df['closed_date'] = pd.to_datetime(df['closed_date'], errors='coerce')
    
    # Drop duplicates on unique_key keeping the latest row
    initial_count = len(df)
    df = df.drop_duplicates(subset='unique_key', keep='last')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed:,} duplicate rows (kept latest)")
    print(f"Prepared {len(df):,} rows for insertion")
    
    # Connect to Postgres
    try:
        print("Connecting to Postgres...")
        engine = create_engine(database_url)
        
        # TRUNCATE table before insert
        print("Truncating raw.nyc311_requests table...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE raw.nyc311_requests"))
            conn.commit()
        
        # Insert data using pandas to_sql
        print("Inserting data into raw.nyc311_requests...")
        df.to_sql(
            'nyc311_requests',
            engine,
            schema='raw',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        print(f"\n✓ Successfully inserted {len(df):,} rows into raw.nyc311_requests")
        
    except Exception as e:
        print(f"\nError loading data into Postgres: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_311_to_postgres()


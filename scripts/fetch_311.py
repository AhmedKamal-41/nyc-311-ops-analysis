#!/usr/bin/env python3
"""
Fetch NYC 311 data from Socrata API and save to CSV.
"""
import argparse
import requests
import pandas as pd
from datetime import datetime, timedelta
import sys


def fetch_311_data(days=30, limit=50000):
    """
    Fetch NYC 311 data from Socrata API.
    
    Args:
        days: Number of days to fetch (default 30)
        limit: Records per page (default 50000)
    
    Returns:
        pandas DataFrame with all fetched records
    """
    base_url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    
    # Calculate date filter
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_filter = f"created_date >= '{start_date.strftime('%Y-%m-%dT%H:%M:%S')}'"
    
    # Fields to select
    fields = [
        "unique_key", "created_date", "closed_date", "agency", 
        "complaint_type", "descriptor", "status", "borough", 
        "incident_zip", "city", "latitude", "longitude"
    ]
    select_fields = ",".join(fields)
    
    all_records = []
    offset = 0
    page = 1
    
    print(f"Fetching NYC 311 data from last {days} days...")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Page size: {limit:,} records\n")
    
    while True:
        params = {
            "$select": select_fields,
            "$where": date_filter,
            "$limit": limit,
            "$offset": offset,
            "$order": "unique_key"
        }
        
        try:
            print(f"Fetching page {page} (offset {offset:,})...", end=" ", flush=True)
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print("No more records.")
                break
            
            all_records.extend(data)
            print(f"Retrieved {len(data):,} records (total: {len(all_records):,})")
            
            # If we got fewer records than the limit, we've reached the end
            if len(data) < limit:
                break
            
            offset += limit
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data: {e}")
            sys.exit(1)
    
    # Convert to DataFrame
    if not all_records:
        print("\nNo records found.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    
    # Ensure columns are in the correct order
    df = df[fields]
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Fetch NYC 311 data from Socrata API"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to fetch (default: 30)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50000,
        help="Records per page (default: 50000)"
    )
    
    args = parser.parse_args()
    
    # Fetch data
    df = fetch_311_data(days=args.days, limit=args.limit)
    
    if df.empty:
        print("\nNo data to save.")
        return
    
    # Save to CSV
    output_path = "data/raw/311.csv"
    print(f"\nSaving to {output_path}...")
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Successfully saved {len(df):,} records to {output_path}")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Standalone Google Trends scraper - writes directly to PostgreSQL
Run: python run_google_trends.py
"""

from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

def main():
    print("🔍 Fetching Google Trends data...")
    
    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    keywords = ['measles', 'mmr vaccine', 'measles outbreak']
    
    # Get data
    pytrends.build_payload(keywords, cat=0, timeframe='today 3-m', geo='US', gprop='')
    df = pytrends.interest_over_time()
    
    if 'isPartial' in df.columns:
        df = df.drop('isPartial', axis=1)
    
    # Reshape to long format
    df = df.reset_index()
    df_long = df.melt(
        id_vars=['date'],
        value_vars=keywords,
        var_name='keyword',
        value_name='search_interest'
    )
    
    # Add metadata
    df_long['geo'] = 'US'
    df_long['scraped_at'] = datetime.now()
    df_long['keyword_group'] = 1
    df_long = df_long[['date', 'keyword', 'search_interest', 'keyword_group', 'geo', 'scraped_at']]
    
    print(f"📊 Fetched {len(df_long)} rows")
    
    # Write to PostgreSQL
    print("💾 Writing to PostgreSQL...")
    connection_string = 'postgresql://postgres:postgres@127.0.0.1:5432/biopulse'
    engine = create_engine(connection_string)
    
    try:
        df_long.to_sql(
            name='raw_google_trends',
            con=engine,
            schema='public',
            if_exists='append',
            index=False,
            method='multi'
        )
        print("✅ Successfully exported to PostgreSQL!")
        print(f"   Date range: {df_long['date'].min()} to {df_long['date'].max()}")
    except Exception as e:
        if 'duplicate key' in str(e).lower():
            print("⚠️ Data already exists (skipping duplicates)")
        else:
            print(f"❌ Error: {e}")
            raise
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()

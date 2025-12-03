#!/usr/bin/env python3
"""
Standalone NewsAPI scraper - writes directly to PostgreSQL
Run: python run_newsapi_scraper.py
"""

import os
from newsapi import NewsApiClient
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def scrape_news_articles():
    """Scrape measles/vaccine related news articles"""
    print("🔍 Fetching news articles...")
    
    api_key = os.getenv('NEWSAPI_KEY')
    
    if not api_key:
        print("❌ NEWSAPI_KEY not found in .env file!")
        print("   Get your free key at: https://newsapi.org/")
        return pd.DataFrame()
    
    newsapi = NewsApiClient(api_key=api_key)
    
    queries = [
        'measles outbreak',
        'measles vaccine',
        'MMR vaccine',
        'anti-vax measles'
    ]
    
    all_articles = []
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    for query in queries:
        try:
            print(f"   Searching: {query}")
            response = newsapi.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            
            for article in response.get('articles', []):
                all_articles.append({
                    'article_url': article.get('url', ''),
                    'query_category': query[:50],
                    'source_name': article.get('source', {}).get('name', 'Unknown')[:100],
                    'author': article.get('author', '')[:200] if article.get('author') else None,
                    'title': article.get('title', ''),
                    'description': article.get('description', '') if article.get('description') else None,
                    'content': article.get('content', '') if article.get('content') else None,
                    'published_at': article.get('publishedAt'),
                    'scraped_at': datetime.now()
                })
                
        except Exception as e:
            print(f"   ⚠️ Error for query '{query}': {e}")
            continue
    
    if all_articles:
        df = pd.DataFrame(all_articles)
        df = df.drop_duplicates(subset=['article_url'], keep='first')
        print(f"📊 Found {len(df)} unique articles")
        return df
    else:
        print("⚠️ No articles found")
        return pd.DataFrame()

def main():
    df = scrape_news_articles()
    
    if df.empty:
        print("❌ No data to export")
        return
    
    print("💾 Writing to PostgreSQL...")
    connection_string = 'postgresql://postgres:postgres@127.0.0.1:5432/biopulse'
    engine = create_engine(connection_string)
    
    df.to_sql(
        name='raw_news_articles',
        con=engine,
        schema='public',
        if_exists='append',
        index=False
    )
    engine.dispose()
    
    print("✅ Successfully exported news articles to PostgreSQL!")
    print(f"   Date range: {df['published_at'].min()} to {df['published_at'].max()}")

if __name__ == '__main__':
    main()

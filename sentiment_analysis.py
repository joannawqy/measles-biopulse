#!/usr/bin/env python3
"""
Sentiment Analysis for News Articles
Analyzes sentiment of measles-related news and stores results
"""

import pandas as pd
from sqlalchemy import create_engine
from textblob import TextBlob
from datetime import datetime

def analyze_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    Returns: (polarity, subjectivity, sentiment_label)
    - polarity: -1 (negative) to 1 (positive)
    - subjectivity: 0 (objective) to 1 (subjective)
    """
    if not text or pd.isna(text):
        return 0.0, 0.0, 'neutral'
    
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return polarity, subjectivity, label
    except:
        return 0.0, 0.0, 'neutral'

def main():
    print("🧠 Running sentiment analysis on news articles...")
    
    # Connect to database
    connection_string = 'postgresql://postgres:postgres@127.0.0.1:5432/biopulse'
    engine = create_engine(connection_string)
    
    # Load news articles
    query = """
    SELECT id, title, description, published_at
    FROM raw_news_articles
    WHERE published_at IS NOT NULL
    ORDER BY published_at DESC
    """
    
    try:
        df = pd.read_sql(query, engine)
        print(f"📊 Analyzing {len(df)} articles...")
        
        if df.empty:
            print("⚠️ No articles found. Run newsapi scraper first.")
            return
        
        # Analyze sentiment
        results = []
        for idx, row in df.iterrows():
            # Combine title and description for analysis
            text = f"{row['title']} {row['description'] if pd.notna(row['description']) else ''}"
            
            polarity, subjectivity, label = analyze_sentiment(text)
            
            results.append({
                'article_id': row['id'],
                'sentiment_score': polarity,
                'subjectivity_score': subjectivity,
                'sentiment_label': label,
                'analyzed_at': datetime.now()
            })
        
        # Create DataFrame
        sentiment_df = pd.DataFrame(results)
        
        # Save to new table
        sentiment_df.to_sql(
            name='news_sentiment',
            con=engine,
            schema='public',
            if_exists='replace',
            index=False
        )
        
        # Summary statistics
        print("\n📈 Sentiment Analysis Summary:")
        print(f"   Total articles: {len(sentiment_df)}")
        print(f"   Positive: {len(sentiment_df[sentiment_df['sentiment_label'] == 'positive'])}")
        print(f"   Negative: {len(sentiment_df[sentiment_df['sentiment_label'] == 'negative'])}")
        print(f"   Neutral: {len(sentiment_df[sentiment_df['sentiment_label'] == 'neutral'])}")
        print(f"   Avg sentiment: {sentiment_df['sentiment_score'].mean():.3f}")
        print(f"   Avg subjectivity: {sentiment_df['subjectivity_score'].mean():.3f}")
        
        print("\n✅ Sentiment analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Risk Score Calculator
Combines Google Trends, CDC cases, and news sentiment into a risk score
"""

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import numpy as np

def calculate_risk_score():
    """
    Calculate outbreak risk score (0-100)
    
    Components:
    - Search interest trend (40%): Rising Google searches
    - Case growth (30%): CDC case increases  
    - News sentiment (30%): Negative news coverage
    """
    
    print("🎯 Calculating risk scores...")
    
    connection_string = 'postgresql://postgres:postgres@127.0.0.1:5432/biopulse'
    engine = create_engine(connection_string)
    
    try:
        # 1. Get Google Trends data (last 30 days)
        trends_query = """
        SELECT date, keyword, search_interest
        FROM raw_google_trends
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
        AND keyword = 'measles'
        ORDER BY date
        """
        trends_df = pd.read_sql(trends_query, engine)
        
        # 2. Get CDC cases
        cdc_query = """
        SELECT report_date, case_count
        FROM raw_cdc_cases
        ORDER BY report_date DESC
        LIMIT 10
        """
        cdc_df = pd.read_sql(cdc_query, engine)
        
        # 3. Get news sentiment (last 7 days)
        sentiment_query = """
        SELECT 
            DATE(published_at) as date,
            AVG(sentiment_score) as avg_sentiment,
            COUNT(*) as article_count
        FROM raw_news_articles n
        JOIN news_sentiment s ON n.id = s.article_id
        WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(published_at)
        ORDER BY date
        """
        
        try:
            sentiment_df = pd.read_sql(sentiment_query, engine)
        except:
            print("⚠️ No sentiment data found. Run sentiment_analysis.py first.")
            sentiment_df = pd.DataFrame()
        
        # Calculate component scores
        
        # 1. Search Interest Score (0-40 points)
        if not trends_df.empty and len(trends_df) >= 2:
            # Calculate trend (recent vs baseline)
            recent_avg = trends_df.tail(7)['search_interest'].mean()
            baseline_avg = trends_df['search_interest'].mean()
            
            if baseline_avg > 0:
                trend_change = (recent_avg - baseline_avg) / baseline_avg
                search_score = min(40, max(0, 20 + (trend_change * 40)))
            else:
                search_score = 20
        else:
            search_score = 20  # Default
        
        # 2. Case Growth Score (0-30 points)
        if not cdc_df.empty and len(cdc_df) >= 2:
            recent_cases = cdc_df.iloc[0]['case_count']
            baseline_cases = cdc_df['case_count'].mean()
            
            if baseline_cases > 0:
                case_change = (recent_cases - baseline_cases) / baseline_cases
                case_score = min(30, max(0, 15 + (case_change * 30)))
            else:
                case_score = 15
            
            # Absolute case threshold
            if recent_cases > 1000:
                case_score = min(30, case_score + 10)
        else:
            case_score = 15  # Default
        
        # 3. News Sentiment Score (0-30 points)
        if not sentiment_df.empty:
            avg_sentiment = sentiment_df['avg_sentiment'].mean()
            
            # Negative sentiment = higher risk
            # Scale: -1 (very negative) = 30 points, 0 (neutral) = 15 points, 1 (positive) = 0 points
            sentiment_score = max(0, min(30, 15 - (avg_sentiment * 15)))
        else:
            sentiment_score = 15  # Default neutral
        
        # Total Risk Score (0-100)
        total_risk = search_score + case_score + sentiment_score
        
        # Risk level
        if total_risk >= 70:
            risk_level = 'HIGH'
            risk_emoji = '🔴'
        elif total_risk >= 40:
            risk_level = 'MEDIUM'
            risk_emoji = '🟡'
        else:
            risk_level = 'LOW'
            risk_emoji = '🟢'
        
        # Create risk assessment
        risk_data = {
            'calculated_at': datetime.now(),
            'risk_score': round(total_risk, 2),
            'risk_level': risk_level,
            'search_interest_score': round(search_score, 2),
            'case_growth_score': round(case_score, 2),
            'news_sentiment_score': round(sentiment_score, 2),
            'total_articles_analyzed': len(sentiment_df) if not sentiment_df.empty else 0,
            'latest_case_count': int(cdc_df.iloc[0]['case_count']) if not cdc_df.empty else 0
        }
        
        # Save to database
        risk_df = pd.DataFrame([risk_data])
        risk_df.to_sql(
            name='risk_assessment',
            con=engine,
            schema='public',
            if_exists='append',
            index=False
        )
        
        # Display results
        print(f"\n{risk_emoji} RISK ASSESSMENT {risk_emoji}")
        print("="*50)
        print(f"Overall Risk Score: {total_risk:.1f}/100 ({risk_level})")
        print(f"\nComponent Breakdown:")
        print(f"  📈 Search Interest: {search_score:.1f}/40")
        print(f"  🏥 Case Growth:     {case_score:.1f}/30")
        print(f"  📰 News Sentiment:  {sentiment_score:.1f}/30")
        print(f"\nData Points:")
        print(f"  • Trends analyzed: {len(trends_df)} days")
        print(f"  • Latest cases: {risk_data['latest_case_count']:,}")
        print(f"  • News articles: {risk_data['total_articles_analyzed']}")
        print("="*50)
        print(f"\n✅ Risk assessment saved to database!")
        
    except Exception as e:
        print(f"❌ Error calculating risk: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == '__main__':
    calculate_risk_score()

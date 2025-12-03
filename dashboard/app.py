"""
BioPulse: Measles Tracker Dashboard
Streamlit application for visualizing Google Trends, CDC, and news data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

st.set_page_config(
    page_title="BioPulse: Measles Tracker",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_db_connection():
    """Create PostgreSQL connection"""
    try:
        conn_string = "postgresql://postgres:postgres@127.0.0.1:5432/biopulse"
        engine = create_engine(conn_string)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl=300)
def load_google_trends(_engine):
    """Load Google Trends search interest data"""
    query = "SELECT date, keyword, search_interest, geo FROM raw_google_trends ORDER BY date DESC"
    try:
        df = pd.read_sql(query, _engine)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.warning(f"Google Trends data unavailable: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_cdc_cases(_engine):
    """Load CDC measles case data"""
    query = "SELECT report_date, state, case_count, source_url FROM raw_cdc_cases ORDER BY report_date DESC"
    try:
        df = pd.read_sql(query, _engine)
        df['report_date'] = pd.to_datetime(df['report_date'])
        return df
    except Exception as e:
        st.warning(f"CDC data unavailable: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_news_articles(_engine):
    """Load news articles"""
    query = "SELECT published_at, title, description, source_name, query_category, article_url FROM raw_news_articles ORDER BY published_at DESC LIMIT 100"
    try:
        df = pd.read_sql(query, _engine)
        df['published_at'] = pd.to_datetime(df['published_at'])
        return df
    except Exception as e:
        st.warning(f"News data unavailable: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_data_stats(_engine):
    """Get row counts for each table"""
    stats = {}
    tables = ['raw_google_trends', 'raw_cdc_cases', 'raw_news_articles']
    
    for table in tables:
        try:
            result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", _engine)
            stats[table] = result['count'].iloc[0]
        except:
            stats[table] = 0
    
    return stats

def main():
    st.title("🦠 BioPulse: Measles Outbreak Tracker")
    st.markdown("**Real-time tracking of measles outbreaks using Google Trends, CDC data, and news sentiment**")
    
    st.sidebar.header("📊 Dashboard")
    
    engine = get_db_connection()
    
    if engine is None:
        st.error("⚠️ Cannot connect to database. Please ensure PostgreSQL is running.")
        return
    
    stats = get_data_stats(engine)
    
    st.sidebar.subheader("📊 Data Available")
    st.sidebar.metric("Google Trends", f"{stats.get('raw_google_trends', 0):,} rows")
    st.sidebar.metric("CDC Cases", f"{stats.get('raw_cdc_cases', 0):,} rows")
    st.sidebar.metric("News Articles", f"{stats.get('raw_news_articles', 0):,} articles")
    
    trends_df = load_google_trends(engine)
    cdc_df = load_cdc_cases(engine)
    news_df = load_news_articles(engine)
    
    if trends_df.empty and cdc_df.empty and news_df.empty:
        st.info("📭 **No data available yet.** Please run the scrapers to populate the database.")
        st.code("""
# Run individual scrapers
python run_google_trends.py
python run_cdc_scraper.py
python run_newsapi_scraper.py

# Or run all at once
python run_all_scrapers.py
        """, language="bash")
        return
    
    tab1, tab2, tab3 = st.tabs(["📈 Google Trends", "🏥 CDC Data", "📰 News Articles"])
    
    with tab1:
        if not trends_df.empty:
            st.subheader("📈 Google Trends: Search Interest Over Time")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                latest_date = trends_df['date'].max()
                st.metric("Latest Data", latest_date.strftime('%Y-%m-%d'))
            
            with col2:
                avg_interest = trends_df['search_interest'].mean()
                st.metric("Avg Search Interest", f"{avg_interest:.1f}")
            
            with col3:
                peak_interest = trends_df['search_interest'].max()
                st.metric("Peak Interest", f"{peak_interest}")
            
            trends_pivot = trends_df.pivot(index='date', columns='keyword', values='search_interest').reset_index()
            
            fig = go.Figure()
            
            keywords = ['measles', 'mmr vaccine', 'measles outbreak']
            colors = {'measles': 'red', 'mmr vaccine': 'blue', 'measles outbreak': 'orange'}
            
            for keyword in keywords:
                if keyword in trends_pivot.columns:
                    fig.add_trace(go.Scatter(
                        x=trends_pivot['date'],
                        y=trends_pivot[keyword],
                        name=keyword.title(),
                        mode='lines+markers',
                        line=dict(color=colors.get(keyword, 'gray'), width=2)
                    ))
            
            fig.update_layout(
                title="Search Interest Trends (0-100 scale)",
                xaxis_title="Date",
                yaxis_title="Search Interest",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📋 View Recent Data"):
                st.dataframe(trends_df.sort_values('date', ascending=False).head(20), use_container_width=True)
        else:
            st.info("No Google Trends data available. Run `python run_google_trends.py`")
    
    with tab2:
        if not cdc_df.empty:
            st.subheader("🏥 CDC Measles Case Data")
            
            total_cases = cdc_df['case_count'].sum()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Reported Cases", f"{total_cases:,}")
            
            with col2:
                latest_report = cdc_df['report_date'].max()
                st.metric("Latest Report", latest_report.strftime('%Y-%m-%d'))
            
            st.dataframe(cdc_df[['report_date', 'state', 'case_count', 'source_url']], use_container_width=True)
        else:
            st.info("No CDC data available. Run `python run_cdc_scraper.py`")
    
    with tab3:
        if not news_df.empty:
            st.subheader("📰 Recent Measles News Articles")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Articles", len(news_df))
            
            with col2:
                unique_sources = news_df['source_name'].nunique()
                st.metric("Unique Sources", unique_sources)
            
            with col3:
                latest_article = news_df['published_at'].max()
                st.metric("Latest Article", latest_article.strftime('%Y-%m-%d'))
            
            categories = ['All'] + sorted(news_df['query_category'].unique().tolist())
            selected_category = st.selectbox("Filter by Topic", categories)
            
            filtered_news = news_df if selected_category == 'All' else news_df[news_df['query_category'] == selected_category]
            
            source_counts = filtered_news['source_name'].value_counts().head(10)
            fig_sources = px.bar(
                x=source_counts.index,
                y=source_counts.values,
                labels={'x': 'News Source', 'y': 'Article Count'},
                title="Top News Sources"
            )
            st.plotly_chart(fig_sources, use_container_width=True)
            
            articles_per_day = filtered_news.groupby(filtered_news['published_at'].dt.date).size().reset_index()
            articles_per_day.columns = ['date', 'count']
            
            fig_timeline = px.line(
                articles_per_day,
                x='date',
                y='count',
                title="Articles Published Per Day",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            st.subheader("Latest Articles")
            for _, article in filtered_news.head(20).iterrows():
                with st.expander(f"📄 {article['title']}" + (f" ({article['published_at'].strftime('%Y-%m-%d')})" if pd.notna(article['published_at']) else "")):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if pd.notna(article['description']):
                            st.write(article['description'])
                    with col2:
                        st.write(f"**Source:** {article['source_name']}")
                        st.write(f"**Topic:** {article['query_category']}")
                        if pd.notna(article['article_url']):
                            st.link_button("Read More", article['article_url'])
        else:
            st.info("No news data available. Run `python run_newsapi_scraper.py`")

if __name__ == "__main__":
    main()

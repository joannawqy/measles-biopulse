# BioPulse: Measles Outbreak Tracker

Real-time measles outbreak monitoring system combining Google Trends, CDC data, and news sentiment analysis.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51-red.svg)](https://streamlit.io/)

## Overview

BioPulse is an automated data engineering project that monitors measles outbreak signals by integrating multiple data sources:

**Data Sources:**
- Google Trends: Public search interest as a leading indicator
- CDC: Official measles case reports
- NewsAPI: Media coverage and sentiment analysis

**Key Features:**
- Automated daily data collection
- NLP-powered sentiment analysis using TextBlob
- Risk scoring algorithm (0-100 scale)
- Interactive Streamlit dashboard
- PostgreSQL data warehouse
- Complete logging and monitoring

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for PostgreSQL)
- NewsAPI key (free at [newsapi.org](https://newsapi.org/))

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/measles-biopulse.git
cd measles-biopulse

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
# Edit .env and add your NEWSAPI_KEY

# Start PostgreSQL
docker-compose up -d

# Run complete pipeline
python run_full_pipeline.py

# Launch dashboard
streamlit run dashboard/app.py
```

Visit http://localhost:8501 to view the dashboard.

## Data Sources

### Google Trends
- Search interest for "measles", "mmr vaccine", "measles outbreak"
- 90-day rolling history
- No API key required

### CDC Cases
- Official measles case counts from CDC website
- Source: [CDC Measles Data](https://www.cdc.gov/measles/)
- Automated web scraping

### News Articles
- Measles-related news from 30+ sources
- 7-day lookback window
- Requires free NewsAPI key

## Architecture

**Data Pipeline:**
1. Data Collection: Python scrapers (Google Trends, CDC, NewsAPI)
2. Storage: PostgreSQL database
3. Analysis: TextBlob sentiment analysis + custom risk scoring
4. Visualization: Interactive Streamlit dashboard

**Tech Stack:**
- Language: Python 3.11
- Database: PostgreSQL 15
- NLP: TextBlob
- Dashboard: Streamlit + Plotly
- Orchestration: Cron jobs
- Infrastructure: Docker

## Project Structure

```
measles-biopulse/
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── run_google_trends.py        # Google Trends scraper
├── run_cdc_scraper.py          # CDC scraper
├── run_newsapi_scraper.py      # NewsAPI scraper
├── run_all_scrapers.py         # Master script
├── run_full_pipeline.py        # Complete pipeline (collection + analysis)
├── sentiment_analysis.py       # NLP sentiment analysis
├── calculate_risk_score.py     # Risk scoring algorithm
├── run_daily_scrapers.sh       # Cron-friendly wrapper script
├── init_db.sql                 # Database schema
├── docker-compose.yaml         # PostgreSQL service
├── requirements.txt            # Python dependencies
└── logs/                       # Daily execution logs
```

## Risk Scoring Algorithm

The risk score (0-100) combines three weighted components:

**Search Interest (40 points):**
- Monitors Google Trends for measles-related search spikes
- Compares recent 7-day average vs. 30-day baseline
- Higher scores indicate increased public concern

**Case Growth (30 points):**
- Tracks CDC reported case counts
- Compares latest reports vs. historical average
- Accounts for absolute case thresholds

**News Sentiment (30 points):**
- Analyzes sentiment of recent news articles using TextBlob
- Negative sentiment correlates with higher risk
- Weighted by article volume and recency

**Risk Levels:**
- LOW (0-39): Normal monitoring
- MEDIUM (40-69): Increased attention recommended
- HIGH (70-100): Potential outbreak conditions

## Automation

Set up daily automated execution:

```bash
# View current cron jobs
crontab -l

# Add daily execution at 6 AM
crontab -e

# Add this line:
0 6 * * * /path/to/measles-biopulse/run_daily_scrapers.sh
```

Logs are saved to `logs/scraper_YYYYMMDD.log`

## Testing

Run the complete test suite:

```bash
# Start services
docker-compose up -d

# Run pipeline
python run_full_pipeline.py

# Verify data
docker exec biopulse_postgres psql -U postgres -d biopulse -c "
  SELECT 'Google Trends' as source, COUNT(*) as rows FROM raw_google_trends
  UNION ALL SELECT 'CDC Cases', COUNT(*) FROM raw_cdc_cases
  UNION ALL SELECT 'News Articles', COUNT(*) FROM raw_news_articles;
"

# Check sentiment
docker exec biopulse_postgres psql -U postgres -d biopulse -c "
  SELECT sentiment_label, COUNT(*) FROM news_sentiment GROUP BY sentiment_label;
"

# View risk score
docker exec biopulse_postgres psql -U postgres -d biopulse -c "
  SELECT risk_score, risk_level FROM risk_assessment ORDER BY calculated_at DESC LIMIT 1;
"
```

## License

MIT License

## Acknowledgments

Data sources:
- Google Trends API (pytrends)
- CDC Measles Data
- NewsAPI

Technologies:
- Streamlit for dashboarding
- TextBlob for NLP
- PostgreSQL for data storage

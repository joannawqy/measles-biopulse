# 🦠 BioPulse: Measles Outbreak Tracker

> **Real-time measles outbreak monitoring using Google Trends, CDC data, and news sentiment analysis**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51-red.svg)](https://streamlit.io/)

## 🎯 Overview

BioPulse is an **automated data pipeline** that tracks measles outbreaks by combining:

1. **Google Trends** - Public search interest as a leading indicator
2. **CDC Data** - Official measles case reports
3. **News Articles** - Media coverage and sentiment

## ✨ Features

- ✅ **Automated Data Collection** - 3 scrapers run daily
- 📊 **Interactive Dashboard** - Real-time visualization with Streamlit
- 🗄️ **PostgreSQL Storage** - Structured data warehouse
- 📈 **Time Series Analysis** - Track trends over 90+ days
- 🔄 **Simple Setup** - No complex orchestration needed!

## 🚀 Quick Start

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

# Run scrapers
python run_all_scrapers.py

# Launch dashboard
streamlit run dashboard/app.py
```

Visit **http://localhost:8501** 🎉

## 📊 Data Sources

### 1. Google Trends 📈
- Search interest for "measles", "mmr vaccine", "measles outbreak"
- Daily updates, 90-day history
- No API key needed

### 2. CDC Cases 🏥
- Official measles case counts
- Source: [CDC Measles Data](https://www.cdc.gov/measles/)
- Web scraping

### 3. News Articles 📰
- Measles-related news from 30+ sources
- Last 7 days coverage
- Requires NewsAPI key

## 🛠️ Tech Stack

- **Data Collection:** Python, requests, BeautifulSoup, pytrends
- **Database:** PostgreSQL 15
- **Orchestration:** Cron (simple!)
- **Visualization:** Streamlit, Plotly
- **Infrastructure:** Docker

## 📁 Project Structure

```
measles-biopulse/
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── run_google_trends.py        # Google Trends scraper
├── run_cdc_scraper.py          # CDC scraper
├── run_newsapi_scraper.py      # NewsAPI scraper
├── run_all_scrapers.py         # Run all scrapers
├── init_db.sql                 # Database schema
├── docker-compose.yaml         # PostgreSQL service
└── requirements.txt            # Python dependencies
```

## ⏰ Automation

Set up daily data collection:

```bash
# Add to crontab
crontab -e

# Run at 6 AM daily
0 6 * * * cd /path/to/measles-biopulse && python run_all_scrapers.py
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [Google Trends](https://trends.google.com/)
- [CDC](https://www.cdc.gov/measles/)
- [NewsAPI](https://newsapi.org/)
- [Streamlit](https://streamlit.io/)

---

⭐ **Star this repo if you found it useful!**

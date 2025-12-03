-- BioPulse Database Schema
-- Measles Outbreak Tracker

-- Drop existing tables
DROP TABLE IF EXISTS raw_google_trends CASCADE;
DROP TABLE IF EXISTS raw_cdc_cases CASCADE;
DROP TABLE IF EXISTS raw_news_articles CASCADE;

-- Google Trends Data
CREATE TABLE raw_google_trends (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    search_interest INTEGER,
    keyword_group INTEGER,
    geo VARCHAR(10) DEFAULT 'US',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, keyword, geo)
);

CREATE INDEX idx_raw_trends_date ON raw_google_trends(date);
CREATE INDEX idx_raw_trends_keyword ON raw_google_trends(keyword);

-- CDC Cases
CREATE TABLE raw_cdc_cases (
    id SERIAL PRIMARY KEY,
    scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_date DATE,
    state VARCHAR(50),
    county VARCHAR(100),
    case_count INTEGER,
    source_url TEXT,
    raw_html TEXT,
    UNIQUE(report_date, state, county)
);

CREATE INDEX idx_raw_cdc_report_date ON raw_cdc_cases(report_date);
CREATE INDEX idx_raw_cdc_state ON raw_cdc_cases(state);

-- News Articles
CREATE TABLE raw_news_articles (
    id SERIAL PRIMARY KEY,
    article_url TEXT NOT NULL UNIQUE,
    query_category VARCHAR(50),
    source_name VARCHAR(100),
    author VARCHAR(200),
    title TEXT,
    description TEXT,
    content TEXT,
    published_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_news_category ON raw_news_articles(query_category);
CREATE INDEX idx_raw_news_published ON raw_news_articles(published_at);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ BioPulse database schema initialized successfully!';
    RAISE NOTICE '📊 Tables created: raw_google_trends, raw_cdc_cases, raw_news_articles';
END $$;

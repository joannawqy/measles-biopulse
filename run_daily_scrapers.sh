#!/bin/bash
# Daily BioPulse Data Collection Script
# This script runs all scrapers and logs results

# Set paths
PROJECT_DIR="/Users/mac/measles-biopulse"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/scraper_$(date +%Y%m%d).log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Start
log_message "=========================================="
log_message "Starting BioPulse Daily Data Collection"
log_message "=========================================="

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Run all scrapers
log_message "Running Google Trends scraper..."
/opt/anaconda3/bin/python run_google_trends.py >> "$LOG_FILE" 2>&1
TRENDS_EXIT=$?
log_message "Google Trends completed with exit code: $TRENDS_EXIT"

log_message "Running CDC scraper..."
/opt/anaconda3/bin/python run_cdc_scraper.py >> "$LOG_FILE" 2>&1
CDC_EXIT=$?
log_message "CDC scraper completed with exit code: $CDC_EXIT"

log_message "Running NewsAPI scraper..."
/opt/anaconda3/bin/python run_newsapi_scraper.py >> "$LOG_FILE" 2>&1
NEWS_EXIT=$?
log_message "NewsAPI scraper completed with exit code: $NEWS_EXIT"

# Summary
log_message "=========================================="
if [ $TRENDS_EXIT -eq 0 ] && [ $CDC_EXIT -eq 0 ] && [ $NEWS_EXIT -eq 0 ]; then
    log_message "✅ All scrapers completed successfully!"
    exit 0
else
    log_message "⚠️ Some scrapers failed. Check logs above."
    exit 1
fi

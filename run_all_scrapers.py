#!/usr/bin/env python3
"""
Run all BioPulse scrapers in sequence
Usage: python run_all_scrapers.py
"""

import subprocess
import sys
from datetime import datetime

def run_scraper(script_name):
    """Run a scraper script and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with error:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_name} timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    print("🚀 BioPulse Data Pipeline - Starting All Scrapers")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scrapers = [
        'run_google_trends.py',
        'run_cdc_scraper.py',
        'run_newsapi_scraper.py'
    ]
    
    results = {}
    
    for scraper in scrapers:
        results[scraper] = run_scraper(scraper)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    for scraper, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {scraper}")
    
    total = len(results)
    successful = sum(results.values())
    print(f"\n🎯 Total: {successful}/{total} scrapers succeeded")
    print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if successful == total else 1

if __name__ == '__main__':
    sys.exit(main())

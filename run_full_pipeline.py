#!/usr/bin/env python3
"""
Complete BioPulse Pipeline
Runs all steps: data collection → sentiment analysis → risk scoring
"""

import subprocess
import sys
from datetime import datetime

def run_step(step_name, script):
    """Run a pipeline step and report results"""
    print(f"\n{'='*60}")
    print(f"📍 Step: {step_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ {step_name} completed")
            return True
        else:
            print(f"❌ {step_name} failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {step_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 BioPulse Complete Pipeline")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    steps = [
        ("Data Collection", "run_all_scrapers.py"),
        ("Sentiment Analysis", "sentiment_analysis.py"),
        ("Risk Scoring", "calculate_risk_score.py")
    ]
    
    results = {}
    
    for step_name, script in steps:
        results[step_name] = run_step(step_name, script)
    
    # Final Summary
    print(f"\n{'='*60}")
    print("📊 PIPELINE SUMMARY")
    print(f"{'='*60}")
    
    for step_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step_name}")
    
    total = len(results)
    successful = sum(results.values())
    
    print(f"\n🎯 Result: {successful}/{total} steps completed")
    print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful == total:
        print("\n🎉 Pipeline completed successfully!")
        print("\n📊 Next: Check the dashboard at http://localhost:8501")
        return 0
    else:
        print("\n⚠️ Pipeline completed with errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())

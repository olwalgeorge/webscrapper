#!/usr/bin/env python3
"""
Direct test of mini_test_spider functionality
"""
import os
import sys
import subprocess
import json
import sqlite3
from datetime import datetime

def run_spider_test():
    """Run mini_test spider and analyze results"""
    print("=== DIRECT MINI SPIDER TEST ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.executable}")
    
    # Clean up previous results
    for file in ['crops.db', 'crops_data.json']:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Removed existing {file}")
    
    # Run spider with timeout
    try:
        print("=== RUNNING MINI_TEST SPIDER ===")
        cmd = [sys.executable, "-m", "scrapy", "crawl", "mini_test", "-L", "INFO"]
        
        result = subprocess.run(
            cmd,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        # Check results
        check_results()
        
    except subprocess.TimeoutExpired:
        print("❌ Spider timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Error running spider: {e}")

def check_results():
    """Check the results of scraping"""
    print("\n=== CHECKING RESULTS ===")
    
    # Check JSON file
    if os.path.exists('crops_data.json'):
        try:
            with open('crops_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ JSON: {len(data)} crops exported")
            for crop in data:
                print(f"  - {crop.get('name', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
    else:
        print("❌ No JSON file created")
    
    # Check database
    if os.path.exists('crops.db'):
        try:
            conn = sqlite3.connect('crops.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM crops")
            count = cursor.fetchone()[0]
            print(f"✓ Database: {count} crops stored")
            
            cursor.execute("SELECT name, water_needs, sun_requirements FROM crops")
            crops = cursor.fetchall()
            for crop in crops:
                print(f"  - {crop[0]}: water={bool(crop[1])}, sun={bool(crop[2])}")
            
            conn.close()
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    else:
        print("❌ No database file created")

if __name__ == "__main__":
    run_spider_test()

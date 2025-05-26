"""
Test script to validate DatabasePipeline with detailed logging
"""

import os
import sys
import sqlite3
from datetime import datetime
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.debug_test_spider import DebugTestSpider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('spider_test.log')
    ]
)

def run_spider_with_detailed_logging():
    """Run spider with detailed logging"""
    print("\n=== RUNNING SPIDER WITH DETAILED LOGGING ===")
    
    # Get project settings
    settings = get_project_settings()
    
    # Enable detailed logging
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('LOG_ENABLED', True)
    
    # Make sure DatabasePipeline is enabled
    settings.set('ITEM_PIPELINES', {
        'crop_scraper.pipelines.ValidationPipeline': 300,
        'crop_scraper.pipelines.DatabasePipeline': 400,
        'crop_scraper.pipelines.JsonWriterPipeline': 500,
    })
    
    # Reduce delays for testing
    settings.set('DOWNLOAD_DELAY', 1)
    settings.set('AUTOTHROTTLE_ENABLED', False)
    
    # Create and run spider
    process = CrawlerProcess(settings)
    process.crawl(DebugTestSpider)
    process.start()

def check_json_output():
    """Check if JSON output was created"""
    print("\n=== CHECKING JSON OUTPUT ===")
    if os.path.exists('crops_data.json'):
        with open('crops_data.json', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"JSON file size: {len(content)} characters")
            if content.strip():
                import json
                try:
                    data = json.loads(content)
                    print(f"JSON contains {len(data)} items")
                    if data:
                        print("First item keys:", list(data[0].keys()) if data else "No items")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
            else:
                print("JSON file is empty")
    else:
        print("No JSON file found")

def check_database_tables():
    """Check database structure"""
    print("\n=== CHECKING DATABASE STRUCTURE ===")
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Database tables: {[table[0] for table in tables]}")
        
        # Check crops table structure
        cursor.execute("PRAGMA table_info(crops)")
        crops_columns = cursor.fetchall()
        print(f"Crops table has {len(crops_columns)} columns")
        
        # Check nutrient_recipes table structure
        cursor.execute("PRAGMA table_info(nutrient_recipes)")
        recipes_columns = cursor.fetchall()
        print(f"Nutrient_recipes table has {len(recipes_columns)} columns")
        
        conn.close()
    else:
        print("No database file found")

def main():
    """Main test function"""
    print("Testing DatabasePipeline with detailed logging...")
    
    # Clean up previous files
    for file in ['crops_data.json', 'spider_test.log']:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed existing {file}")
    
    # Run spider
    try:
        run_spider_with_detailed_logging()
        print("\nSpider completed!")
    except Exception as e:
        print(f"\nError running spider: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check outputs
    check_json_output()
    check_database_tables()
    
    # Show log file if it exists
    if os.path.exists('spider_test.log'):
        print("\n=== SPIDER LOG ===")
        with open('spider_test.log', 'r') as f:
            log_content = f.read()
            print(log_content[-2000:])  # Show last 2000 characters
    
    print("\n=== DETAILED TEST COMPLETED ===")

if __name__ == "__main__":
    main()

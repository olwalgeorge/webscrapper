"""
Simple test script to validate DatabasePipeline
"""

import os
import sys
import sqlite3

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.debug_test_spider import DebugTestSpider


def run_spider():
    """Run spider with DatabasePipeline"""
    print("Running spider with DatabasePipeline...")
    
    # Get project settings
    settings = get_project_settings()
    
    # Configure settings
    settings.set('LOG_LEVEL', 'WARNING')  # Reduce log noise
    settings.set('ITEM_PIPELINES', {
        'crop_scraper.pipelines.ValidationPipeline': 300,
        'crop_scraper.pipelines.DatabasePipeline': 400,
        'crop_scraper.pipelines.JsonWriterPipeline': 500,
    })
    
    # Create and run spider
    process = CrawlerProcess(settings)
    process.crawl(DebugTestSpider)
    process.start()


def check_results():
    """Check spider results"""
    print("\n=== CHECKING RESULTS ===")
    
    # Check JSON output
    if os.path.exists('crops_data.json'):
        with open('crops_data.json', 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                import json
                data = json.loads(content)
                print(f"✓ JSON file created with {len(data)} items")
                if data:
                    item = data[0]
                    print(f"  Sample item: {item.get('name', 'Unknown')} from {item.get('source_url', 'Unknown')}")
            else:
                print("✗ JSON file is empty")
    else:
        print("✗ No JSON file created")
    
    # Check database
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"✓ Database created with tables: {tables}")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM crops")
        crops_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nutrient_recipes")
        recipes_count = cursor.fetchone()[0]
        
        print(f"✓ Database contains {crops_count} crops and {recipes_count} nutrient recipes")
        
        if crops_count > 0:
            cursor.execute("SELECT name, source_url FROM crops LIMIT 1")
            sample_crop = cursor.fetchone()
            print(f"  Sample crop: {sample_crop[0]} from {sample_crop[1]}")
        
        conn.close()
    else:
        print("✗ No database file created")


if __name__ == "__main__":
    try:
        run_spider()
        check_results()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

"""
Test script to validate DatabasePipeline functionality
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.debug_test_spider import DebugTestSpider


def check_database_before():
    """Check database state before running spider"""
    print("\n=== CHECKING DATABASE BEFORE SPIDER ===")
    
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Check crops table
        cursor.execute("SELECT COUNT(*) FROM crops")
        crops_count = cursor.fetchone()[0]
        print(f"Existing crops in database: {crops_count}")
        
        # Check recent entries
        cursor.execute("SELECT name, source_url, created_at FROM crops ORDER BY created_at DESC LIMIT 5")
        recent_crops = cursor.fetchall()
        print("Recent crops:")
        for crop in recent_crops:
            print(f"  - {crop[0]} from {crop[1]} at {crop[2]}")
        
        conn.close()
    else:
        print("Database file does not exist yet")


def check_database_after():
    """Check database state after running spider"""
    print("\n=== CHECKING DATABASE AFTER SPIDER ===")
    
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Check crops table
        cursor.execute("SELECT COUNT(*) FROM crops")
        crops_count = cursor.fetchone()[0]
        print(f"Total crops in database: {crops_count}")
        
        # Check recent entries
        cursor.execute("SELECT name, source_url, scraped_date, created_at FROM crops ORDER BY created_at DESC LIMIT 5")
        recent_crops = cursor.fetchall()
        print("Recent crops:")
        for crop in recent_crops:
            print(f"  - {crop[0]} from {crop[1]}")
            print(f"    Scraped: {crop[2]}")
            print(f"    Created: {crop[3]}")
        
        # Check nutrient_recipes table
        cursor.execute("SELECT COUNT(*) FROM nutrient_recipes")
        recipes_count = cursor.fetchone()[0]
        print(f"\nTotal nutrient recipes in database: {recipes_count}")
        
        if recipes_count > 0:
            cursor.execute("SELECT crop_name, fertilizer_type, source_url FROM nutrient_recipes ORDER BY created_at DESC LIMIT 3")
            recent_recipes = cursor.fetchall()
            print("Recent nutrient recipes:")
            for recipe in recent_recipes:
                print(f"  - {recipe[0]}: {recipe[1]} from {recipe[2]}")
        
        conn.close()
    else:
        print("Database file still does not exist!")


def run_spider_with_database():
    """Run spider with DatabasePipeline enabled"""
    print("\n=== RUNNING SPIDER WITH DATABASE PIPELINE ===")
    
    # Get project settings
    settings = get_project_settings()
    
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


def main():
    """Main test function"""
    print("Testing DatabasePipeline functionality...")
    
    # Check database state before
    check_database_before()
    
    # Run spider
    try:
        run_spider_with_database()
        print("\nSpider completed successfully!")
    except Exception as e:
        print(f"\nError running spider: {e}")
        return
    
    # Check database state after
    check_database_after()
    
    print("\n=== DATABASE PIPELINE TEST COMPLETED ===")


if __name__ == "__main__":
    main()

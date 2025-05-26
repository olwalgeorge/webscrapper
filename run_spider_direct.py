#!/usr/bin/env python3
"""
Direct Python execution of Scrapy spider
"""
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project to Python path
project_path = os.getcwd()
if project_path not in sys.path:
    sys.path.insert(0, project_path)

def run_spider_directly():
    """Run spider using CrawlerProcess"""
    print("=== DIRECT SPIDER EXECUTION TEST ===")
    print(f"Working directory: {os.getcwd()}")
    
    # Clean up previous results
    for file in ['crops.db', 'crops_data.json']:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Removed existing {file}")
    
    try:
        # Get project settings
        settings = get_project_settings()
        
        # Override some settings for debugging
        settings.update({
            'LOG_LEVEL': 'INFO',
            'LOG_ENABLED': True,
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 1,
            'CONCURRENT_REQUESTS': 1,
        })
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Import and add spider
        from crop_scraper.spiders.simple_mini_spider import SimpleMiniSpider
        process.crawl(SimpleMiniSpider)
        
        print("Starting spider...")
        process.start()  # This will block until finished
        
        print("Spider finished!")
        
    except Exception as e:
        print(f"❌ Error running spider: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_spider_directly()

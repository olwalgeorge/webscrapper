#!/usr/bin/env python3
"""
Simple test script for the mini spider
"""

import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project directory to Python path
project_dir = r'c:\Users\PC\byu classwork\wd330\project'
sys.path.insert(0, project_dir)

# Import the spider
from crop_scraper.spiders.mini_test_spider import MiniTestSpider

def run_mini_spider():
    print("Starting mini test spider...")
    
    # Get project settings
    settings = get_project_settings()
    
    # Override some settings for testing
    settings.update({
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.JsonWriterPipeline': 800,
        },
        'LOG_LEVEL': 'INFO'
    })
    
    # Create and configure the process
    process = CrawlerProcess(settings)
    
    # Add the spider to the process
    process.crawl(MiniTestSpider)
    
    # Start the reactor (this will block until the spider finishes)
    try:
        process.start()
        print("Spider completed successfully!")
    except Exception as e:
        print(f"Error running spider: {e}")

if __name__ == "__main__":
    run_mini_spider()

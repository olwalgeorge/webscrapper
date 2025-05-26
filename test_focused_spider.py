#!/usr/bin/env python3
"""
Test script for the focused almanac spider
"""

import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project directory to Python path
project_dir = r'c:\Users\PC\byu classwork\wd330\project'
sys.path.insert(0, project_dir)

# Import the spider
from crop_scraper.spiders.almanac_focused_spider import AlmanacFocusedSpider

def run_focused_spider():
    print("Starting focused almanac spider test...")
    
    # Get project settings
    settings = get_project_settings()
    
    # Override some settings for testing
    settings.update({
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 800,
        },
        'LOG_LEVEL': 'INFO'
    })
    
    # Create and configure the process
    process = CrawlerProcess(settings)
    
    # Add the spider to the process
    process.crawl(AlmanacFocusedSpider)
    
    # Start the reactor (this will block until the spider finishes)
    try:
        process.start()
        print("Spider completed successfully!")
    except Exception as e:
        print(f"Error running spider: {e}")

if __name__ == "__main__":
    run_focused_spider()

#!/usr/bin/env python3

import sys
import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('test_mini_spider.log'),
        logging.StreamHandler()
    ]
)

def run_mini_spider():
    """Run the mini test spider directly"""
    try:
        # Get project settings
        settings = get_project_settings()
        
        # Override settings for testing
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('FEEDS', {
            'test_mini_spider_output.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 2,
            }
        })
        
        # Create and configure process
        process = CrawlerProcess(settings)
        
        # Add spider
        process.crawl('mini_test')
        
        # Start the crawling process
        print("Starting mini test spider...")
        process.start()
        
        print("Mini test spider completed!")
        
    except Exception as e:
        print(f"Error running spider: {e}")
        logging.error(f"Error running spider: {e}", exc_info=True)

if __name__ == "__main__":
    run_mini_spider()

#!/usr/bin/env python3
"""
Test Scrapy programmatically to identify hanging issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json

def test_basic_scraping():
    """Test basic scraping functionality"""
    
    # Create a very simple spider inline
    import scrapy
    
    class TestSpider(scrapy.Spider):
        name = 'test'
        start_urls = ['http://httpbin.org/get']
        
        custom_settings = {
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 0,
            'LOG_LEVEL': 'INFO',
            'CLOSESPIDER_TIMEOUT': 10,  # Close after 10 seconds
        }
        
        def parse(self, response):
            print(f"SUCCESS: Got response from {response.url}")
            print(f"Status: {response.status}")
            yield {
                'url': response.url,
                'status': response.status,
                'success': True
            }
    
    try:
        # Get project settings
        settings = get_project_settings()
        settings.update({
            'ROBOTSTXT_OBEY': False,
            'LOG_LEVEL': 'INFO',
            'CLOSESPIDER_TIMEOUT': 10,
            'ITEM_PIPELINES': {},  # Disable all pipelines for testing
        })
        
        # Create and run crawler
        process = CrawlerProcess(settings)
        process.crawl(TestSpider)
        print("Starting crawler...")
        process.start()  # This will block until finished
        print("Crawler finished!")
        
    except Exception as e:
        print(f"Error running crawler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Scrapy functionality...")
    test_basic_scraping()
    print("Test completed!")

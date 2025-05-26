#!/usr/bin/env python3
"""
Test our crop spiders programmatically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.simple_test_spider import SimpleAlmanacSpider

def test_crop_scraping():
    """Test our crop scraping spider"""
    
    try:
        # Get project settings
        settings = get_project_settings()
        settings.update({
            'ROBOTSTXT_OBEY': False,
            'LOG_LEVEL': 'INFO',
            'CLOSESPIDER_TIMEOUT': 30,  # 30 second timeout
            'DOWNLOAD_DELAY': 1,
            'ITEM_PIPELINES': {
                'crop_scraper.pipelines.ValidationPipeline': 300,
                'crop_scraper.pipelines.JsonWriterPipeline': 800,
            },
            'FEEDS': {
                'test_output.json': {
                    'format': 'json',
                    'overwrite': True,
                },
            },
        })
        
        # Create and run crawler
        process = CrawlerProcess(settings)
        process.crawl(SimpleAlmanacSpider)
        print("Starting crop scraper...")
        process.start()  # This will block until finished
        print("Crop scraper finished!")
        
        # Check if we got any results
        if os.path.exists('test_output.json'):
            with open('test_output.json', 'r') as f:
                data = f.read()
                print(f"Output file size: {len(data)} characters")
                if data.strip():
                    import json
                    results = json.loads(data)
                    print(f"Number of items scraped: {len(results)}")
                    if results:
                        print("First item:")
                        print(json.dumps(results[0], indent=2))
                else:
                    print("Output file is empty")
        else:
            print("No output file generated")
            
    except Exception as e:
        print(f"Error running crawler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing crop scraping functionality...")
    test_crop_scraping()
    print("Test completed!")

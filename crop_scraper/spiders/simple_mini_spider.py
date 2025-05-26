#!/usr/bin/env python3
"""
Simplified mini test spider for debugging
"""
import scrapy
from crop_scraper.items import CropItem


class SimpleMiniSpider(scrapy.Spider):
    name = 'simple_mini'
    allowed_domains = ['almanac.com']
    
    start_urls = [
        'https://www.almanac.com/plant/tomatoes',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 500,
        },
        'LOG_LEVEL': 'DEBUG'
    }
    
    def parse(self, response):
        """Simple parse method with lots of logging"""
        self.logger.info(f"=== PARSING: {response.url} ===")
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"Response length: {len(response.body)}")
        
        # Test basic selectors
        h1_text = response.css('h1::text').get()
        self.logger.info(f"H1 text: {h1_text}")
        
        # Create item
        item = CropItem()
        item['name'] = 'Tomatoes'  # Simple hardcoded for testing
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
        item['water_needs'] = 'Test water needs'
        item['soil_ph'] = 'Test soil pH'
        
        self.logger.info(f"Created item: {item}")
        self.logger.info("=== YIELDING ITEM ===")
        
        yield item

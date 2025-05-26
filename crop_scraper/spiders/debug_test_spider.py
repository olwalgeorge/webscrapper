import scrapy
from crop_scraper.items import CropItem


class DebugTestSpider(scrapy.Spider):
    name = 'debug_test'
    allowed_domains = ['almanac.com']
      # Test with just one specific crop page
    start_urls = [
        'https://www.almanac.com/plant/tomatoes'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 800,
        },
        'LOG_LEVEL': 'DEBUG'
    }
    
    def parse(self, response):
        """Parse the tomato page for basic information"""
        self.logger.info(f"Successfully reached: {response.url}")
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        
        # Check if we got the right page
        page_text = response.css('body *::text').getall()
        self.logger.info(f"Found {len(page_text)} text elements on page")
        
        # Look for tomato-specific content
        tomato_words = [text for text in page_text if 'tomato' in text.lower()]
        self.logger.info(f"Found {len(tomato_words)} elements mentioning tomatoes")
        
        if len(tomato_words) > 0:
            self.logger.info(f"Sample tomato text: {tomato_words[0][:100]}")
        
        item = CropItem()
        
        # Extract basic information
        item['name'] = "Tomatoes"  # Hardcode for testing
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
        
        # Add some basic info
        item['water_needs'] = "Regular watering needed"
        item['sun_requirements'] = "Full sun"
        
        self.logger.info(f"Created item: {item}")
        yield item

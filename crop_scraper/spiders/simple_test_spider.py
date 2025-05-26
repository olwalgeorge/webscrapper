import scrapy
from crop_scraper.items import CropItem


class SimpleAlmanacSpider(scrapy.Spider):
    name = 'simple_almanac'
    allowed_domains = ['almanac.com']
    
    # Test with just one specific crop page
    start_urls = [
        'https://www.almanac.com/plant/tomatoes'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False,  # Disable for testing
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.JsonWriterPipeline': 800,
        }
    }
    
    def parse(self, response):
        """Parse the tomato page for basic information"""
        self.logger.info(f"Parsing page: {response.url}")
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        
        item = CropItem()
        
        # Extract basic information
        item['name'] = self.extract_name(response)
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
        
        # Extract what we can find
        item['water_needs'] = self.extract_text_containing(response, ['water', 'watering', 'irrigation'])
        item['soil_ph'] = self.extract_text_containing(response, ['ph', 'pH', 'acid', 'alkaline'])
        item['fertilizer_recommendations'] = self.extract_text_containing(response, ['fertilizer', 'feed', 'nutrients'])
        item['sun_requirements'] = self.extract_text_containing(response, ['sun', 'light', 'shade'])
        item['planting_depth'] = self.extract_text_containing(response, ['depth', 'plant', 'sow'])
        item['spacing'] = self.extract_text_containing(response, ['space', 'spacing', 'apart'])
        item['days_to_maturity'] = self.extract_text_containing(response, ['days', 'maturity', 'harvest'])
        
        self.logger.info(f"Extracted item: {item}")
        yield item
    
    def extract_name(self, response):
        """Extract crop name"""
        name_selectors = [
            'h1::text',
            '.page-title::text', 
            'title::text'
        ]
        
        for selector in name_selectors:
            name = response.css(selector).get()
            if name:
                # Clean up the name
                name = name.strip().replace(' | The Old Farmer\'s Almanac', '')
                if name and len(name) > 0:
                    return name
        
        return 'Unknown'
    
    def extract_text_containing(self, response, keywords):
        """Extract text that contains any of the given keywords"""
        text_content = response.css('*::text').getall()
        matching_texts = []
        
        for text in text_content:
            text = text.strip()
            if len(text) > 10:  # Ignore very short text
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        matching_texts.append(text)
                        break
        
        # Return first few matches, joined
        if matching_texts:
            return ' | '.join(matching_texts[:3])  # Limit to first 3 matches
        return None

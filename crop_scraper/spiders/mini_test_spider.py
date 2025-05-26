import scrapy
from crop_scraper.items import CropItem


class MiniTestSpider(scrapy.Spider):
    name = 'mini_test'
    allowed_domains = ['almanac.com']
      # Test with multiple specific crop pages
    start_urls = [
        'https://www.almanac.com/plant/tomatoes',
        'https://www.almanac.com/plant/carrots',
        'https://www.almanac.com/plant/lettuce',
        'https://www.almanac.com/plant/sweet-peppers',  # Fixed URL
        'https://www.almanac.com/plant/beans'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 500,
        },
        'LOG_LEVEL': 'INFO'
    }
    
    def parse(self, response):
        """Parse crop pages for basic information"""
        self.logger.info(f"Parsing page: {response.url}")
        
        item = CropItem()
        
        # Extract basic information
        item['name'] = self.extract_name(response)
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
          # Extract comprehensive information with better error handling
        try:
            # Extract data and convert lists to strings for database compatibility
            water_needs = self.extract_text_containing(response, ['water', 'watering', 'irrigation'])
            item['water_needs'] = ' | '.join(water_needs) if water_needs else ''
            
            soil_ph = self.extract_text_containing(response, ['ph', 'pH', 'acid', 'alkaline'])
            item['soil_ph'] = ' | '.join(soil_ph) if soil_ph else ''
            
            fertilizer_recs = self.extract_text_containing(response, ['fertilizer', 'feed', 'nutrients'])
            item['fertilizer_recommendations'] = ' | '.join(fertilizer_recs) if fertilizer_recs else ''
            
            sun_reqs = self.extract_text_containing(response, ['sun', 'light', 'shade'])
            item['sun_requirements'] = ' | '.join(sun_reqs) if sun_reqs else ''
            
            planting_depth = self.extract_text_containing(response, ['depth', 'plant', 'sow'])
            item['planting_depth'] = ' | '.join(planting_depth) if planting_depth else ''
            
            spacing = self.extract_text_containing(response, ['space', 'spacing', 'apart'])
            item['spacing'] = ' | '.join(spacing) if spacing else ''
            
            days_to_maturity = self.extract_text_containing(response, ['days', 'maturity', 'harvest'])
            item['days_to_maturity'] = ' | '.join(days_to_maturity) if days_to_maturity else ''
        except Exception as e:
            self.logger.error(f"Error extracting data from {response.url}: {e}")
        
        self.logger.info(f"Successfully extracted data for: {item.get('name', 'Unknown')}")
        yield item
    
    def extract_name(self, response):
        """Extract crop name"""
        # Try multiple selectors to find the crop name
        name_selectors = [
            'h1.page-title::text',
            'h1::text',
            '.plant-name::text',
            '.crop-name::text',
            'h1 span::text',
            '.entry-title::text'
        ]
        
        for selector in name_selectors:
            name = response.css(selector).get()
            if name:
                clean_name = name.strip()
                # Filter out common non-crop words
                if clean_name and not any(word in clean_name.lower() for word in ['almanac', 'calendar', 'growing', 'planting']):
                    return clean_name
        
        # Fallback to URL parsing
        url_parts = response.url.split('/')
        if 'plant' in url_parts:
            idx = url_parts.index('plant')
            if idx + 1 < len(url_parts):
                crop_name = url_parts[idx + 1].replace('-', ' ').title()
                return crop_name
        
        return 'Unknown'
    
    def extract_text_containing(self, response, keywords):
        """Extract text containing any of the specified keywords"""
        results = []
        
        # Look for content in specific content areas first
        content_selectors = [
            '.article-content p::text',
            '.content p::text', 
            '.plant-content p::text',
            'main p::text',
            '.entry-content p::text',
            'p::text'
        ]
        
        # Get text from content areas
        for selector in content_selectors:
            texts = response.css(selector).getall()
            if texts:
                break
        else:
            # Fallback to all text
            texts = response.css('*::text').getall()
        
        for text in texts:
            if not text:
                continue
            text = text.strip()
            # Only consider substantial text
            if len(text) > 20 and len(text) < 1000:  
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        # Clean up the text
                        cleaned_text = ' '.join(text.split())
                        # Filter out navigation and header text
                        if not any(nav_word in cleaned_text.lower() for nav_word in [
                            'navigation', 'menu', 'calendar', 'holiday', 'moon', 'sun',
                            'almanac', 'store', 'sunrise', 'set times', 'best days'
                        ]):
                            if cleaned_text not in results:
                                results.append(cleaned_text)
                        break
        
        return results[:3]  # Limit to top 3 relevant pieces of text

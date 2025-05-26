import scrapy
from scrapy import Request
from crop_scraper.items import CropItem
import re


class AlmanacFocusedSpider(scrapy.Spider):
    name = 'almanac_focused'
    allowed_domains = ['almanac.com']
    
    # Focus on specific popular crops to avoid infinite crawling
    crop_list = [
        'tomatoes', 'carrots', 'lettuce', 'onions', 'peppers', 'cucumbers',
        'beans', 'peas', 'corn', 'potatoes', 'cabbage', 'broccoli',
        'spinach', 'radishes', 'beets', 'squash', 'zucchini', 'herbs',
        'basil', 'parsley', 'cilantro', 'thyme', 'oregano', 'mint'
    ]
    
    start_urls = [f'https://www.almanac.com/plant/{crop}' for crop in crop_list]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 800,
        }
    }
    
    def parse(self, response):
        """Parse individual crop pages for nutrition and care information"""
        self.logger.info(f"Parsing crop page: {response.url}")
        
        # Check if page exists (not 404)
        if response.status != 200:
            self.logger.warning(f"Page not found: {response.url}")
            return
        
        item = CropItem()
        
        # Basic information
        item['name'] = self.extract_name(response)
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
        
        # Extract comprehensive information
        item['water_needs'] = self.extract_water_needs(response)
        item['soil_ph'] = self.extract_soil_ph(response)
        item['fertilizer_recommendations'] = self.extract_fertilizer_info(response)
        item['sun_requirements'] = self.extract_sun_requirements(response)
        item['planting_depth'] = self.extract_planting_depth(response)
        item['spacing'] = self.extract_spacing(response)
        item['days_to_maturity'] = self.extract_days_to_maturity(response)
        item['planting_season'] = self.extract_planting_season(response)
        item['harvest_time'] = self.extract_harvest_time(response)
        item['soil_type'] = self.extract_soil_type(response)
        item['temperature_range'] = self.extract_temperature_range(response)
        
        self.logger.info(f"Successfully extracted data for: {item.get('name', 'Unknown')}")
        yield item
    
    def extract_name(self, response):
        """Extract crop name from the page"""
        name_selectors = [
            'h1.page-title::text',
            'h1::text',
            '.plant-name::text',
            '.crop-name::text'
        ]
        
        for selector in name_selectors:
            name = response.css(selector).get()
            if name:
                return name.strip()
        
        # Fallback to URL parsing
        url_parts = response.url.split('/')
        if 'plant' in url_parts:
            idx = url_parts.index('plant')
            if idx + 1 < len(url_parts):
                return url_parts[idx + 1].replace('-', ' ').title()
        
        return ''
    
    def extract_water_needs(self, response):
        """Extract water requirements information"""
        water_keywords = ['water', 'watering', 'irrigation', 'moisture', 'drought']
        return self.extract_text_containing(response, water_keywords)
    
    def extract_soil_ph(self, response):
        """Extract soil pH information"""
        ph_keywords = ['ph', 'pH', 'acid', 'alkaline', 'neutral']
        return self.extract_text_containing(response, ph_keywords)
    
    def extract_fertilizer_info(self, response):
        """Extract fertilizer and nutrient information"""
        fertilizer_keywords = ['fertilizer', 'fertiliser', 'feed', 'nutrients', 'compost', 'npk', 'nitrogen', 'phosphorus', 'potassium']
        return self.extract_text_containing(response, fertilizer_keywords)
    
    def extract_sun_requirements(self, response):
        """Extract sun/light requirements"""
        sun_keywords = ['sun', 'light', 'shade', 'partial', 'full sun', 'bright']
        return self.extract_text_containing(response, sun_keywords)
    
    def extract_planting_depth(self, response):
        """Extract planting depth information"""
        depth_keywords = ['depth', 'deep', 'plant', 'sow', 'seed', 'inch', 'inches', 'cm']
        return self.extract_text_containing(response, depth_keywords)
    
    def extract_spacing(self, response):
        """Extract plant spacing information"""
        spacing_keywords = ['space', 'spacing', 'apart', 'distance', 'inches', 'feet', 'cm']
        return self.extract_text_containing(response, spacing_keywords)
    
    def extract_days_to_maturity(self, response):
        """Extract days to maturity information"""
        maturity_keywords = ['days', 'maturity', 'harvest', 'ready', 'weeks']
        return self.extract_text_containing(response, maturity_keywords)
    
    def extract_planting_season(self, response):
        """Extract planting season information"""
        season_keywords = ['spring', 'summer', 'fall', 'winter', 'season', 'month', 'plant']
        return self.extract_text_containing(response, season_keywords)
    
    def extract_harvest_time(self, response):
        """Extract harvest timing information"""
        harvest_keywords = ['harvest', 'pick', 'ready', 'ripe', 'mature']
        return self.extract_text_containing(response, harvest_keywords)
    
    def extract_soil_type(self, response):
        """Extract soil type preferences"""
        soil_keywords = ['soil', 'clay', 'sandy', 'loam', 'drainage', 'well-drained']
        return self.extract_text_containing(response, soil_keywords)
    
    def extract_temperature_range(self, response):
        """Extract temperature requirements"""
        temp_keywords = ['temperature', 'degrees', 'hot', 'cold', 'frost', 'hardy', 'zone']
        return self.extract_text_containing(response, temp_keywords)
    
    def extract_text_containing(self, response, keywords):
        """Extract text containing any of the specified keywords"""
        results = []
        
        # Get all text from the page
        all_text = response.css('*::text').getall()
        
        for text in all_text:
            text = text.strip()
            if len(text) > 10:  # Only consider substantial text
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        # Clean up the text
                        cleaned_text = ' '.join(text.split())
                        if cleaned_text not in results and len(cleaned_text) < 500:
                            results.append(cleaned_text)
                        break
        
        return results[:5]  # Limit to top 5 relevant pieces of text

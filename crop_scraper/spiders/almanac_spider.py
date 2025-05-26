import scrapy
from scrapy import Request
from crop_scraper.items import CropItem
import re


class AlmanacSpider(scrapy.Spider):
    name = 'almanac'
    allowed_domains = ['almanac.com']
    start_urls = [
        'https://www.almanac.com/plants',
        'https://www.almanac.com/plants/vegetables',
        'https://www.almanac.com/plants/fruits',
        'https://www.almanac.com/plants/herbs'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }
    
    def parse(self, response):
        """Parse the main plants page to find individual crop pages"""
        
        # Extract links to individual plant pages
        plant_links = response.css('a[href*="/plant/"]::attr(href)').getall()
        
        for link in plant_links:
            if link:
                full_url = response.urljoin(link)
                yield Request(
                    url=full_url,
                    callback=self.parse_crop,
                    meta={'source_page': response.url}
                )
        
        # Look for pagination or additional plant category pages
        next_page_links = response.css('a[href*="/plants/"]::attr(href)').getall()
        
        for link in next_page_links:
            if link and link not in self.start_urls:
                full_url = response.urljoin(link)
                yield Request(
                    url=full_url,
                    callback=self.parse,
                    meta={'source_page': response.url}
                )
    
    def parse_crop(self, response):
        """Parse individual crop/plant pages for nutrition and care information"""
        
        item = CropItem()
        
        # Basic information
        item['name'] = self.extract_name(response)
        item['common_name'] = item['name']  # Almanac typically uses common names
        item['scientific_name'] = self.extract_scientific_name(response)
        item['category'] = self.extract_category(response)
        
        # Growing requirements
        item['planting_depth'] = self.extract_planting_depth(response)
        item['spacing'] = self.extract_spacing(response)
        item['days_to_maturity'] = self.extract_days_to_maturity(response)
        
        # Water requirements
        item['water_needs'] = self.extract_water_needs(response)
        item['irrigation_frequency'] = self.extract_irrigation_frequency(response)
        
        # Soil requirements
        item['soil_ph'] = self.extract_soil_ph(response)
        item['soil_type'] = self.extract_soil_type(response)
        
        # Nutrient requirements
        fertilizer_info = self.extract_fertilizer_info(response)
        item['fertilizer_recommendations'] = fertilizer_info.get('recommendations', [])
        item['organic_fertilizer_options'] = fertilizer_info.get('organic_options', [])
        item['fertilizer_npk'] = fertilizer_info.get('npk', '')
        
        # Growing conditions
        item['sun_requirements'] = self.extract_sun_requirements(response)
        item['temperature_range'] = self.extract_temperature_range(response)
        item['hardiness_zone'] = self.extract_hardiness_zone(response)
        
        # Timing
        item['planting_season'] = self.extract_planting_season(response)
        item['harvest_time'] = self.extract_harvest_time(response)
        
        # Metadata
        item['source_url'] = response.url
        item['data_source'] = 'almanac.com'
        
        yield item
    
    def extract_name(self, response):
        """Extract crop name from the page"""
        # Try multiple selectors for name
        selectors = [
            'h1::text',
            '.plant-name::text',
            '.page-title::text',
            'title::text'
        ]
        
        for selector in selectors:
            name = response.css(selector).get()
            if name:
                # Clean up the name
                name = re.sub(r'\s*\|\s*.*', '', name)  # Remove site name after |
                return name.strip()
        
        return None
    
    def extract_scientific_name(self, response):
        """Extract scientific name if available"""
        # Look for italic text or specific classes that might contain scientific names
        scientific_selectors = [
            '.scientific-name::text',
            'em::text',
            'i::text',
            '*[class*="scientific"]::text',
            '*[class*="latin"]::text'
        ]
        
        for selector in scientific_selectors:
            names = response.css(selector).getall()
            for name in names:
                # Scientific names typically have two words
                if re.match(r'^[A-Z][a-z]+ [a-z]+', name.strip()):
                    return name.strip()
        
        return None
    
    def extract_category(self, response):
        """Extract crop category (vegetable, fruit, herb, etc.)"""
        # Look for breadcrumbs or category information
        category_selectors = [
            '.breadcrumb a::text',
            '.category::text',
            '.plant-type::text'
        ]
        
        for selector in category_selectors:
            categories = response.css(selector).getall()
            for cat in categories:
                cat = cat.strip().lower()
                if cat in ['vegetable', 'fruit', 'herb', 'flower', 'tree', 'shrub']:
                    return cat.title()
        
        # Infer from URL
        if '/vegetables/' in response.url:
            return 'Vegetable'
        elif '/fruits/' in response.url:
            return 'Fruit'
        elif '/herbs/' in response.url:
            return 'Herb'
        
        return None
    
    def extract_planting_depth(self, response):
        """Extract planting depth information"""
        text = ' '.join(response.css('*::text').getall())
        
        depth_patterns = [
            r'plant(?:ing)?\s+(?:depth|deep)\s*:?\s*([^.]+)',
            r'(?:sow|plant)\s+(\d+[^.]*(?:inch|in|cm|centimeter|deep))',
            r'depth\s*:?\s*([^.]+)'
        ]
        
        for pattern in depth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_spacing(self, response):
        """Extract plant spacing information"""
        text = ' '.join(response.css('*::text').getall())
        
        spacing_patterns = [
            r'spac(?:ing|e)\s*:?\s*([^.]+)',
            r'plant\s+(\d+[^.]*(?:inch|in|cm|feet|ft|apart))',
            r'distance\s*:?\s*([^.]+)'
        ]
        
        for pattern in spacing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_days_to_maturity(self, response):
        """Extract days to maturity"""
        text = ' '.join(response.css('*::text').getall())
        
        maturity_patterns = [
            r'(?:days?\s+to\s+)?matur(?:ity|e)\s*:?\s*(\d+[^.]*days?)',
            r'harvest\s+in\s+(\d+[^.]*days?)',
            r'ready\s+in\s+(\d+[^.]*days?)'
        ]
        
        for pattern in maturity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_water_needs(self, response):
        """Extract water requirements"""
        text = ' '.join(response.css('*::text').getall())
        
        water_patterns = [
            r'water(?:ing)?\s*:?\s*([^.]+)',
            r'moisture\s*:?\s*([^.]+)',
            r'irrigation\s*:?\s*([^.]+)'
        ]
        
        for pattern in water_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                water_info = match.group(1).strip()
                # Filter out very long matches that might be paragraphs
                if len(water_info) < 200:
                    return water_info
        
        return None
    
    def extract_irrigation_frequency(self, response):
        """Extract irrigation frequency"""
        text = ' '.join(response.css('*::text').getall())
        
        freq_patterns = [
            r'water\s+([^.]*(?:daily|weekly|twice|once|every))',
            r'irrigat(?:e|ion)\s+([^.]*(?:daily|weekly|twice|once|every))'
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_soil_ph(self, response):
        """Extract soil pH requirements"""
        text = ' '.join(response.css('*::text').getall())
        
        ph_patterns = [
            r'ph\s*:?\s*([^.]+)',
            r'soil\s+ph\s*:?\s*([^.]+)',
            r'acidity\s*:?\s*([^.]+)'
        ]
        
        for pattern in ph_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ph_info = match.group(1).strip()
                if len(ph_info) < 100:  # Reasonable length
                    return ph_info
        
        return None
    
    def extract_soil_type(self, response):
        """Extract soil type requirements"""
        text = ' '.join(response.css('*::text').getall())
        
        soil_patterns = [
            r'soil\s+type\s*:?\s*([^.]+)',
            r'soil\s*:?\s*([^.]*(?:clay|sand|loam|well.drain))',
            r'growing\s+medium\s*:?\s*([^.]+)'
        ]
        
        for pattern in soil_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                soil_info = match.group(1).strip()
                if len(soil_info) < 200:
                    return soil_info
        
        return None
    
    def extract_fertilizer_info(self, response):
        """Extract fertilizer and nutrient information"""
        text = ' '.join(response.css('*::text').getall())
        result = {
            'recommendations': [],
            'organic_options': [],
            'npk': ''
        }
        
        # Look for fertilizer recommendations
        fertilizer_patterns = [
            r'fertili[sz]er?\s*:?\s*([^.]+)',
            r'feed(?:ing)?\s*:?\s*([^.]+)',
            r'nutrient(?:s)?\s*:?\s*([^.]+)',
            r'compost\s*:?\s*([^.]+)'
        ]
        
        for pattern in fertilizer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) < 300:  # Reasonable length
                    result['recommendations'].append(match.strip())
        
        # Look for NPK ratios
        npk_patterns = [
            r'(\d+[-:]\d+[-:]\d+)',
            r'n[-:]?p[-:]?k\s*:?\s*(\d+[-:]\d+[-:]\d+)',
            r'nitrogen\s*:?\s*(\d+).*phosph(?:orus|ate)\s*:?\s*(\d+).*potassium\s*:?\s*(\d+)'
        ]
        
        for pattern in npk_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    result['npk'] = match.group(1)
                elif len(match.groups()) == 3:
                    result['npk'] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                break
        
        # Look for organic fertilizer options
        organic_patterns = [
            r'organic\s+fertilizer\s*:?\s*([^.]+)',
            r'compost\s*:?\s*([^.]+)',
            r'manure\s*:?\s*([^.]+)',
            r'organic\s+matter\s*:?\s*([^.]+)'
        ]
        
        for pattern in organic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) < 200:
                    result['organic_options'].append(match.strip())
        
        return result
    
    def extract_sun_requirements(self, response):
        """Extract sun/light requirements"""
        text = ' '.join(response.css('*::text').getall())
        
        sun_patterns = [
            r'sun(?:light)?\s*:?\s*([^.]+)',
            r'light\s*:?\s*([^.]+)',
            r'(?:full|partial|shade)\s+sun',
            r'(?:full|partial)\s+shade'
        ]
        
        for pattern in sun_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sun_info = match.group(1).strip() if hasattr(match, 'group') else match.group(0)
                if len(sun_info) < 100:
                    return sun_info
        
        return None
    
    def extract_temperature_range(self, response):
        """Extract temperature requirements"""
        text = ' '.join(response.css('*::text').getall())
        
        temp_patterns = [
            r'temperature\s*:?\s*([^.]+)',
            r'(\d+[-–]\d+\s*°?[CF])',
            r'warm\s+season|cool\s+season|cold\s+hardy'
        ]
        
        for pattern in temp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                temp_info = match.group(1) if hasattr(match, 'groups') and match.groups() else match.group(0)
                if len(temp_info.strip()) < 100:
                    return temp_info.strip()
        
        return None
    
    def extract_hardiness_zone(self, response):
        """Extract USDA hardiness zone"""
        text = ' '.join(response.css('*::text').getall())
        
        zone_patterns = [
            r'(?:hardiness\s+)?zone(?:s)?\s*:?\s*(\d+[ab]?[-–]\d+[ab]?)',
            r'zone\s+(\d+[ab]?)',
            r'usda\s+(?:zone\s+)?(\d+[ab]?[-–]\d+[ab]?)'
        ]
        
        for pattern in zone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_planting_season(self, response):
        """Extract planting season/timing"""
        text = ' '.join(response.css('*::text').getall())
        
        planting_patterns = [
            r'plant(?:ing)?\s+(?:time|season)\s*:?\s*([^.]+)',
            r'sow\s*:?\s*([^.]+)',
            r'start\s+(?:seeds?\s+)?(?:in|during)\s+([^.]+)'
        ]
        
        for pattern in planting_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                timing = match.group(1).strip()
                if len(timing) < 200:
                    return timing
        
        return None
    
    def extract_harvest_time(self, response):
        """Extract harvest timing"""
        text = ' '.join(response.css('*::text').getall())
        
        harvest_patterns = [
            r'harvest\s*:?\s*([^.]+)',
            r'ready\s+(?:to\s+harvest|for\s+harvest)\s*:?\s*([^.]+)',
            r'pick\s*:?\s*([^.]+)'
        ]
        
        for pattern in harvest_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                harvest_info = match.group(1).strip()
                if len(harvest_info) < 200:
                    return harvest_info
        
        return None

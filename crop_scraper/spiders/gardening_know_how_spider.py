import scrapy
from scrapy import Request
from crop_scraper.items import CropItem
import re


class GardeningKnowHowSpider(scrapy.Spider):
    name = 'gardening_know_how'
    allowed_domains = ['gardeningknowhow.com']
    start_urls = [
        'https://www.gardeningknowhow.com/edible/vegetables',
        'https://www.gardeningknowhow.com/edible/herbs',
        'https://www.gardeningknowhow.com/edible/fruits'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }
    
    def parse(self, response):
        """Parse category pages to find individual crop articles"""
        
        # Look for article links
        article_links = response.css('a[href*="/edible/"]::attr(href)').getall()
        
        for link in article_links:
            if link and self.is_crop_article(link):
                full_url = response.urljoin(link)
                yield Request(
                    url=full_url,
                    callback=self.parse_crop_article,
                    meta={'source_page': response.url}
                )
        
        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )
    
    def is_crop_article(self, url):
        """Check if URL is for a crop-specific article"""
        crop_indicators = [
            'growing', 'plant', 'care', 'fertiliz', 'water', 'soil',
            'tomato', 'lettuce', 'pepper', 'bean', 'carrot', 'onion'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in crop_indicators)
    
    def parse_crop_article(self, response):
        """Parse individual crop articles"""
        
        item = CropItem()
        
        # Extract crop name from title
        title = response.css('h1::text').get()
        if title:
            item['name'] = self.clean_crop_name(title)
            item['common_name'] = item['name']
        
        # Extract content
        content_text = ' '.join(response.css('.entry-content *::text').getall())
        
        # Extract various growing information
        item['water_needs'] = self.extract_water_info(content_text)
        item['soil_ph'] = self.extract_soil_ph(content_text)
        item['fertilizer_recommendations'] = self.extract_fertilizer_info(content_text)
        item['sun_requirements'] = self.extract_sun_requirements(content_text)
        item['planting_depth'] = self.extract_planting_depth(content_text)
        item['spacing'] = self.extract_spacing(content_text)
        item['days_to_maturity'] = self.extract_maturity(content_text)
        
        # Metadata
        item['source_url'] = response.url
        item['data_source'] = 'Gardening Know How'
        
        # Only yield if we have a valid crop name
        if item.get('name'):
            yield item
    
    def clean_crop_name(self, title):
        """Clean and extract crop name from article title"""
        # Remove common prefixes/suffixes
        title = re.sub(r'(how to|growing|care|tips|guide|information)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'(plant|plants)', '', title, flags=re.IGNORECASE)
        
        # Extract the main crop name
        words = title.split()
        # Look for common crop names
        crops = [
            'tomato', 'lettuce', 'carrot', 'bean', 'pea', 'corn', 'pepper',
            'cucumber', 'squash', 'onion', 'garlic', 'potato', 'cabbage',
            'broccoli', 'cauliflower', 'spinach', 'kale', 'radish', 'beet',
            'basil', 'parsley', 'cilantro', 'oregano', 'thyme', 'sage'
        ]
        
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word.lower())
            if word_clean in crops:
                return word_clean.title()
        
        # If no specific crop found, return cleaned title
        return ' '.join(words).strip()
    
    def extract_water_info(self, text):
        """Extract watering information"""
        water_patterns = [
            r'water[ing]*[^.]*\.',
            r'irrigation[^.]*\.',
            r'moisture[^.]*\.'
        ]
        
        for pattern in water_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first reasonable match
                for match in matches:
                    if 20 < len(match) < 200:
                        return match.strip()
        
        return None
    
    def extract_soil_ph(self, text):
        """Extract soil pH information"""
        ph_patterns = [
            r'ph[^.]*\d+[^.]*\.',
            r'soil[^.]*ph[^.]*\.',
            r'acid[ic]*[^.]*soil[^.]*\.',
            r'alkaline[^.]*soil[^.]*\.'
        ]
        
        for pattern in ph_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(0)) < 150:
                return match.group(0).strip()
        
        return None
    
    def extract_fertilizer_info(self, text):
        """Extract fertilizer information"""
        fertilizer_patterns = [
            r'fertiliz[er]*[^.]*\.',
            r'feed[ing]*[^.]*\.',
            r'compost[^.]*\.',
            r'nutrient[s]*[^.]*\.',
            r'\d+-\d+-\d+[^.]*\.'
        ]
        
        recommendations = []
        for pattern in fertilizer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if 20 < len(match) < 250:
                    recommendations.append(match.strip())
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def extract_sun_requirements(self, text):
        """Extract sun requirements"""
        sun_patterns = [
            r'full sun[^.]*\.',
            r'partial shade[^.]*\.',
            r'full shade[^.]*\.',
            r'sun[light]*[^.]*hours[^.]*\.',
            r'light[^.]*requirements[^.]*\.'
        ]
        
        for pattern in sun_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(0)) < 150:
                return match.group(0).strip()
        
        return None
    
    def extract_planting_depth(self, text):
        """Extract planting depth"""
        depth_patterns = [
            r'plant[^.]*depth[^.]*\.',
            r'sow[^.]*deep[^.]*\.',
            r'bury[^.]*inch[^.]*\.'
        ]
        
        for pattern in depth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(0)) < 150:
                return match.group(0).strip()
        
        return None
    
    def extract_spacing(self, text):
        """Extract plant spacing"""
        spacing_patterns = [
            r'spac[ing]*[^.]*apart[^.]*\.',
            r'plant[^.]*inches[^.]*apart[^.]*\.',
            r'distance[^.]*between[^.]*\.'
        ]
        
        for pattern in spacing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(0)) < 150:
                return match.group(0).strip()
        
        return None
    
    def extract_maturity(self, text):
        """Extract days to maturity"""
        maturity_patterns = [
            r'matur[ity]*[^.]*\d+[^.]*days[^.]*\.',
            r'harvest[^.]*\d+[^.]*days[^.]*\.',
            r'ready[^.]*\d+[^.]*weeks[^.]*\.'
        ]
        
        for pattern in maturity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.group(0)) < 150:
                return match.group(0).strip()
        
        return None

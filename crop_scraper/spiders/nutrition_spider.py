# filepath: c:\Users\PC\byu classwork\wd330\project\crop_scraper\spiders\nutrition_spider.py
import scrapy
import re
from crop_scraper.items import CropItem
from urllib.parse import urljoin


class NutritionSpider(scrapy.Spider):
    name = 'nutrition'
    allowed_domains = [
        'almanac.com',
        'extension.umn.edu',
        'extension.psu.edu',
        'ag.umass.edu',
        'extension.umd.edu',
        'gardening.cornell.edu',
        'hgic.clemson.edu'
    ]
    
    # Target sites known for detailed nutrition information
    start_urls = [
        # Almanac.com - general growing info
        'https://www.almanac.com/plant/tomatoes',
        'https://www.almanac.com/plant/carrots',
        'https://www.almanac.com/plant/lettuce',
        'https://www.almanac.com/plant/beans',
        'https://www.almanac.com/plant/corn',
        'https://www.almanac.com/plant/potatoes',
        
        # University Extension sites - detailed nutrition schedules
        'https://extension.umn.edu/vegetables/growing-tomatoes',
        'https://extension.psu.edu/vegetable-fertilizer-recommendations',
        'https://ag.umass.edu/greenhouse-floriculture/fact-sheets/nutrition-management-for-greenhouse-crops',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEEDS': {
            'nutrition_data.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
    }
    
    def parse(self, response):
        """Parse crop pages for nutrition data"""
        self.logger.info(f"Parsing nutrition page: {response.url}")
        
        item = CropItem()
        
        # Extract basic crop info
        item['name'] = self.extract_name(response)
        item['source_url'] = response.url
        item['data_source'] = response.url.split('/')[2]
        
        # Extract stage-specific nutrition data
        try:
            # Enhanced nutrition extraction with growth stages
            nutrition_data = self.extract_stage_nutrition(response)
            
            # Basic fertilizer info
            item['fertilizer_recommendations'] = self.extract_fertilizer_recommendations(response)
            item['nitrogen_requirement'] = nutrition_data.get('nitrogen', '')
            item['phosphorus_requirement'] = nutrition_data.get('phosphorus', '')
            item['potassium_requirement'] = nutrition_data.get('potassium', '')
            item['secondary_nutrients'] = nutrition_data.get('secondary', '')
            item['micronutrients'] = nutrition_data.get('micronutrients', '')
            
            # Water and soil requirements
            item['water_needs'] = self.extract_water_requirements(response)
            item['soil_ph'] = self.extract_soil_requirements(response)
            
            # Growing info
            item['planting_depth'] = self.extract_planting_info(response)
            item['spacing'] = self.extract_spacing_info(response)
            item['days_to_maturity'] = self.extract_maturity_info(response)
            item['sun_requirements'] = self.extract_sun_requirements(response)
            
        except Exception as e:
            self.logger.error(f"Error extracting nutrition data from {response.url}: {e}")
        
        self.logger.info(f"Successfully extracted nutrition data for: {item.get('name', 'Unknown')}")
        yield item
        
        # Also create nutrient recipe items for stage-specific data
        for recipe in self.extract_nutrient_recipes(response, item.get('name', 'Unknown')):
            yield recipe
    
    def extract_stage_nutrition(self, response):
        """Extract stage-specific nutrition requirements"""
        nutrition_data = {
            'nitrogen': [],
            'phosphorus': [],
            'potassium': [],
            'secondary': [],
            'micronutrients': []
        }
        
        # Growth stage keywords to look for
        stage_keywords = {
            'seedling': ['seedling', 'germination', 'emergence', 'transplant'],
            'vegetative': ['vegetative', 'growth', 'leaf', 'foliage', 'vegetative growth'],
            'flowering': ['flowering', 'bloom', 'flower', 'bud', 'reproductive'],
            'fruiting': ['fruit', 'harvest', 'maturity', 'production', 'yield'],
            'general': ['fertilizer', 'nutrient', 'feed', 'nutrition']
        }
        
        # NPK ratio patterns
        npk_patterns = [
            r'(\d+)-(\d+)-(\d+)',  # 10-10-10 format
            r'N[:\s]*(\d+).*P[:\s]*(\d+).*K[:\s]*(\d+)',  # N:10 P:10 K:10 format
            r'nitrogen[:\s]*(\d+).*phosphorus[:\s]*(\d+).*potassium[:\s]*(\d+)',
        ]
        
        # Extract all text content
        all_text = ' '.join(response.css('*::text').getall())
        
        # Look for NPK ratios
        for pattern in npk_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                try:
                    n, p, k = match.groups()
                    nutrition_data['nitrogen'].append(f"N: {n}")
                    nutrition_data['phosphorus'].append(f"P: {p}")
                    nutrition_data['potassium'].append(f"K: {k}")
                except:
                    continue
        
        # Look for stage-specific nutrition info
        for stage, keywords in stage_keywords.items():
            stage_content = self.extract_text_containing(response, keywords)
            
            # Extract nitrogen info for this stage
            nitrogen_info = self.extract_nutrient_info(stage_content, ['nitrogen', 'N', 'nitrate'])
            if nitrogen_info:
                nutrition_data['nitrogen'].extend([f"{stage}: {info}" for info in nitrogen_info])
            
            # Extract phosphorus info
            phosphorus_info = self.extract_nutrient_info(stage_content, ['phosphorus', 'P', 'phosphate'])
            if phosphorus_info:
                nutrition_data['phosphorus'].extend([f"{stage}: {info}" for info in phosphorus_info])
            
            # Extract potassium info
            potassium_info = self.extract_nutrient_info(stage_content, ['potassium', 'K', 'potash'])
            if potassium_info:
                nutrition_data['potassium'].extend([f"{stage}: {info}" for info in potassium_info])
        
        # Look for secondary nutrients (Ca, Mg, S)
        secondary_nutrients = self.extract_nutrient_info(all_text, 
            ['calcium', 'magnesium', 'sulfur', 'Ca', 'Mg', 'S'])
        if secondary_nutrients:
            nutrition_data['secondary'].extend(secondary_nutrients)
        
        # Look for micronutrients
        micronutrients = self.extract_nutrient_info(all_text,
            ['iron', 'manganese', 'zinc', 'copper', 'boron', 'molybdenum', 'Fe', 'Mn', 'Zn', 'Cu', 'B', 'Mo'])
        if micronutrients:
            nutrition_data['micronutrients'].extend(micronutrients)
        
        # Convert lists to pipe-separated strings
        for key in nutrition_data:
            nutrition_data[key] = ' | '.join(nutrition_data[key]) if nutrition_data[key] else ''
        
        return nutrition_data
    
    def extract_nutrient_info(self, text_content, nutrient_keywords):
        """Extract specific nutrient information from text"""
        nutrient_info = []
        
        if isinstance(text_content, list):
            text_content = ' '.join(text_content)
        
        for keyword in nutrient_keywords:
            # Look for sentences containing the nutrient keyword
            sentences = re.split(r'[.!?]', text_content)
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 20 and len(clean_sentence) < 300:
                        # Look for numbers and measurements
                        if any(char.isdigit() for char in clean_sentence):
                            nutrient_info.append(clean_sentence)
        
        return nutrient_info
    
    def extract_nutrient_recipes(self, response, crop_name):
        """Extract detailed nutrient recipes for different growth stages"""
        recipes = []
        
        # Look for fertilizer schedules or feeding charts
        schedule_keywords = [
            'fertilizer schedule', 'feeding schedule', 'nutrient schedule',
            'fertilizer program', 'feeding program', 'weekly feeding',
            'application rate', 'fertilizer rate', 'ppm', 'ec'
        ]
        
        schedule_content = self.extract_text_containing(response, schedule_keywords)
        
        if schedule_content:
            # Try to parse into structured recipes
            for content in schedule_content:
                recipe = self.parse_fertilizer_schedule(content, crop_name, response.url)
                if recipe:
                    recipes.append(recipe)
        
        return recipes
    
    def parse_fertilizer_schedule(self, content, crop_name, source_url):
        """Parse fertilizer schedule text into structured data"""
        from crop_scraper.items import CropItem
        
        # Look for timing indicators
        timing_patterns = [
            r'week (\d+)', r'day (\d+)', r'(\d+) weeks?',
            r'seedling', r'vegetative', r'flowering', r'fruiting'
        ]
        
        # Look for NPK values
        npk_match = re.search(r'(\d+)-(\d+)-(\d+)', content)
        
        # Look for application rates
        rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:ppm|mg/l|g/l)',
            r'(\d+(?:\.\d+)?)\s*(?:tablespoons?|tbsp|tsp|cups?)',
            r'(\d+(?:\.\d+)?)\s*(?:grams?|ounces?|lbs?)'
        ]
        
        timing = None
        for pattern in timing_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                timing = match.group()
                break
        
        rate = None
        for pattern in rate_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                rate = match.group()
                break
        
        if timing or npk_match or rate:
            recipe = CropItem()
            recipe['name'] = crop_name
            recipe['fertilizer_type'] = 'scheduled_feeding'
            recipe['application_timing'] = timing or 'general'
            recipe['application_rate'] = rate or 'as directed'
            
            if npk_match:
                n, p, k = npk_match.groups()
                recipe['nitrogen_requirement'] = f"N: {n}"
                recipe['phosphorus_requirement'] = f"P: {p}"
                recipe['potassium_requirement'] = f"K: {k}"
                recipe['fertilizer_npk'] = f"{n}-{p}-{k}"
            
            recipe['fertilizer_recommendations'] = content[:500]  # Limit length
            recipe['source_url'] = source_url
            recipe['data_source'] = source_url.split('/')[2]
            
            return recipe
        
        return None
    
    def extract_fertilizer_recommendations(self, response):
        """Extract general fertilizer recommendations"""
        keywords = [
            'fertilizer', 'fertilize', 'feed', 'feeding', 'nutrient', 'nutrition',
            'compost', 'manure', 'organic', 'npk', 'nitrogen', 'phosphorus', 'potassium'
        ]
        
        recommendations = self.extract_text_containing(response, keywords)
        return ' | '.join(recommendations) if recommendations else ''
    
    def extract_water_requirements(self, response):
        """Extract water and irrigation requirements"""
        keywords = [
            'water', 'watering', 'irrigation', 'moisture', 'humid', 'wet', 'dry',
            'inches per week', 'gallons', 'liters'
        ]
        
        water_info = self.extract_text_containing(response, keywords)
        return ' | '.join(water_info) if water_info else ''
    
    def extract_soil_requirements(self, response):
        """Extract soil pH and soil requirements"""
        keywords = ['ph', 'pH', 'acid', 'alkaline', 'soil', 'loam', 'clay', 'sand']
        
        soil_info = self.extract_text_containing(response, keywords)
        return ' | '.join(soil_info) if soil_info else ''
    
    def extract_planting_info(self, response):
        """Extract planting depth and method"""
        keywords = ['depth', 'plant', 'sow', 'seed', 'inch', 'cm', 'deep']
        
        planting_info = self.extract_text_containing(response, keywords)
        return ' | '.join(planting_info) if planting_info else ''
    
    def extract_spacing_info(self, response):
        """Extract spacing requirements"""
        keywords = ['space', 'spacing', 'apart', 'distance', 'inch', 'feet', 'cm']
        
        spacing_info = self.extract_text_containing(response, keywords)
        return ' | '.join(spacing_info) if spacing_info else ''
    
    def extract_maturity_info(self, response):
        """Extract days to maturity"""
        keywords = ['days', 'maturity', 'harvest', 'ready', 'weeks']
        
        maturity_info = self.extract_text_containing(response, keywords)
        return ' | '.join(maturity_info) if maturity_info else ''
    
    def extract_sun_requirements(self, response):
        """Extract sun and light requirements"""
        keywords = ['sun', 'light', 'shade', 'full sun', 'partial', 'hours']
        
        sun_info = self.extract_text_containing(response, keywords)
        return ' | '.join(sun_info) if sun_info else ''
    
    def extract_text_containing(self, response, keywords):
        """Extract text snippets containing specific keywords"""
        results = []
        
        # Enhanced content selectors for better nutrition data extraction
        content_selectors = [
            'div.content *::text',
            'article *::text',
            '.entry-content *::text',
            '.post-content *::text',
            '.main-content *::text',
            'main *::text',
            '.fertilizer *::text',
            '.nutrition *::text',
            '.feeding *::text',
            'table *::text',  # Tables often contain nutrition schedules
            '.schedule *::text',
            '.chart *::text'
        ]
        
        # Try to get text from structured content first
        texts = []
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
            # Look for substantial text chunks
            if len(text) > 15 and len(text) < 1000:  
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        # Clean up the text
                        cleaned_text = ' '.join(text.split())
                        # Filter out navigation and header text
                        if not any(nav_word in cleaned_text.lower() for nav_word in [
                            'navigation', 'menu', 'calendar', 'holiday', 'moon', 'sun times',
                            'almanac', 'store', 'sunrise', 'set times', 'best days', 'copyright',
                            'privacy', 'terms', 'subscribe', 'newsletter'
                        ]):
                            if cleaned_text not in results:
                                results.append(cleaned_text)
                        break
        
        return results[:5]  # Limit to top 5 relevant pieces
    
    def extract_name(self, response):
        """Extract crop name"""
        # Try multiple selectors to find the crop name
        name_selectors = [
            'h1.page-title::text',
            'h1::text',
            '.plant-name::text',
            '.crop-name::text',
            'h1 span::text',
            '.entry-title::text',
            'title::text'
        ]
        
        for selector in name_selectors:
            name = response.css(selector).get()
            if name:
                clean_name = name.strip()
                # Clean up title text
                clean_name = clean_name.replace(' | The Old Farmer\'s Almanac', '')
                clean_name = clean_name.replace(' - Extension', '')
                clean_name = clean_name.replace(' - University', '')
                
                # Filter out common non-crop words
                if clean_name and not any(word in clean_name.lower() for word in [
                    'almanac', 'calendar', 'extension', 'university', 'home'
                ]):
                    return clean_name
        
        # Fallback to URL parsing
        url_parts = response.url.split('/')
        if 'plant' in url_parts:
            idx = url_parts.index('plant')
            if idx + 1 < len(url_parts):
                crop_name = url_parts[idx + 1].replace('-', ' ').title()
                return crop_name
        
        # Final fallback
        return response.url.split('/')[-1].replace('-', ' ').title()

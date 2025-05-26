import scrapy
from scrapy import Request
from crop_scraper.items import CropItem, NutrientRecipeItem
import re
import json


class ExtensionSpider(scrapy.Spider):
    name = 'extension'
    allowed_domains = [
        'extension.psu.edu',
        'extension.purdue.edu', 
        'extension.umn.edu',
        'extension.illinois.edu',
        'extension.usu.edu'
    ]
    
    # Start URLs for university extension services
    start_urls = [
        'https://extension.psu.edu/plants/vegetable-gardening',
        'https://extension.purdue.edu/extmedia/HO/',
        'https://extension.umn.edu/vegetables',
        'https://extension.illinois.edu/vegetables',
        'https://extension.usu.edu/vegetableguide/'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        """Parse extension main pages to find crop-specific guides"""
        
        # Look for links to individual crop guides
        crop_links = response.css('a[href*="vegetable"], a[href*="crop"], a[href*="grow"]::attr(href)').getall()
        
        for link in crop_links:
            if link:
                full_url = response.urljoin(link)
                if self.is_relevant_crop_page(full_url):
                    yield Request(
                        url=full_url,
                        callback=self.parse_crop_guide,
                        meta={'source_page': response.url}
                    )
        
        # Look for PDF documents that might contain nutrient information
        pdf_links = response.css('a[href$=".pdf"]::attr(href)').getall()
        
        for pdf_link in pdf_links:
            if pdf_link and self.is_relevant_pdf(pdf_link):
                full_url = response.urljoin(pdf_link)
                yield Request(
                    url=full_url,
                    callback=self.parse_pdf_guide,
                    meta={'source_page': response.url}
                )
    
    def is_relevant_crop_page(self, url):
        """Check if URL is likely to contain crop information"""
        relevant_keywords = [
            'tomato', 'lettuce', 'carrot', 'bean', 'pea', 'corn', 'pepper',
            'cucumber', 'squash', 'onion', 'garlic', 'potato', 'cabbage',
            'broccoli', 'cauliflower', 'spinach', 'kale', 'radish', 'beet',
            'turnip', 'parsnip', 'vegetable', 'crop', 'fertilizer', 'nutrient'
        ]
        
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in relevant_keywords)
    
    def is_relevant_pdf(self, url):
        """Check if PDF is likely to contain crop nutrition information"""
        relevant_keywords = [
            'fertilizer', 'nutrient', 'nutrition', 'npk', 'crop', 'vegetable',
            'growing', 'guide', 'recommendation'
        ]
        
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in relevant_keywords)
    
    def parse_crop_guide(self, response):
        """Parse individual crop guide pages"""
        
        # Determine if this contains detailed nutrient recipes
        text_content = ' '.join(response.css('*::text').getall())
        
        if self.contains_detailed_nutrients(text_content):
            yield from self.extract_nutrient_recipes(response, text_content)
        else:
            # Extract basic crop information
            item = self.extract_basic_crop_info(response, text_content)
            if item:
                yield item
    
    def parse_pdf_guide(self, response):
        """Parse PDF documents (basic handling)"""
        # Note: This is a placeholder. For actual PDF parsing, you'd need
        # additional tools like PyPDF2 or pdfplumber
        
        # For now, we'll log that we found a PDF and store the URL
        self.logger.info(f"Found PDF guide: {response.url}")
        
        # You could implement PDF download and parsing here
        # or use a service that converts PDFs to text
        
        pass
    
    def contains_detailed_nutrients(self, text):
        """Check if text contains detailed nutrient information"""
        nutrient_indicators = [
            r'\d+\s*ppm', r'parts\s+per\s+million', r'mg/L', r'mg/l',
            r'nitrogen.*\d+', r'phosphorus.*\d+', r'potassium.*\d+',
            r'N[-:]P[-:]K', r'\d+[-:]\d+[-:]\d+',
            r'EC.*\d+', r'electrical\s+conductivity'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in nutrient_indicators)
    
    def extract_nutrient_recipes(self, response, text):
        """Extract detailed nutrient recipes from extension guides"""
        
        crop_name = self.extract_crop_name_from_url_or_title(response)
        
        # Look for nutrient tables or detailed recommendations
        nutrient_sections = self.find_nutrient_sections(text)
        
        for section in nutrient_sections:
            recipe_item = NutrientRecipeItem()
            
            recipe_item['crop_name'] = crop_name
            recipe_item['stage_of_growth'] = self.extract_growth_stage(section)
            
            # Extract PPM values for major nutrients
            recipe_item['nitrogen_ppm'] = self.extract_ppm_value(section, 'nitrogen|N')
            recipe_item['phosphorus_ppm'] = self.extract_ppm_value(section, 'phosphorus|P')
            recipe_item['potassium_ppm'] = self.extract_ppm_value(section, 'potassium|K')
            
            # Extract secondary nutrients
            recipe_item['calcium_ppm'] = self.extract_ppm_value(section, 'calcium|Ca')
            recipe_item['magnesium_ppm'] = self.extract_ppm_value(section, 'magnesium|Mg')
            recipe_item['sulfur_ppm'] = self.extract_ppm_value(section, 'sulfur|S')
            
            # Extract micronutrients
            recipe_item['iron_ppm'] = self.extract_ppm_value(section, 'iron|Fe')
            recipe_item['manganese_ppm'] = self.extract_ppm_value(section, 'manganese|Mn')
            recipe_item['zinc_ppm'] = self.extract_ppm_value(section, 'zinc|Zn')
            recipe_item['copper_ppm'] = self.extract_ppm_value(section, 'copper|Cu')
            recipe_item['boron_ppm'] = self.extract_ppm_value(section, 'boron|B')
            recipe_item['molybdenum_ppm'] = self.extract_ppm_value(section, 'molybdenum|Mo')
            
            # Extract solution properties
            recipe_item['ec_range'] = self.extract_ec_range(section)
            recipe_item['ph_range'] = self.extract_ph_range(section)
            
            # Extract application details
            recipe_item['application_method'] = self.extract_application_method(section)
            recipe_item['frequency'] = self.extract_application_frequency(section)
            
            # Metadata
            recipe_item['source_url'] = response.url
            recipe_item['data_source'] = self.get_data_source_name(response.url)
            recipe_item['reference_document'] = response.css('title::text').get()
            
            # Only yield if we have meaningful data
            if any([recipe_item.get('nitrogen_ppm'), recipe_item.get('phosphorus_ppm'), 
                   recipe_item.get('potassium_ppm')]):
                yield recipe_item
    
    def extract_basic_crop_info(self, response, text):
        """Extract basic crop information from extension pages"""
        
        crop_name = self.extract_crop_name_from_url_or_title(response)
        if not crop_name:
            return None
        
        item = CropItem()
        item['name'] = crop_name
        item['common_name'] = crop_name
        
        # Extract fertilizer recommendations
        fertilizer_info = self.extract_extension_fertilizer_info(text)
        item['fertilizer_recommendations'] = fertilizer_info.get('recommendations', [])
        item['fertilizer_npk'] = fertilizer_info.get('npk', '')
        
        # Extract other growing information
        item['soil_ph'] = self.extract_soil_ph_extension(text)
        item['water_needs'] = self.extract_water_needs_extension(text)
        item['planting_depth'] = self.extract_planting_depth_extension(text)
        item['spacing'] = self.extract_spacing_extension(text)
        item['days_to_maturity'] = self.extract_maturity_extension(text)
        
        # Metadata
        item['source_url'] = response.url
        item['data_source'] = self.get_data_source_name(response.url)
        
        return item
    
    def extract_crop_name_from_url_or_title(self, response):
        """Extract crop name from URL or page title"""
        
        # Try to get from title first
        title = response.css('title::text').get()
        if title:
            # Common crop names
            crops = [
                'tomato', 'lettuce', 'carrot', 'bean', 'pea', 'corn', 'pepper',
                'cucumber', 'squash', 'onion', 'garlic', 'potato', 'cabbage',
                'broccoli', 'cauliflower', 'spinach', 'kale', 'radish', 'beet'
            ]
            
            title_lower = title.lower()
            for crop in crops:
                if crop in title_lower:
                    return crop.title()
        
        # Try to extract from URL
        url_parts = response.url.lower().split('/')
        for part in url_parts:
            for crop in crops:
                if crop in part:
                    return crop.title()
        
        return None
    
    def find_nutrient_sections(self, text):
        """Find sections of text that contain nutrient information"""
        
        # Split text into sections based on headers or paragraphs
        sections = []
        
        # Look for nutrient tables or sections
        nutrient_keywords = [
            'nutrient', 'fertilizer', 'ppm', 'mg/L', 'N-P-K', 'nitrogen',
            'phosphorus', 'potassium', 'solution', 'concentration'
        ]
        
        # Simple section splitting - you might want to make this more sophisticated
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if any(keyword.lower() in paragraph.lower() for keyword in nutrient_keywords):
                if len(paragraph) > 50:  # Ignore very short sections
                    sections.append(paragraph)
        
        return sections
    
    def extract_growth_stage(self, text):
        """Extract growth stage from nutrient section"""
        
        stage_patterns = [
            r'(seedling|transplant|vegetative|flowering|fruiting|harvest)',
            r'(germination|establishment|growth|reproductive)',
            r'week\s+(\d+)', r'stage\s+(\d+)'
        ]
        
        for pattern in stage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return 'general'
    
    def extract_ppm_value(self, text, nutrient_pattern):
        """Extract PPM value for a specific nutrient"""
        
        patterns = [
            f'{nutrient_pattern}[^\\d]*([\\d.]+)\\s*ppm',
            f'{nutrient_pattern}[^\\d]*([\\d.]+)\\s*mg/L',
            f'({nutrient_pattern})\\s*([\\d.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Get the numeric part
                    if len(match.groups()) == 2:
                        return float(match.group(2))
                    else:
                        return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_ec_range(self, text):
        """Extract EC (electrical conductivity) range"""
        
        ec_patterns = [
            r'EC[^\\d]*([\\d.]+[-–][\\d.]+)',
            r'electrical\\s+conductivity[^\\d]*([\\d.]+[-–][\\d.]+)',
            r'([\\d.]+[-–][\\d.]+)\\s*(?:mS|dS|µS)'
        ]
        
        for pattern in ec_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_ph_range(self, text):
        """Extract pH range"""
        
        ph_patterns = [
            r'pH[^\\d]*([\\d.]+[-–][\\d.]+)',
            r'([\\d.]+[-–][\\d.]+)\\s*pH'
        ]
        
        for pattern in ph_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_application_method(self, text):
        """Extract application method"""
        
        method_keywords = [
            'foliar', 'soil', 'hydroponic', 'fertigation', 'broadcast',
            'band', 'side-dress', 'top-dress', 'injection'
        ]
        
        for keyword in method_keywords:
            if keyword.lower() in text.lower():
                return keyword.title()
        
        return None
    
    def extract_application_frequency(self, text):
        """Extract application frequency"""
        
        freq_patterns = [
            r'(daily|weekly|monthly|bi-weekly)',
            r'every\\s+(\\d+)\\s+(day|week|month)',
            r'(once|twice)\\s+per\\s+(week|month)'
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def extract_extension_fertilizer_info(self, text):
        """Extract fertilizer information from extension text"""
        
        result = {'recommendations': [], 'npk': ''}
        
        # Look for fertilizer recommendations
        fertilizer_patterns = [
            r'fertilizer[^.]*\\.',
            r'apply[^.]*fertilizer[^.]*\\.',
            r'\\d+[-:]\\d+[-:]\\d+[^.]*\\.'
        ]
        
        for pattern in fertilizer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            result['recommendations'].extend([match.strip() for match in matches])
        
        # Look for NPK ratios
        npk_match = re.search(r'(\\d+[-:]\\d+[-:]\\d+)', text)
        if npk_match:
            result['npk'] = npk_match.group(1)
        
        return result
    
    def extract_soil_ph_extension(self, text):
        """Extract soil pH from extension text"""
        
        ph_patterns = [
            r'soil\\s+pH[^\\d]*([\\d.]+[-–][\\d.]+)',
            r'pH[^\\d]*([\\d.]+[-–][\\d.]+)'
        ]
        
        for pattern in ph_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_water_needs_extension(self, text):
        """Extract water needs from extension text"""
        
        water_patterns = [
            r'water[^.]*inch[^.]*\\.',
            r'irrigation[^.]*\\.',
            r'moisture[^.]*\\.'
        ]
        
        for pattern in water_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_planting_depth_extension(self, text):
        """Extract planting depth from extension text"""
        
        depth_patterns = [
            r'plant[^.]*depth[^.]*\\.',
            r'sow[^.]*deep[^.]*\\.'
        ]
        
        for pattern in depth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_spacing_extension(self, text):
        """Extract plant spacing from extension text"""
        
        spacing_patterns = [
            r'spac[^.]*apart[^.]*\\.',
            r'plant[^.]*inches?[^.]*apart[^.]*\\.'
        ]
        
        for pattern in spacing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_maturity_extension(self, text):
        """Extract days to maturity from extension text"""
        
        maturity_patterns = [
            r'matur[^.]*\\d+[^.]*days?[^.]*\\.',
            r'harvest[^.]*\\d+[^.]*days?[^.]*\\.'
        ]
        
        for pattern in maturity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def get_data_source_name(self, url):
        """Get a friendly name for the data source based on URL"""
        
        if 'psu.edu' in url:
            return 'Penn State Extension'
        elif 'purdue.edu' in url:
            return 'Purdue Extension'
        elif 'umn.edu' in url:
            return 'University of Minnesota Extension'
        elif 'illinois.edu' in url:
            return 'University of Illinois Extension'
        elif 'usu.edu' in url:
            return 'Utah State University Extension'
        else:
            return 'University Extension'

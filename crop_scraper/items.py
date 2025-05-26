# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


def clean_text(text):
    """Clean and normalize text data"""
    if text:
        return text.strip().replace('\n', ' ').replace('\r', ' ')
    return text


def parse_nutrients(nutrient_string):
    """Parse nutrient values from strings like 'N-P-K: 10-10-10'"""
    if not nutrient_string:
        return {}
    
    try:
        # Handle different nutrient format patterns
        if '-' in nutrient_string:
            parts = nutrient_string.split('-')
            if len(parts) >= 3:
                return {
                    'nitrogen': float(parts[0]) if parts[0].replace('.', '').isdigit() else None,
                    'phosphorus': float(parts[1]) if parts[1].replace('.', '').isdigit() else None,
                    'potassium': float(parts[2]) if parts[2].replace('.', '').isdigit() else None
                }
    except (ValueError, IndexError):
        pass
    
    return {}


class CropItem(scrapy.Item):
    """Main item for storing crop information"""
    
    # Basic crop information
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    common_name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    scientific_name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    category = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Growing requirements
    planting_depth = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    spacing = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    days_to_maturity = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Water requirements
    water_needs = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    irrigation_frequency = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    water_amount_per_week = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Soil requirements
    soil_ph = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    soil_type = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Nutrient requirements (the "recipe")
    nitrogen_requirement = scrapy.Field()
    phosphorus_requirement = scrapy.Field()
    potassium_requirement = scrapy.Field()
    
    fertilizer_npk = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text, parse_nutrients),
        output_processor=TakeFirst()
    )
    
    fertilizer_recommendations = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=Join('; ')
    )
    
    organic_fertilizer_options = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=Join('; ')
    )
    
    # Additional nutrients
    secondary_nutrients = scrapy.Field()  # Ca, Mg, S
    micronutrients = scrapy.Field()  # Fe, Mn, Zn, etc.
    
    # Growing conditions
    sun_requirements = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    temperature_range = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    hardiness_zone = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Timing
    planting_season = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    harvest_time = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Metadata
    source_url = scrapy.Field()
    scraped_date = scrapy.Field()
    data_source = scrapy.Field()


class NutrientRecipeItem(scrapy.Item):
    """Specialized item for detailed nutrient recipes"""
    
    crop_name = scrapy.Field()
    stage_of_growth = scrapy.Field()  # seedling, vegetative, flowering, fruiting
    
    # Primary macronutrients (NPK)
    nitrogen_ppm = scrapy.Field()
    phosphorus_ppm = scrapy.Field()
    potassium_ppm = scrapy.Field()
    
    # Secondary macronutrients
    calcium_ppm = scrapy.Field()
    magnesium_ppm = scrapy.Field()
    sulfur_ppm = scrapy.Field()
    
    # Micronutrients
    iron_ppm = scrapy.Field()
    manganese_ppm = scrapy.Field()
    zinc_ppm = scrapy.Field()
    copper_ppm = scrapy.Field()
    boron_ppm = scrapy.Field()
    molybdenum_ppm = scrapy.Field()
    
    # Solution properties
    ec_range = scrapy.Field()  # Electrical conductivity
    ph_range = scrapy.Field()
    
    # Application details
    application_method = scrapy.Field()
    frequency = scrapy.Field()
    
    # Metadata
    source_url = scrapy.Field()
    reference_document = scrapy.Field()
    author = scrapy.Field()
    data_source = scrapy.Field()

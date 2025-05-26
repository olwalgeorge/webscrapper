# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
import json
import sqlite3
from datetime import datetime
from scrapy.exceptions import DropItem
import logging
import os


class ValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Validate required fields
        if not adapter.get('name'):
            raise DropItem(f"Missing crop name in {item}")
        
        # Add timestamp
        adapter['scraped_date'] = datetime.now().isoformat()
        
        return item


class DatabasePipeline:
    def __init__(self):
        self.database_name = 'crops.db'
        self.connection = None
        
    def open_spider(self, spider):
        """Initialize database connection and create tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.database_name)
            self.create_tables()
            logging.info(f"Database connection established: {self.database_name}")
        except Exception as e:
            logging.error(f"Error opening database: {e}")
            raise
    
    def close_spider(self, spider):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.connection.cursor()
          # Create crops table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                common_name TEXT,
                scientific_name TEXT,
                category TEXT,
                planting_depth TEXT,
                spacing TEXT,
                days_to_maturity TEXT,
                water_needs TEXT,
                irrigation_frequency TEXT,
                water_amount_per_week TEXT,
                soil_ph TEXT,
                soil_type TEXT,
                nitrogen_requirement TEXT,
                phosphorus_requirement TEXT,
                potassium_requirement TEXT,
                fertilizer_npk TEXT,
                fertilizer_recommendations TEXT,
                organic_fertilizer_options TEXT,
                secondary_nutrients TEXT,
                micronutrients TEXT,
                sun_requirements TEXT,
                temperature_range TEXT,
                hardiness_zone TEXT,
                companion_plants TEXT,
                pest_resistance TEXT,
                planting_season TEXT,
                harvest_time TEXT,
                source_url TEXT,
                scraped_date TEXT,
                data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, source_url)
            )
        ''')
        
        # Create nutrient_recipes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrient_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL,
                fertilizer_type TEXT,
                npk_ratio TEXT,
                application_rate TEXT,
                application_frequency TEXT,
                application_timing TEXT,
                nitrogen_requirements TEXT,
                phosphorus_requirements TEXT,
                potassium_requirements TEXT,
                calcium_requirements TEXT,
                magnesium_requirements TEXT,
                micronutrients TEXT,
                organic_fertilizers TEXT,
                synthetic_fertilizers TEXT,
                compost_recommendations TEXT,
                mulching_recommendations TEXT,
                watering_frequency TEXT,
                watering_amount TEXT,
                irrigation_method TEXT,
                source_url TEXT,
                scraped_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(crop_name, fertilizer_type, source_url)            )
        ''')        
        
        self.connection.commit()
        logging.info("Database tables created successfully")
    
    def process_item(self, item, spider):
        """Process and store item in database"""
        adapter = ItemAdapter(item)
        
        try:
            # Determine item type and insert accordingly
            if 'fertilizer_type' in adapter or 'npk_ratio' in adapter:
                self.insert_nutrient_recipe(adapter)
            else:
                self.insert_crop(adapter)
                
            return item
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logging.warning(f"Duplicate item skipped: {adapter.get('name', 'Unknown')}")
                return item
            else:
                logging.error(f"Database integrity error: {e}")
                raise DropItem(f"Database error: {e}")
        except Exception as e:
            logging.error(f"Error processing item: {e}")
            raise DropItem(f"Database error: {e}")
    
    def insert_crop(self, adapter):
        """Insert crop data into crops table"""
        cursor = self.connection.cursor()
        
        crop_data = (
            adapter.get('name'),
            adapter.get('common_name'),
            adapter.get('scientific_name'),
            adapter.get('category'),
            adapter.get('planting_depth'),
            adapter.get('spacing'),
            adapter.get('days_to_maturity'),
            adapter.get('water_needs'),
            adapter.get('irrigation_frequency'),
            adapter.get('water_amount_per_week'),
            adapter.get('soil_ph'),
            adapter.get('soil_type'),
            adapter.get('nitrogen_requirement'),
            adapter.get('phosphorus_requirement'),
            adapter.get('potassium_requirement'),
            adapter.get('fertilizer_npk'),
            adapter.get('fertilizer_recommendations'),
            adapter.get('organic_fertilizer_options'),
            adapter.get('secondary_nutrients'),
            adapter.get('micronutrients'),
            adapter.get('sun_requirements'),
            adapter.get('temperature_range'),
            adapter.get('hardiness_zone'),
            adapter.get('companion_plants'),
            adapter.get('pest_resistance'),
            adapter.get('planting_season'),
            adapter.get('harvest_time'),
            adapter.get('source_url'),
            adapter.get('scraped_date'),
            adapter.get('data_source')
        )
        
        cursor.execute('''
            INSERT OR IGNORE INTO crops (
                name, common_name, scientific_name, category, planting_depth, spacing,
                days_to_maturity, water_needs, irrigation_frequency, water_amount_per_week,
                soil_ph, soil_type, nitrogen_requirement, phosphorus_requirement,
                potassium_requirement, fertilizer_npk, fertilizer_recommendations,
                organic_fertilizer_options, secondary_nutrients, micronutrients,
                sun_requirements, temperature_range, hardiness_zone, companion_plants,
                pest_resistance, planting_season, harvest_time, source_url,
                scraped_date, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', crop_data)
        
        self.connection.commit()
        logging.info(f"Inserted crop: {adapter.get('name')}")
    
    def insert_nutrient_recipe(self, adapter):
        """Insert nutrient recipe data into nutrient_recipes table"""
        cursor = self.connection.cursor()
        
        recipe_data = (
            adapter.get('crop_name'),
            adapter.get('fertilizer_type'),
            adapter.get('npk_ratio'),
            adapter.get('application_rate'),
            adapter.get('application_frequency'),
            adapter.get('application_timing'),
            adapter.get('nitrogen_requirements'),
            adapter.get('phosphorus_requirements'),
            adapter.get('potassium_requirements'),
            adapter.get('calcium_requirements'),
            adapter.get('magnesium_requirements'),
            adapter.get('micronutrients'),
            adapter.get('organic_fertilizers'),
            adapter.get('synthetic_fertilizers'),
            adapter.get('compost_recommendations'),
            adapter.get('mulching_recommendations'),
            adapter.get('watering_frequency'),
            adapter.get('watering_amount'),
            adapter.get('irrigation_method'),
            adapter.get('source_url'),
            adapter.get('scraped_date')
        )
        
        cursor.execute('''
            INSERT OR IGNORE INTO nutrient_recipes (
                crop_name, fertilizer_type, npk_ratio, application_rate,
                application_frequency, application_timing, nitrogen_requirements,
                phosphorus_requirements, potassium_requirements, calcium_requirements,
                magnesium_requirements, micronutrients, organic_fertilizers,
                synthetic_fertilizers, compost_recommendations, mulching_recommendations,
                watering_frequency, watering_amount, irrigation_method,
                source_url, scraped_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', recipe_data)
        
        self.connection.commit()
        logging.info(f"Inserted nutrient recipe for: {adapter.get('crop_name')}")


class TestPipeline:
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('crops_data.json', 'w', encoding='utf-8')
        self.items = []
    
    def close_spider(self, spider):
        json.dump(self.items, self.file, indent=2, ensure_ascii=False)
        self.file.close()
    
    def process_item(self, item, spider):
        self.items.append(ItemAdapter(item).asdict())
        return item

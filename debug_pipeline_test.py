"""
Debug test to see what's happening with DatabasePipeline
"""

import os
import sys
import sqlite3
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crop_scraper.pipelines import DatabasePipeline, ValidationPipeline
from crop_scraper.items import CropItem
from itemadapter import ItemAdapter


def test_pipeline_directly():
    """Test the pipeline directly without Scrapy"""
    print("=== TESTING PIPELINE DIRECTLY ===")
      # Create a test item
    item = CropItem()
    item['name'] = 'Test Tomatoes'
    item['scientific_name'] = 'Solanum lycopersicum'
    item['category'] = 'Vegetable'
    item['soil_ph'] = '6.0-6.8'
    item['water_needs'] = 'Regular watering'
    item['source_url'] = 'https://test.example.com'
    
    print(f"Created test item: {item['name']}")
    
    # Test ValidationPipeline
    validation_pipeline = ValidationPipeline()
    validated_item = validation_pipeline.process_item(item, None)
    print(f"Validation pipeline added timestamp: {validated_item.get('scraped_date')}")
    
    # Test DatabasePipeline
    print("\nTesting DatabasePipeline...")
    
    # Remove existing database for clean test
    if os.path.exists('crops.db'):
        os.remove('crops.db')
        print("Removed existing database")
    
    db_pipeline = DatabasePipeline()
    
    try:
        # Open spider (creates connection and tables)
        db_pipeline.open_spider(None)
        print("✓ Database connection opened and tables created")
        
        # Process item
        result_item = db_pipeline.process_item(validated_item, None)
        print(f"✓ Item processed: {result_item['name']}")
        
        # Close spider
        db_pipeline.close_spider(None)
        print("✓ Database connection closed")
        
    except Exception as e:
        print(f"✗ Error in database pipeline: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check database contents
    print("\n=== CHECKING DATABASE CONTENTS ===")
    
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Check crops table
        cursor.execute("SELECT * FROM crops")
        crops = cursor.fetchall()
        print(f"Crops in database: {len(crops)}")
        
        if crops:
            # Get column names
            cursor.execute("PRAGMA table_info(crops)")
            columns = [col[1] for col in cursor.fetchall()]
            
            for crop in crops:
                print(f"  Crop: {crop[1]} (ID: {crop[0]})")  # name is second column
                print(f"    Scientific name: {crop[2]}")
                print(f"    Source URL: {crop[23]}")  # Adjust index based on schema
        else:
            print("  No crops found in database")
        
        conn.close()
    else:
        print("✗ Database file not found")


def check_database_schema():
    """Check the database schema"""
    print("\n=== CHECKING DATABASE SCHEMA ===")
    
    if os.path.exists('crops.db'):
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(crops)")
        columns = cursor.fetchall()
        
        print("Crops table columns:")
        for i, col in enumerate(columns):
            print(f"  {i}: {col[1]} ({col[2]})")
        
        conn.close()
    else:
        print("No database file found")


if __name__ == "__main__":
    test_pipeline_directly()
    check_database_schema()

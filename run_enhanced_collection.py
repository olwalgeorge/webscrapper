#!/usr/bin/env python3
"""
Enhanced spider run to collect more comprehensive nutrition data
"""
import os
import sys
import sqlite3
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.nutrition_spider import NutritionSpider

def run_enhanced_nutrition_collection():
    """Run the nutrition spider with enhanced settings"""
    
    print("🌱 ENHANCED NUTRITION DATA COLLECTION")
    print("=====================================")
    print("Collecting detailed nutrition data from multiple sources...")
    
    # Clean any existing output
    if os.path.exists('nutrition_data.json'):
        os.remove('nutrition_data.json')
    
    start_time = time.time()
    
    # Get enhanced settings
    settings = get_project_settings()
    
    # Configure for comprehensive nutrition collection
    settings.update({
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {
            'crop_scraper.pipelines.ValidationPipeline': 300,
            'crop_scraper.pipelines.DatabasePipeline': 400,
            'crop_scraper.pipelines.JsonWriterPipeline': 500,
        },
        'FEEDS': {
            'nutrition_data.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
        # Enhanced extraction settings
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    })
    
    # Run the spider
    process = CrawlerProcess(settings)
    process.crawl(NutritionSpider)
    process.start()
    
    end_time = time.time()
    
    print(f"\n⏱️  Collection completed in {end_time - start_time:.1f} seconds")
    
    # Analyze results
    analyze_nutrition_results()

def analyze_nutrition_results():
    """Analyze the nutrition collection results"""
    print("\n📊 NUTRITION DATA ANALYSIS")
    print("==========================")
    
    # Check JSON output
    if os.path.exists('nutrition_data.json'):
        try:
            import json
            with open('nutrition_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ JSON: {len(data)} items collected")
            
            # Analyze data types
            crop_items = [item for item in data if item.get('name')]
            recipe_items = [item for item in data if item.get('crop_name')]
            
            print(f"   - Crop profiles: {len(crop_items)}")
            print(f"   - Nutrient recipes: {len(recipe_items)}")
            
            # Show sample data
            if crop_items:
                sample = crop_items[0]
                print(f"\n📋 Sample crop: {sample.get('name', 'Unknown')}")
                print(f"   - Nitrogen req: {sample.get('nitrogen_requirement', 'Not specified')[:50]}...")
                print(f"   - Fertilizer: {sample.get('fertilizer_recommendations', 'Not specified')[:50]}...")
                
        except Exception as e:
            print(f"❌ JSON analysis error: {e}")
    else:
        print("❌ No JSON output file created")
    
    # Check database
    if os.path.exists('crops.db'):
        try:
            conn = sqlite3.connect('crops.db')
            cursor = conn.cursor()
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM crops")
            total_crops = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM nutrient_recipes")
            total_recipes = cursor.fetchone()[0]
            
            print(f"\n💾 Database updated:")
            print(f"   - Total crops: {total_crops}")
            print(f"   - Total recipes: {total_recipes}")
            
            # Check recent additions
            cursor.execute("""
                SELECT name, nitrogen_requirement, phosphorus_requirement, potassium_requirement 
                FROM crops 
                WHERE created_at > datetime('now', '-1 hour')
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            
            recent_crops = cursor.fetchall()
            if recent_crops:
                print(f"\n🆕 Recently added crops:")
                for crop in recent_crops:
                    name = crop[0]
                    n_req = crop[1][:30] + "..." if crop[1] else "None"
                    p_req = crop[2][:30] + "..." if crop[2] else "None"
                    k_req = crop[3][:30] + "..." if crop[3] else "None"
                    print(f"   - {name}")
                    print(f"     N: {n_req}")
                    print(f"     P: {p_req}")
                    print(f"     K: {k_req}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database analysis error: {e}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Run: python dashboard.py  (start web dashboard)")
    print("2. Run: python data_analysis.py  (generate reports)")
    print("3. Scale up: Add more crop varieties and sources")

def main():
    """Main function"""
    print("Enhanced Nutrition Data Collection System")
    print("WD330 Agricultural Informatics Project")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('crops.db'):
        print("⚠️  No database found. Run a basic spider first.")
        return
    
    # Run enhanced collection
    try:
        run_enhanced_nutrition_collection()
        print(f"\n🎉 ENHANCED COLLECTION COMPLETE!")
        print("Your agricultural nutrition database has been updated with detailed nutrition data.")
        
    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

"""
Test script for multi-crop scraping with all pipelines
"""

import os
import sys
import sqlite3
import json
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crop_scraper.spiders.mini_test_spider import MiniTestSpider


def clean_test_environment():
    """Clean up any existing test files"""
    files_to_clean = ['crops.db', 'crops_data.json']
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Removed existing {file}")
            except Exception as e:
                print(f"Warning: Could not remove {file}: {e}")


def run_multi_crop_spider():
    """Run spider to scrape multiple crops"""
    print("\n=== RUNNING MULTI-CROP SPIDER TEST ===")
    print("Scraping: Tomatoes, Carrots, Lettuce, Peppers, Beans")
    
    start_time = time.time()
    
    # Get project settings
    settings = get_project_settings()
    
    # Ensure all pipelines are enabled
    settings.set('ITEM_PIPELINES', {
        'crop_scraper.pipelines.ValidationPipeline': 300,
        'crop_scraper.pipelines.DatabasePipeline': 400,
        'crop_scraper.pipelines.JsonWriterPipeline': 500,
    })
    
    # Configure for multi-crop scraping
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('DOWNLOAD_DELAY', 2)
    settings.set('RANDOMIZE_DOWNLOAD_DELAY', True)
    settings.set('CONCURRENT_REQUESTS', 1)
    
    # Create and run spider
    process = CrawlerProcess(settings)
    process.crawl(MiniTestSpider)
    process.start()
    
    end_time = time.time()
    print(f"✓ Spider completed in {end_time - start_time:.2f} seconds")


def analyze_multi_crop_results():
    """Analyze results from multi-crop scraping"""
    print("\n=== MULTI-CROP RESULTS ANALYSIS ===")
    
    # Check JSON output
    if os.path.exists('crops_data.json'):
        try:
            with open('crops_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✓ JSON: {len(data)} crops exported")
                
                for i, item in enumerate(data, 1):
                    name = item.get('name', 'Unknown')
                    source = item.get('source_url', 'Unknown')
                    fields = len([k for k, v in item.items() if v and v != ''])
                    print(f"  {i}. {name} - {fields} fields populated")
                    
        except Exception as e:
            print(f"✗ JSON: Error reading file - {e}")
            return False
    else:
        print("✗ JSON: No output file created")
        return False
    
    # Check database
    if os.path.exists('crops.db'):
        try:
            conn = sqlite3.connect('crops.db')
            cursor = conn.cursor()
            
            # Check crops data
            cursor.execute("SELECT COUNT(*) FROM crops")
            crops_count = cursor.fetchone()[0]
            print(f"✓ Database: {crops_count} crops stored")
            
            # List all crops
            cursor.execute("SELECT name, source_url, scraped_date FROM crops ORDER BY created_at")
            all_crops = cursor.fetchall()
            
            print("  Crops in database:")
            for i, crop in enumerate(all_crops, 1):
                print(f"    {i}. {crop[0]} ({crop[1].split('/')[-1]})")
            
            # Check for data quality
            cursor.execute("SELECT COUNT(*) FROM crops WHERE water_needs IS NOT NULL AND water_needs != ''")
            crops_with_water = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM crops WHERE sun_requirements IS NOT NULL AND sun_requirements != ''")
            crops_with_sun = cursor.fetchone()[0]
            
            print(f"  Data quality:")
            print(f"    - Crops with water info: {crops_with_water}/{crops_count}")
            print(f"    - Crops with sun info: {crops_with_sun}/{crops_count}")
            
            conn.close()
            return crops_count > 0
            
        except Exception as e:
            print(f"✗ Database: Error accessing database - {e}")
            return False
    else:
        print("✗ Database: No database file created")
        return False


def test_data_export():
    """Test exporting data in different formats"""
    print(f"\n=== TESTING DATA EXPORT ===")
    
    if not os.path.exists('crops.db'):
        print("✗ No database to export")
        return
    
    try:
        conn = sqlite3.connect('crops.db')
        cursor = conn.cursor()
        
        # Export to CSV-like format
        cursor.execute("""
            SELECT name, category, water_needs, sun_requirements, soil_ph, 
                   planting_depth, spacing, source_url 
            FROM crops 
            ORDER BY name
        """)
        
        crops_data = cursor.fetchall()
        
        # Create simple report
        with open('crops_report.txt', 'w', encoding='utf-8') as f:
            f.write("CROP NUTRITION DATA REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            for crop in crops_data:
                f.write(f"Crop: {crop[0]}\n")
                f.write(f"Category: {crop[1] or 'N/A'}\n")
                f.write(f"Water Needs: {crop[2] or 'N/A'}\n")
                f.write(f"Sun Requirements: {crop[3] or 'N/A'}\n")
                f.write(f"Soil pH: {crop[4] or 'N/A'}\n")
                f.write(f"Planting Depth: {crop[5] or 'N/A'}\n")
                f.write(f"Spacing: {crop[6] or 'N/A'}\n")
                f.write(f"Source: {crop[7]}\n")
                f.write("-" * 30 + "\n")
        
        print(f"✓ Created crops_report.txt with {len(crops_data)} crops")
        conn.close()
        
    except Exception as e:
        print(f"✗ Export error: {e}")


def main():
    """Main test function"""
    print("=== MULTI-CROP SCRAPY PIPELINE TEST ===")
    print("Testing comprehensive data collection from multiple crop pages")
    
    # Clean environment
    clean_test_environment()
    
    # Run multi-crop spider
    try:
        run_multi_crop_spider()
    except Exception as e:
        print(f"✗ Spider failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Analyze results
    success = analyze_multi_crop_results()
    
    # Test data export
    test_data_export()
    
    # Final status
    if success:
        print(f"\n🎉 MULTI-CROP TEST PASSED!")
        print("Successfully demonstrated:")
        print("- ✓ Multi-crop web scraping")
        print("- ✓ Batch data processing") 
        print("- ✓ Database storage at scale")
        print("- ✓ Data export capabilities")
        print("\nNext: Scale to more websites and crop types!")
    else:
        print(f"\n❌ MULTI-CROP TEST FAILED")
    
    return success


if __name__ == "__main__":
    main()

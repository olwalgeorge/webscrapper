#!/usr/bin/env python3
"""
Simple test scraper using only standard library to verify our approach
"""
import urllib.request
import urllib.parse
import json
import re
import sqlite3
from html.parser import HTMLParser
import time
import os

class CropDataParser(HTMLParser):
    """Simple HTML parser to extract crop information"""
    
    def __init__(self):
        super().__init__()
        self.in_plant_info = False
        self.current_tag = None
        self.data = {}
        self.current_text = ""
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        # Look for elements that might contain plant information
        for attr_name, attr_value in attrs:
            if attr_name == "class" and any(keyword in attr_value.lower() 
                                          for keyword in ['plant', 'crop', 'garden', 'grow']):
                self.in_plant_info = True
                
    def handle_endtag(self, tag):
        if self.in_plant_info and tag in ['div', 'section', 'article']:
            self.in_plant_info = False
        self.current_tag = None
        
    def handle_data(self, data):
        if self.in_plant_info:
            self.current_text += data.strip() + " "

def create_database():
    """Create SQLite database for storing crop data"""
    conn = sqlite3.connect('crop_data.db')
    cursor = conn.cursor()
    
    # Create crops table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            water_needs TEXT,
            soil_ph TEXT,
            sun_requirements TEXT,
            planting_depth TEXT,
            spacing TEXT,
            days_to_maturity TEXT,
            fertilizer_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create nutrient_recipes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrient_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER,
            nitrogen_ppm REAL,
            phosphorus_ppm REAL,
            potassium_ppm REAL,
            calcium_ppm REAL,
            magnesium_ppm REAL,
            sulfur_ppm REAL,
            iron_ppm REAL,
            ph_range TEXT,
            ec_range TEXT,
            notes TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (crop_id) REFERENCES crops (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def test_simple_request():
    """Test basic web request functionality"""
    try:
        # Test a simple request to a reliable site
        url = "http://httpbin.org/get"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print("✓ Basic web request successful!")
            print(f"  Response from: {data['url']}")
            return True
            
    except Exception as e:
        print(f"✗ Web request failed: {e}")
        return False

def test_crop_site_access():
    """Test access to our target crop information sites"""
    sites_to_test = [
        "https://www.almanac.com/plant/tomatoes",
        "https://www.gardeningknowhow.com/edible/vegetables/tomato/growing-tomatoes.htm"
    ]
    
    for url in sites_to_test:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
                print(f"✓ Successfully accessed: {url}")
                print(f"  Content length: {len(content)} characters")
                
                # Look for crop-related keywords
                keywords = ['water', 'fertilizer', 'nutrient', 'soil', 'plant', 'grow']
                found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
                print(f"  Found keywords: {', '.join(found_keywords)}")
                
                time.sleep(2)  # Be respectful
                
        except Exception as e:
            print(f"✗ Failed to access {url}: {e}")

def extract_sample_data():
    """Extract some sample crop data to test our parsing"""
    sample_crops = [
        {
            "name": "Tomato",
            "water_needs": "1-2 inches per week",
            "soil_ph": "6.0-6.8",
            "sun_requirements": "Full sun (6-8 hours)",
            "planting_depth": "1/4 inch",
            "spacing": "18-36 inches apart",
            "days_to_maturity": "60-80 days",
            "fertilizer_info": "High potassium, moderate nitrogen"
        },
        {
            "name": "Lettuce",
            "water_needs": "1 inch per week",
            "soil_ph": "6.0-7.0",
            "sun_requirements": "Partial shade",
            "planting_depth": "1/4 inch",
            "spacing": "4-6 inches apart",
            "days_to_maturity": "30-45 days",
            "fertilizer_info": "High nitrogen for leafy growth"
        }
    ]
    
    # Store in database
    conn = sqlite3.connect('crop_data.db')
    cursor = conn.cursor()
    
    for crop in sample_crops:
        cursor.execute('''
            INSERT INTO crops (name, water_needs, soil_ph, sun_requirements, 
                             planting_depth, spacing, days_to_maturity, fertilizer_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            crop['name'], crop['water_needs'], crop['soil_ph'], 
            crop['sun_requirements'], crop['planting_depth'], 
            crop['spacing'], crop['days_to_maturity'], crop['fertilizer_info']
        ))
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT * FROM crops')
    rows = cursor.fetchall()
    print(f"\n✓ Stored {len(rows)} crop records in database:")
    for row in rows:
        print(f"  - {row[1]} ({row[2]})")
    
    conn.close()

def main():
    """Run all tests"""
    print("🌱 Testing Crop Scraper Setup")
    print("=" * 40)
    
    # Test 1: Create database
    print("\n1. Creating database...")
    create_database()
    
    # Test 2: Test basic connectivity
    print("\n2. Testing web connectivity...")
    test_simple_request()
    
    # Test 3: Test access to crop sites
    print("\n3. Testing crop website access...")
    test_crop_site_access()
    
    # Test 4: Test data storage
    print("\n4. Testing data storage...")
    extract_sample_data()
    
    print("\n" + "=" * 40)
    print("🎉 Basic testing complete!")
    print("\nNext steps:")
    print("- Install Scrapy and other packages")
    print("- Run the full spiders")
    print("- Expand to more crop sources")

if __name__ == "__main__":
    main()

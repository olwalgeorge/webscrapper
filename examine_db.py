#!/usr/bin/env python3
"""
Script to examine the current database contents and data quality
"""
import sqlite3
import json

def examine_database():
    conn = sqlite3.connect('crops.db')
    cursor = conn.cursor()
    
    # Check table schema
    print("=== CROPS TABLE SCHEMA ===")
    cursor.execute('PRAGMA table_info(crops)')
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    print("\n=== NUTRIENT_RECIPES TABLE SCHEMA ===")
    cursor.execute('PRAGMA table_info(nutrient_recipes)')
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Check data quality
    print("\n=== DATA QUALITY ANALYSIS ===")
    cursor.execute('SELECT COUNT(*) FROM crops')
    total_crops = cursor.fetchone()[0]
    print(f"Total crops: {total_crops}")
    
    cursor.execute('SELECT COUNT(*) FROM nutrient_recipes')
    total_recipes = cursor.fetchone()[0]
    print(f"Total nutrient recipes: {total_recipes}")
    
    # Check field completeness
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN water_needs IS NOT NULL AND water_needs != '' THEN 1 END) as water_complete,
            COUNT(CASE WHEN soil_ph IS NOT NULL AND soil_ph != '' THEN 1 END) as ph_complete,
            COUNT(CASE WHEN fertilizer_recommendations IS NOT NULL AND fertilizer_recommendations != '' THEN 1 END) as fert_complete,
            COUNT(CASE WHEN sun_requirements IS NOT NULL AND sun_requirements != '' THEN 1 END) as sun_complete
        FROM crops
    ''')
    completeness = cursor.fetchone()
    print(f"\nData completeness:")
    print(f"- Water needs: {completeness[0]}/{total_crops} ({completeness[0]/total_crops*100:.1f}%)")
    print(f"- Soil pH: {completeness[1]}/{total_crops} ({completeness[1]/total_crops*100:.1f}%)")
    print(f"- Fertilizer info: {completeness[2]}/{total_crops} ({completeness[2]/total_crops*100:.1f}%)")
    print(f"- Sun requirements: {completeness[3]}/{total_crops} ({completeness[3]/total_crops*100:.1f}%)")
    
    # Show sample data
    print("\n=== SAMPLE CROP DATA ===")
    cursor.execute('SELECT name, water_needs, soil_ph, fertilizer_recommendations FROM crops LIMIT 3')
    crops = cursor.fetchall()
    
    for i, crop in enumerate(crops, 1):
        print(f"\n{i}. {crop[0]}")
        print(f"   Water: {crop[1][:100] if crop[1] else 'None'}{'...' if crop[1] and len(crop[1]) > 100 else ''}")
        print(f"   pH: {crop[2][:100] if crop[2] else 'None'}{'...' if crop[2] and len(crop[2]) > 100 else ''}")
        print(f"   Fertilizer: {crop[3][:100] if crop[3] else 'None'}{'...' if crop[3] and len(crop[3]) > 100 else ''}")
    
    conn.close()

if __name__ == "__main__":
    examine_database()

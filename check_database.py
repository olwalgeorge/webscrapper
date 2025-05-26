#!/usr/bin/env python3
"""
Script to check the database content
"""

import sqlite3
import os

def check_database():
    db_path = 'crops.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist")
        return
    
    print(f"Checking database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if crops table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crops'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✓ Crops table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(crops)")
            columns = cursor.fetchall()
            print(f"Table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM crops")
            count = cursor.fetchone()[0]
            print(f"✓ Found {count} rows in crops table")
            
            # Get sample data
            if count > 0:
                cursor.execute("SELECT * FROM crops LIMIT 3")
                rows = cursor.fetchall()
                print("\nSample data:")
                for i, row in enumerate(rows, 1):
                    print(f"Row {i}: {row}")
        else:
            print("✗ Crops table does not exist")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()

#!/usr/bin/env python3
"""
Test URL accessibility and basic content extraction
"""
import requests
from bs4 import BeautifulSoup
import time

def test_urls():
    """Test if our target URLs are accessible"""
    urls = [
        'https://www.almanac.com/plant/tomatoes',
        'https://www.almanac.com/plant/carrots',
        'https://www.almanac.com/plant/lettuce',
        'https://www.almanac.com/plant/peppers',
        'https://www.almanac.com/plant/beans'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("=== URL ACCESSIBILITY TEST ===")
    
    for url in urls:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for potential crop name
                h1_tags = soup.find_all('h1')
                if h1_tags:
                    print(f"  H1 tags found: {[h1.get_text().strip() for h1 in h1_tags[:2]]}")
                
                # Check for keywords
                page_text = soup.get_text().lower()
                keywords = ['water', 'soil', 'sun', 'fertilizer', 'plant']
                found_keywords = [kw for kw in keywords if kw in page_text]
                print(f"  Keywords found: {found_keywords}")
                
                # Check for potential content sections
                content_divs = soup.find_all(['div', 'section', 'article'])
                print(f"  Content sections: {len(content_divs)}")
            
            time.sleep(2)  # Be respectful
            
        except requests.RequestException as e:
            print(f"  ❌ Error: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_urls()

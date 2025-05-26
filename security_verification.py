#!/usr/bin/env python3
"""
Security Verification Script for Agricultural Nutrition Database Project
This script verifies that all security measures are properly implemented.
"""

import os
import re
import glob
from pathlib import Path

def check_for_exposed_keys():
    """Check for any exposed API keys in the codebase."""
    print("🔍 Checking for exposed API keys...")
    
    # Common API key patterns
    patterns = [
        r'AIza[0-9A-Za-z-_]{35}',  # Google API key
        r'["\']api_key["\']\s*:\s*["\'][^"\']{20,}["\']',  # JSON API keys
        r'api_key\s*=\s*["\'][^"\']{20,}["\']',  # Python API keys
        r'GOOGLE_MAPS_API_KEY\s*=\s*["\'][^"\']{20,}["\']',  # Specific Google Maps keys
    ]
    
    excluded_dirs = {'.git', '__pycache__', '.scrapy', 'node_modules', '.env'}
    exposed_keys = []
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.txt', '.md', '.yml', '.yaml')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                # Exclude template files and environment examples
                                if not any(x in filepath for x in ['.template', '.example', 'security_verification.py']):
                                    exposed_keys.append((filepath, matches))
                except Exception as e:
                    continue
    
    if exposed_keys:
        print("❌ EXPOSED API KEYS FOUND:")
        for filepath, keys in exposed_keys:
            print(f"  📁 {filepath}: {keys}")
        return False
    else:
        print("✅ No exposed API keys found")
        return True

def check_gitignore():
    """Verify .gitignore includes security patterns."""
    print("\n🔍 Checking .gitignore security patterns...")
    
    required_patterns = [
        '.env',
        '.scrapy/',
        '*api_key*',
        '*secret*',
        '*token*',
        '*.db',
        '*.sqlite'
    ]
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"❌ Missing .gitignore patterns: {missing_patterns}")
            return False
        else:
            print("✅ All required .gitignore patterns present")
            return True
    except FileNotFoundError:
        print("❌ .gitignore file not found")
        return False

def check_environment_setup():
    """Check if environment variables are properly configured."""
    print("\n🔍 Checking environment variable setup...")
    
    # Check if .env.template exists
    if not os.path.exists('.env.template'):
        print("❌ .env.template file missing")
        return False
    
    # Check if settings.py uses environment variables
    try:
        with open('crop_scraper/settings.py', 'r') as f:
            settings_content = f.read()
        
        required_imports = ['os.getenv', 'load_dotenv']
        missing_imports = []
        
        for imp in required_imports:
            if imp not in settings_content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"❌ Missing imports in settings.py: {missing_imports}")
            return False
        
        print("✅ Environment variable setup properly configured")
        return True
    except FileNotFoundError:
        print("❌ crop_scraper/settings.py not found")
        return False

def check_scrapy_cache_removed():
    """Verify .scrapy directory has been removed."""
    print("\n🔍 Checking if .scrapy cache has been removed...")
    
    if os.path.exists('.scrapy'):
        print("❌ .scrapy directory still exists - should be removed")
        return False
    else:
        print("✅ .scrapy directory properly removed")
        return True

def main():
    """Run all security checks."""
    print("🛡️  SECURITY VERIFICATION REPORT")
    print("=" * 50)
    
    checks = [
        check_for_exposed_keys(),
        check_gitignore(),
        check_environment_setup(),
        check_scrapy_cache_removed()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 ALL SECURITY CHECKS PASSED!")
        print("\n📋 NEXT STEPS:")
        print("1. Copy .env.template to .env and add your actual API keys")
        print("2. Never commit .env files to version control")
        print("3. Regularly rotate API keys for enhanced security")
        print("4. Consider using a secrets management service for production")
    else:
        print("⚠️  SOME SECURITY CHECKS FAILED!")
        print("Please address the issues above before deploying.")
    
    return all(checks)

if __name__ == "__main__":
    main()

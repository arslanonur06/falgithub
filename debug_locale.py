#!/usr/bin/env python3
"""
Debug script to check locale file structure.
"""

import json

def debug_locale_file(file_path):
    """Debug a locale file structure."""
    print(f"🔍 Debugging {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return
    
    # Check specific keys
    test_keys = [
        "astrology.birth_chart",
        "menu.astrology",
        "common.back"
    ]
    
    for key in test_keys:
        keys = key.split('.')
        current = data
        
        print(f"\n🔍 Checking key: {key}")
        print(f"   Keys to traverse: {keys}")
        
        # Navigate through nested dictionary
        for i, k in enumerate(keys):
            print(f"   Step {i+1}: Looking for '{k}' in {type(current)}")
            if isinstance(current, dict):
                if k in current:
                    current = current[k]
                    print(f"   ✅ Found '{k}': {type(current)}")
                else:
                    print(f"   ❌ Key '{k}' not found in {list(current.keys())}")
                    break
            else:
                print(f"   ❌ Current is not a dict: {type(current)}")
                break
        else:
            print(f"   ✅ Final value: {current}")

if __name__ == "__main__":
    debug_locale_file("locales/en.json")
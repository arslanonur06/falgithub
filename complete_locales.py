#!/usr/bin/env python3
"""
Complete all locale files by adding missing sections from English locale
"""

import json
import os

def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json_file(file_path, data):
    """Save JSON file safely"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def complete_locale_file(locale_file, en_data):
    """Complete a locale file with missing sections from English"""
    print(f"\n🔧 Completing {locale_file}...")
    
    # Load current locale data
    current_data = load_json_file(locale_file)
    if not current_data:
        return False
    
    # Find the last key in current data to know where to insert
    current_keys = list(current_data.keys())
    if not current_keys:
        return False
    
    # Get all keys from English data
    en_keys = list(en_data.keys())
    
    # Find missing keys
    missing_keys = [key for key in en_keys if key not in current_data]
    
    if not missing_keys:
        print(f"✅ {locale_file} is already complete")
        return True
    
    print(f"📝 Adding {len(missing_keys)} missing sections...")
    
    # Add missing sections
    for key in missing_keys:
        if key in en_data:
            current_data[key] = en_data[key]
            print(f"  ➕ Added: {key}")
    
    # Save updated file
    save_json_file(locale_file, current_data)
    return True

def main():
    """Main function"""
    print("🔮 Completing all locale files...")
    
    # Load English locale as reference
    en_file = 'locales/en.json'
    en_data = load_json_file(en_file)
    if not en_data:
        print("❌ Could not load English locale file")
        return
    
    print(f"✅ Loaded English locale with {len(en_data)} sections")
    
    # Get all locale files except English
    locales_dir = 'locales'
    locale_files = []
    
    for file in os.listdir(locales_dir):
        if file.endswith('.json') and file != 'en.json':
            locale_files.append(os.path.join(locales_dir, file))
    
    print(f"📁 Found {len(locale_files)} locale files to complete")
    
    # Complete each locale file
    completed_count = 0
    for locale_file in locale_files:
        if complete_locale_file(locale_file, en_data):
            completed_count += 1
    
    print(f"\n🎉 Completed {completed_count}/{len(locale_files)} locale files!")

if __name__ == '__main__':
    main()
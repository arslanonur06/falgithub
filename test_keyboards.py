#!/usr/bin/env python3
"""
Test script to verify keyboard creation without translation errors.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_keyboard_creation():
    """Test that all keyboards can be created without errors."""
    print("🔍 Testing keyboard creation...")
    
    try:
        # Import the i18n utility first
        from src.utils.i18n import i18n
        
        # Test i18n loading
        i18n.load_translations()
        print("✅ i18n translations loaded")
        
        # Test getting some common keys
        test_keys = [
            "menu.astrology",
            "menu.fortune", 
            "menu.profile",
            "menu.premium",
            "menu.referral",
            "menu.help",
            "menu.settings",
            "common.back",
            "common.yes",
            "common.no",
            "common.cancel",
            "profile.edit_info",
            "profile.usage_stats",
            "profile.notifications",
            "fortune.tarot",
            "fortune.coffee"
        ]
        
        for key in test_keys:
            text = i18n.get_text(key, "en")
            if not text or text == key:
                print(f"❌ Missing or invalid key: {key}")
                return False
            else:
                print(f"✅ {key}: {text}")
        
        # Test keyboard creation
        from src.keyboards.main import MainKeyboards
        
        # Test main menu keyboard
        try:
            main_kb = MainKeyboards.get_main_menu("en")
            print("✅ Main menu keyboard created successfully")
        except Exception as e:
            print(f"❌ Error creating main menu keyboard: {e}")
            return False
        
        # Test astrology menu keyboard
        try:
            astro_kb = MainKeyboards.get_astrology_menu("en")
            print("✅ Astrology menu keyboard created successfully")
        except Exception as e:
            print(f"❌ Error creating astrology menu keyboard: {e}")
            return False
        
        # Test fortune menu keyboard
        try:
            fortune_kb = MainKeyboards.get_fortune_menu("en")
            print("✅ Fortune menu keyboard created successfully")
        except Exception as e:
            print(f"❌ Error creating fortune menu keyboard: {e}")
            return False
        
        # Test profile menu keyboard
        try:
            profile_kb = MainKeyboards.get_profile_menu("en")
            print("✅ Profile menu keyboard created successfully")
        except Exception as e:
            print(f"❌ Error creating profile menu keyboard: {e}")
            return False
        
        # Test language selection keyboard
        try:
            lang_kb = MainKeyboards.get_language_selection("en")
            print("✅ Language selection keyboard created successfully")
        except Exception as e:
            print(f"❌ Error creating language selection keyboard: {e}")
            return False
        
        # Test other keyboards
        try:
            yes_no_kb = MainKeyboards.get_yes_no("en")
            cancel_kb = MainKeyboards.get_cancel("en")
            back_kb = MainKeyboards.get_back_button("en")
            print("✅ Other keyboards created successfully")
        except Exception as e:
            print(f"❌ Error creating other keyboards: {e}")
            return False
        
        print("🎉 All keyboard tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_all_languages():
    """Test keyboard creation in all supported languages."""
    print("\n🔍 Testing all languages...")
    
    try:
        from src.utils.i18n import i18n
        from src.keyboards.main import MainKeyboards
        
        languages = ["en", "tr", "es"]
        
        for lang in languages:
            print(f"\n📝 Testing {lang} language...")
            
            try:
                # Test main menu in this language
                main_kb = MainKeyboards.get_main_menu(lang)
                print(f"✅ {lang} main menu keyboard created")
                
                # Test a few key translations
                test_keys = ["menu.astrology", "common.back", "profile.edit_info"]
                for key in test_keys:
                    text = i18n.get_text(key, lang)
                    if text and text != key:
                        print(f"✅ {lang} {key}: {text}")
                    else:
                        print(f"❌ {lang} missing key: {key}")
                        return False
                        
            except Exception as e:
                print(f"❌ Error with {lang} language: {e}")
                return False
        
        print("🎉 All language tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Language test error: {e}")
        return False

def main():
    """Run all keyboard tests."""
    print("🚀 Starting Keyboard Tests")
    print("=" * 50)
    
    tests = [
        ("Keyboard Creation", test_keyboard_creation),
        ("All Languages", test_all_languages),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test passed")
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All keyboard tests passed! No translation errors found.")
        return True
    else:
        print("⚠️  Some keyboard tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
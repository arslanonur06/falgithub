#!/usr/bin/env python3
"""
Test script to verify the bot menu is working correctly.
"""

import asyncio
from src.utils.i18n import i18n
from src.keyboards.main import MainKeyboards

async def test_menu():
    """Test the menu functionality."""
    print("🔍 Testing bot menu functionality...")
    
    # Test i18n
    print("\n📝 Testing i18n translations:")
    print(f"   - menu.astrology (EN): {i18n.get_text('menu.astrology', 'en')}")
    print(f"   - menu.fortune (EN): {i18n.get_text('menu.fortune', 'en')}")
    print(f"   - menu.profile (EN): {i18n.get_text('menu.profile', 'en')}")
    print(f"   - menu.premium (EN): {i18n.get_text('menu.premium', 'en')}")
    print(f"   - menu.referral (EN): {i18n.get_text('menu.referral', 'en')}")
    print(f"   - menu.help (EN): {i18n.get_text('menu.help', 'en')}")
    
    # Test keyboard generation
    print("\n⌨️ Testing keyboard generation:")
    try:
        keyboard = MainKeyboards.get_main_menu_keyboard("en")
        print(f"   - Main menu keyboard created successfully")
        print(f"   - Number of rows: {len(keyboard.inline_keyboard)}")
        
        # Check each button text
        for i, row in enumerate(keyboard.inline_keyboard):
            for j, button in enumerate(row):
                print(f"   - Row {i+1}, Button {j+1}: {button.text}")
                
    except Exception as e:
        print(f"   ❌ Error creating keyboard: {e}")
        return False
    
    print("\n✅ Menu test completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_menu()) 
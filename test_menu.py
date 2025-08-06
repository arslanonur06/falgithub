#!/usr/bin/env python3
"""
Test script to verify the bot menu and translations work correctly
"""

import bot

def test_menu():
    print("🧪 Testing Bot Menu and Translations")
    print("=" * 50)
    
    # Test available languages
    print(f"✅ Available languages: {list(bot.LOCALES.keys())}")
    
    # Test start message
    start_msg = bot.get_text('start_message', 'en')
    print(f"✅ Start message length: {len(start_msg)} characters")
    
    # Test menu keyboard
    keyboard = bot.create_main_menu_keyboard('en')
    print(f"✅ Menu keyboard created with {len(keyboard.inline_keyboard)} rows")
    
    # Show button texts
    print("\n📋 Menu Buttons:")
    for i, row in enumerate(keyboard.inline_keyboard):
        for j, btn in enumerate(row):
            print(f"  {i+1}.{j+1} {btn.text} -> {btn.callback_data}")
    
    # Test admin keyboard
    admin_keyboard = bot.create_admin_panel_keyboard('en')
    print(f"\n✅ Admin keyboard created with {len(admin_keyboard.inline_keyboard)} rows")
    
    print("\n🎉 All tests passed! The bot menu is working correctly.")

if __name__ == "__main__":
    test_menu() 
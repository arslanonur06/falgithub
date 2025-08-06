#!/usr/bin/env python3
"""
Verification script for JSON files and routing completeness.
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_json_files():
    """Check that all JSON files are properly formatted and contain required keys."""
    print("🔍 Checking JSON files...")
    
    # Check locale files
    locale_files = [
        "locales/en.json",
        "locales/tr.json", 
        "locales/es.json"
    ]
    
    required_locale_keys = [
        "menu.main_title",
        "menu.astrology",
        "menu.fortune", 
        "menu.profile",
        "menu.premium",
        "menu.referral",
        "menu.help",
        "common.back",
        "common.yes",
        "common.no",
        "common.cancel",
        "error.general",
        "error.user_not_found",
        "profile.title",
        "profile.name",
        "profile.username",
        "profile.language",
        "profile.premium_status",
        "profile.premium_active",
        "profile.premium_inactive",
        "profile.premium_expires",
        "language.select",
        "language.changed",
        "help.message",
        "message.default_response",
        "referral.my_info",
        "referral.stats",
        "referral.leaderboard",
        "referral.rewards",
        "referral.share",
        "referral.link_copied",
        "referral.copy_link",
        "referral.share_telegram",
        "referral.share_whatsapp",
        "referral.share_text",
        "astrology.birth_chart",
        "astrology.daily_horoscope",
        "astrology.weekly_horoscope",
        "astrology.monthly_horoscope",
        "astrology.compatibility",
        "astrology.moon_calendar",
        "fortune.tarot_reading",
        "fortune.coffee_reading",
        "fortune.dream_interpretation",
        "fortune.palm_reading",
        "payment.premium_plans",
        "payment.plan_details",
        "payment.buy_plan",
        "payment.subscription_management",
        "admin.stats",
        "admin.users",
        "admin.premium",
        "admin.logs",
        "admin.settings"
    ]
    
    for locale_file in locale_files:
        if not os.path.exists(locale_file):
            print(f"❌ Missing locale file: {locale_file}")
            continue
            
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for required keys
            missing_keys = []
            for key in required_locale_keys:
                if not key_exists_in_nested_dict(data, key):
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"⚠️  {locale_file} missing keys: {missing_keys[:5]}...")
            else:
                print(f"✅ {locale_file} - All required keys present")
                
        except json.JSONDecodeError as e:
            print(f"❌ {locale_file} - Invalid JSON: {e}")
        except Exception as e:
            print(f"❌ {locale_file} - Error: {e}")
    
    # Check config files
    config_files = [
        "config/prompts.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {config_file} - Valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file} - Invalid JSON: {e}")
        else:
            print(f"⚠️  {config_file} - File not found (optional)")

def key_exists_in_nested_dict(data, key_path):
    """Check if a nested key exists in a dictionary."""
    keys = key_path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    
    return True

def check_routing_completeness():
    """Check that all callback routing is properly implemented."""
    print("\n🔍 Checking routing completeness...")
    
    # Define expected callback patterns
    expected_callbacks = {
        # User callbacks
        "main_menu": "UserHandlers.show_main_menu",
        "profile_menu": "UserHandlers.show_profile", 
        "language": "UserHandlers.show_language_menu",
        "set_lang_": "UserHandlers.handle_language_change",
        "help_menu": "UserHandlers.show_help",
        "copy_referral_link": "UserHandlers.handle_copy_referral_link",
        "back_to_": "UserHandlers.handle_back_button",
        
        # Astrology callbacks
        "astrology_menu": "astrology_handlers.show_astrology_menu",
        "birth_chart": "astrology_handlers.handle_birth_chart",
        "daily_horoscope": "astrology_handlers.handle_daily_horoscope",
        "weekly_horoscope": "astrology_handlers.handle_weekly_horoscope", 
        "monthly_horoscope": "astrology_handlers.handle_monthly_horoscope",
        "compatibility": "astrology_handlers.handle_compatibility",
        "moon_calendar": "astrology_handlers.handle_moon_calendar",
        "zodiac_": "astrology_handlers.handle_zodiac_selection",
        "daily_horoscope_": "astrology_handlers.handle_zodiac_selection",
        "weekly_horoscope_": "astrology_handlers.handle_zodiac_selection",
        "monthly_horoscope_": "astrology_handlers.handle_zodiac_selection",
        "compat_": "astrology_handlers.handle_compatibility_selection",
        
        # Fortune callbacks
        "fortune_menu": "fortune_handlers.show_fortune_menu",
        "tarot_reading": "fortune_handlers.handle_tarot_reading",
        "coffee_reading": "fortune_handlers.handle_coffee_reading",
        "dream_interpretation": "fortune_handlers.handle_dream_interpretation",
        "palm_reading": "fortune_handlers.handle_palm_reading",
        
        # Payment callbacks
        "premium_menu": "payment_handlers.show_premium_menu",
        "plan_details_": "payment_handlers.show_plan_details",
        "buy_plan_": "payment_handlers.initiate_purchase",
        "subscription_management": "payment_handlers.show_subscription_management",
        "cancel_subscription": "payment_handlers.cancel_subscription",
        "confirm_cancellation": "payment_handlers.confirm_cancellation",
        
        # Admin callbacks
        "admin_": "admin_handlers.handle_admin_callback",
        
        # Referral callbacks
        "referral_menu": "referral_handlers.show_referral_menu",
        "referral_info": "referral_handlers.show_referral_info",
        "referral_stats": "referral_handlers.show_referral_stats",
        "referral_leaderboard": "referral_handlers.show_referral_leaderboard",
        "referral_rewards": "referral_handlers.show_referral_rewards",
        "share_referral": "referral_handlers.share_referral_link"
    }
    
    # Check main_new.py for routing implementation
    main_file = "main_new.py"
    if not os.path.exists(main_file):
        print(f"❌ Main file not found: {main_file}")
        return False
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_routes = []
        for callback_pattern, handler in expected_callbacks.items():
            if callback_pattern not in content and not any(pattern in content for pattern in callback_pattern.split('_')):
                missing_routes.append(f"{callback_pattern} -> {handler}")
        
        if missing_routes:
            print(f"⚠️  Missing routes in {main_file}:")
            for route in missing_routes[:10]:  # Show first 10
                print(f"   - {route}")
            if len(missing_routes) > 10:
                print(f"   ... and {len(missing_routes) - 10} more")
        else:
            print(f"✅ {main_file} - All expected routes implemented")
            
    except Exception as e:
        print(f"❌ Error reading {main_file}: {e}")
        return False
    
    return True

def check_handler_methods():
    """Check that all handler classes have the required methods."""
    print("\n🔍 Checking handler methods...")
    
    handler_files = [
        ("src/handlers/user.py", "UserHandlers", [
            "start_command", "help_command", "profile_command", "language_command",
            "show_main_menu", "show_profile", "show_language_menu", "handle_language_change",
            "show_help", "handle_message", "handle_copy_referral_link", "handle_back_button",
            "callback_query_handler", "error_handler"
        ]),
        ("src/handlers/astrology.py", "AstrologyHandlers", [
            "show_astrology_menu", "handle_birth_chart", "handle_daily_horoscope",
            "handle_weekly_horoscope", "handle_monthly_horoscope", "handle_compatibility",
            "handle_moon_calendar", "handle_zodiac_selection", "handle_compatibility_selection"
        ]),
        ("src/handlers/fortune.py", "FortuneHandlers", [
            "show_fortune_menu", "handle_tarot_reading", "handle_coffee_reading",
            "handle_dream_interpretation", "handle_palm_reading", "handle_photo_input",
            "handle_text_input"
        ]),
        ("src/handlers/payment.py", "PaymentHandlers", [
            "show_premium_menu", "show_premium_plans", "show_plan_details",
            "initiate_purchase", "handle_pre_checkout", "handle_successful_payment",
            "show_subscription_management", "cancel_subscription", "confirm_cancellation"
        ]),
        ("src/handlers/admin.py", "AdminHandlers", [
            "admin_command", "gift_command", "cancel_command", "handle_admin_callback"
        ]),
        ("src/handlers/referral.py", "ReferralHandlers", [
            "show_referral_menu", "show_referral_info", "show_referral_stats",
            "show_referral_leaderboard", "show_referral_rewards", "share_referral_link",
            "process_referral_start", "complete_referral"
        ])
    ]
    
    all_methods_found = True
    
    for file_path, class_name, expected_methods in handler_files:
        if not os.path.exists(file_path):
            print(f"❌ Handler file not found: {file_path}")
            all_methods_found = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_methods = []
            for method in expected_methods:
                if f"def {method}" not in content and f"async def {method}" not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"⚠️  {file_path} - Missing methods: {missing_methods}")
                all_methods_found = False
            else:
                print(f"✅ {file_path} - All methods present")
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_methods_found = False
    
    return all_methods_found

def check_keyboard_methods():
    """Check that all keyboard classes have the required methods."""
    print("\n🔍 Checking keyboard methods...")
    
    keyboard_files = [
        ("src/keyboards/main.py", "MainKeyboards", [
            "get_main_menu", "get_astrology_menu", "get_fortune_menu", "get_profile_menu",
            "get_language_selection", "get_yes_no", "get_cancel", "get_back_button",
            "get_reply_keyboard"
        ]),
        ("src/keyboards/astrology.py", "AstrologyKeyboards", [
            "get_astrology_menu", "get_zodiac_selection", "get_compatibility_menu",
            "get_premium_upgrade_keyboard", "get_back_button"
        ]),
        ("src/keyboards/fortune.py", "FortuneKeyboards", [
            "get_fortune_menu", "get_premium_upgrade_keyboard", "get_back_button"
        ]),
        ("src/keyboards/payment.py", "PaymentKeyboards", [
            "get_premium_plans_keyboard", "get_plan_details_keyboard", "get_premium_user_keyboard",
            "get_subscription_management_keyboard", "get_cancel_confirmation_keyboard",
            "get_premium_upgrade_keyboard", "get_support_keyboard", "get_main_menu_keyboard",
            "get_back_button"
        ]),
        ("src/keyboards/admin.py", "AdminKeyboards", [
            "get_admin_main_menu", "get_admin_users_keyboard", "get_admin_premium_keyboard",
            "get_admin_settings_keyboard", "get_back_to_admin_keyboard"
        ]),
        ("src/keyboards/referral.py", "ReferralKeyboards", [
            "get_referral_menu", "get_referral_info_keyboard", "get_share_keyboard",
            "get_back_button"
        ])
    ]
    
    all_methods_found = True
    
    for file_path, class_name, expected_methods in keyboard_files:
        if not os.path.exists(file_path):
            print(f"❌ Keyboard file not found: {file_path}")
            all_methods_found = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_methods = []
            for method in expected_methods:
                if f"def {method}" not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"⚠️  {file_path} - Missing methods: {missing_methods}")
                all_methods_found = False
            else:
                print(f"✅ {file_path} - All methods present")
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_methods_found = False
    
    return all_methods_found

def main():
    """Run all verification checks."""
    print("🚀 Starting JSON and Routing Verification")
    print("=" * 50)
    
    checks = [
        ("JSON Files", check_json_files),
        ("Routing Completeness", check_routing_completeness),
        ("Handler Methods", check_handler_methods),
        ("Keyboard Methods", check_keyboard_methods),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 Running {check_name} check...")
        try:
            if check_func():
                print(f"✅ {check_name} check passed")
                passed += 1
            else:
                print(f"❌ {check_name} check failed")
        except Exception as e:
            print(f"❌ {check_name} check error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All verifications passed! The bot is ready for deployment.")
        return True
    else:
        print("⚠️  Some verifications failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Simple test to verify all required translation keys exist in locale files.
"""

import json
import os

def check_locale_file(file_path, required_keys):
    """Check if a locale file has all required keys."""
    print(f"🔍 Checking {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False
    
    missing_keys = []
    
    for key in required_keys:
        keys = key.split('.')
        current = data
        
        # Navigate through nested dictionary
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                missing_keys.append(key)
                break
    
    if missing_keys:
        print(f"⚠️  Missing keys in {file_path}: {missing_keys}")
        return False
    else:
        print(f"✅ {file_path} - All required keys present")
        return True

def main():
    """Check all locale files."""
    print("🚀 Checking Locale Files")
    print("=" * 50)
    
    # Required keys for keyboard functionality
    required_keys = [
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
        "fortune.coffee",
        "fortune.tarot_reading",
        "fortune.coffee_reading",
        "fortune.dream_interpretation",
        "fortune.palm_reading",
        "astrology.birth_chart",
        "astrology.daily_horoscope",
        "astrology.weekly_horoscope",
        "astrology.monthly_horoscope",
        "astrology.compatibility",
        "astrology.moon_calendar",
        "payment.premium_plans",
        "payment.plan_details",
        "payment.buy_plan",
        "payment.subscription_management",
        "admin.stats",
        "admin.users",
        "admin.premium",
        "admin.logs",
        "admin.settings",
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
        "error.general",
        "error.user_not_found",
        "language.select",
        "language.changed",
        "help.message",
        "message.default_response"
    ]
    
    locale_files = [
        "locales/en.json",
        "locales/tr.json",
        "locales/es.json"
    ]
    
    all_passed = True
    
    for file_path in locale_files:
        if not check_locale_file(file_path, required_keys):
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All locale files have the required keys!")
        print("✅ No translation errors should occur in keyboard creation.")
        return True
    else:
        print("⚠️  Some locale files are missing required keys.")
        print("❌ This may cause 'text must be of type string' errors.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
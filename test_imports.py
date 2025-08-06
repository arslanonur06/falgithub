#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly.
"""

import sys
import os

def test_imports():
    """Test all module imports."""
    print("🔍 Testing imports...")
    
    try:
        # Test config imports
        print("✅ Testing config imports...")
        from config.settings import settings
        print(f"   - Settings loaded: {settings.BOT_NAME}")
        
        # Test utils imports
        print("✅ Testing utils imports...")
        from src.utils.i18n import i18n
        from src.utils.logger import logger
        from src.utils.helpers import format_currency, calculate_moon_phase
        from src.utils.validators import validate_user_input
        print("   - Utils modules imported successfully")
        
        # Test models imports
        print("✅ Testing models imports...")
        from src.models.user import User
        from src.models.referral import Referral, ReferralStats
        from src.models.payment import Payment, Subscription, Invoice
        print("   - Models imported successfully")
        
        # Test services imports
        print("✅ Testing services imports...")
        from src.services.database import db_service
        from src.services.ai_service import ai_service
        from src.services.payment_service import payment_service
        print("   - Services imported successfully")
        
        # Test keyboards imports
        print("✅ Testing keyboards imports...")
        from src.keyboards.main import MainKeyboards
        from src.keyboards.astrology import AstrologyKeyboards
        from src.keyboards.fortune import FortuneKeyboards
        from src.keyboards.payment import PaymentKeyboards
        from src.keyboards.admin import AdminKeyboards
        from src.keyboards.referral import ReferralKeyboards
        print("   - Keyboards imported successfully")
        
        # Test handlers imports
        print("✅ Testing handlers imports...")
        from src.handlers.user import UserHandlers
        from src.handlers.payment import PaymentHandlers
        from src.handlers.referral import ReferralHandlers
        print("   - Handlers imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_i18n():
    """Test i18n functionality."""
    print("\n🔍 Testing i18n functionality...")
    
    try:
        from src.utils.i18n import i18n
        
        # Test basic text retrieval
        text = i18n.get_text("menu.main_title", "en")
        print(f"   - English main title: {text}")
        
        text = i18n.get_text("common.back", "en")
        print(f"   - English back button: {text}")
        
        # Test nested key retrieval
        text = i18n.get_text("profile.title", "en")
        print(f"   - English profile title: {text}")
        
        print("✅ i18n functionality working!")
        return True
        
    except Exception as e:
        print(f"❌ i18n error: {e}")
        return False

def test_keyboards():
    """Test keyboard generation."""
    print("\n🔍 Testing keyboard generation...")
    
    try:
        from src.keyboards.main import MainKeyboards
        
        # Test main menu keyboard
        keyboard = MainKeyboards.get_main_menu_keyboard("en")
        print(f"   - Main menu keyboard created: {len(keyboard.inline_keyboard)} rows")
        
        # Test language selection keyboard
        keyboard = MainKeyboards.get_language_selection_keyboard()
        print(f"   - Language selection keyboard created: {len(keyboard.inline_keyboard)} rows")
        
        print("✅ Keyboard generation working!")
        return True
        
    except Exception as e:
        print(f"❌ Keyboard error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting import tests...\n")
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test i18n
        i18n_ok = test_i18n()
        
        # Test keyboards
        keyboards_ok = test_keyboards()
        
        if i18n_ok and keyboards_ok:
            print("\n🎉 All tests passed! The modular structure is working correctly.")
            return True
        else:
            print("\n⚠️ Some tests failed. Check the errors above.")
            return False
    else:
        print("\n❌ Import tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
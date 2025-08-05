#!/usr/bin/env python3
"""
Integration test script for the Fal Gram Bot modular structure.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🔍 Testing imports...")
    
    try:
        # Test configuration imports
        from config.settings import settings
        from config.database import DatabaseConfig
        from config.logging import setup_logging
        print("✅ Configuration modules imported successfully")
        
        # Test utility imports
        from src.utils.i18n import i18n
        from src.utils.helpers import generate_referral_code, calculate_moon_phase
        from src.utils.validators import validator
        from src.utils.logger import get_logger
        print("✅ Utility modules imported successfully")
        
        # Test model imports
        from src.models.user import User
        from src.models.referral import Referral, ReferralStats
        from src.models.payment import Payment, Subscription, Invoice
        print("✅ Model modules imported successfully")
        
        # Test service imports
        from src.services.database import db_service
        from src.services.ai_service import ai_service
        from src.services.payment_service import payment_service
        print("✅ Service modules imported successfully")
        
        # Test keyboard imports
        from src.keyboards.main import MainKeyboards
        from src.keyboards.astrology import AstrologyKeyboards
        from src.keyboards.fortune import FortuneKeyboards
        from src.keyboards.payment import PaymentKeyboards
        from src.keyboards.admin import AdminKeyboards
        from src.keyboards.referral import ReferralKeyboards
        print("✅ Keyboard modules imported successfully")
        
        # Test handler imports
        from src.handlers.user import UserHandlers
        from src.handlers.astrology import astrology_handlers
        from src.handlers.fortune import fortune_handlers
        from src.handlers.payment import payment_handlers
        from src.handlers.admin import admin_handlers
        from src.handlers.referral import referral_handlers
        print("✅ Handler modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_models():
    """Test model functionality."""
    print("\n🔍 Testing models...")
    
    try:
        from src.models.user import User
        from src.models.referral import Referral, ReferralStats
        from src.models.payment import Payment, Subscription, Invoice
        
        # Test User model
        user = User(
            user_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        user_dict = user.to_dict()
        user_from_dict = User.from_dict(user_dict)
        assert user.user_id == user_from_dict.user_id
        print("✅ User model working correctly")
        
        # Test Referral model
        referral = Referral(
            referrer_id=12345,
            referred_id=67890,
            referral_code="TEST123"
        )
        referral_dict = referral.to_dict()
        referral_from_dict = Referral.from_dict(referral_dict)
        assert referral.referrer_id == referral_from_dict.referrer_id
        print("✅ Referral model working correctly")
        
        # Test Payment model
        payment = Payment(
            payment_id="pay_123",
            user_id=12345,
            amount=100.0
        )
        payment_dict = payment.to_dict()
        payment_from_dict = Payment.from_dict(payment_dict)
        assert payment.payment_id == payment_from_dict.payment_id
        print("✅ Payment model working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\n🔍 Testing utilities...")
    
    try:
        from src.utils.helpers import generate_referral_code, calculate_moon_phase
        from src.utils.validators import validator
        
        # Test referral code generation
        code1 = generate_referral_code(12345)
        code2 = generate_referral_code(12345)
        assert code1 == code2  # Should be deterministic
        assert len(code1) > 0
        print("✅ Referral code generation working")
        
        # Test moon phase calculation
        moon_phase = calculate_moon_phase()
        assert 'phase' in moon_phase
        assert 'illumination' in moon_phase
        print("✅ Moon phase calculation working")
        
        # Test validators
        assert validator.validate_name("John") == True
        assert validator.validate_email("test@example.com") == True
        assert validator.validate_phone("+1234567890") == True
        print("✅ Validators working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility test error: {e}")
        return False

def test_keyboards():
    """Test keyboard generation."""
    print("\n🔍 Testing keyboards...")
    
    try:
        from src.keyboards.main import MainKeyboards
        from src.keyboards.astrology import AstrologyKeyboards
        from src.keyboards.fortune import FortuneKeyboards
        from src.keyboards.payment import PaymentKeyboards
        from src.keyboards.admin import AdminKeyboards
        from src.keyboards.referral import ReferralKeyboards
        
        # Test main keyboard
        main_kb = MainKeyboards.get_main_menu("en")
        assert main_kb is not None
        print("✅ Main keyboard working")
        
        # Test astrology keyboard
        astro_kb = AstrologyKeyboards.get_astrology_menu("en")
        assert astro_kb is not None
        print("✅ Astrology keyboard working")
        
        # Test fortune keyboard
        fortune_kb = FortuneKeyboards.get_fortune_menu("en")
        assert fortune_kb is not None
        print("✅ Fortune keyboard working")
        
        # Test payment keyboard
        payment_kb = PaymentKeyboards.get_premium_plans_keyboard("en")
        assert payment_kb is not None
        print("✅ Payment keyboard working")
        
        # Test admin keyboard
        admin_kb = AdminKeyboards.get_admin_main_menu("en")
        assert admin_kb is not None
        print("✅ Admin keyboard working")
        
        # Test referral keyboard
        referral_kb = ReferralKeyboards.get_referral_menu("en")
        assert referral_kb is not None
        print("✅ Referral keyboard working")
        
        return True
        
    except Exception as e:
        print(f"❌ Keyboard test error: {e}")
        return False

def test_i18n():
    """Test internationalization."""
    print("\n🔍 Testing internationalization...")
    
    try:
        from src.utils.i18n import i18n
        
        # Test loading translations
        i18n.load_translations()
        print("✅ Translations loaded")
        
        # Test getting text
        text = i18n.get_text("menu.main_title", "en")
        assert text is not None
        print("✅ Text retrieval working")
        
        # Test supported languages
        languages = i18n.get_supported_languages()
        assert len(languages) > 0
        print("✅ Supported languages working")
        
        return True
        
    except Exception as e:
        print(f"❌ i18n test error: {e}")
        return False

def test_services():
    """Test service initialization."""
    print("\n🔍 Testing services...")
    
    try:
        from src.services.database import db_service
        from src.services.ai_service import ai_service
        from src.services.payment_service import payment_service
        
        # Test service instances exist
        assert db_service is not None
        assert ai_service is not None
        assert payment_service is not None
        print("✅ Service instances created")
        
        # Test AI service connection test (without actual API calls)
        connections = ai_service.test_connection()
        assert isinstance(connections, dict)
        print("✅ AI service test method working")
        
        return True
        
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def test_handlers():
    """Test handler classes."""
    print("\n🔍 Testing handlers...")
    
    try:
        from src.handlers.user import UserHandlers
        from src.handlers.astrology import astrology_handlers
        from src.handlers.fortune import fortune_handlers
        from src.handlers.payment import payment_handlers
        from src.handlers.admin import admin_handlers
        from src.handlers.referral import referral_handlers
        
        # Test handler instances exist
        assert UserHandlers is not None
        assert astrology_handlers is not None
        assert fortune_handlers is not None
        assert payment_handlers is not None
        assert admin_handlers is not None
        assert referral_handlers is not None
        print("✅ Handler instances created")
        
        # Test handler methods exist
        assert hasattr(UserHandlers, 'start_command')
        assert hasattr(astrology_handlers, 'show_astrology_menu')
        assert hasattr(fortune_handlers, 'show_fortune_menu')
        assert hasattr(payment_handlers, 'show_premium_menu')
        assert hasattr(admin_handlers, 'admin_command')
        assert hasattr(referral_handlers, 'show_referral_menu')
        print("✅ Handler methods exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Handler test error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "config/settings.py",
        "config/database.py",
        "config/logging.py",
        "src/utils/i18n.py",
        "src/utils/helpers.py",
        "src/utils/validators.py",
        "src/utils/logger.py",
        "src/models/user.py",
        "src/models/referral.py",
        "src/models/payment.py",
        "src/services/database.py",
        "src/services/ai_service.py",
        "src/services/payment_service.py",
        "src/keyboards/main.py",
        "src/keyboards/astrology.py",
        "src/keyboards/fortune.py",
        "src/keyboards/payment.py",
        "src/keyboards/admin.py",
        "src/keyboards/referral.py",
        "src/handlers/user.py",
        "src/handlers/astrology.py",
        "src/handlers/fortune.py",
        "src/handlers/payment.py",
        "src/handlers/admin.py",
        "src/handlers/referral.py",
        "main_new.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Fal Gram Bot Integration Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Models", test_models),
        ("Utilities", test_utilities),
        ("Keyboards", test_keyboards),
        ("Internationalization", test_i18n),
        ("Services", test_services),
        ("Handlers", test_handlers),
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
        print("🎉 All tests passed! The modular structure is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
Main configuration settings for the Fal Gram Bot.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Main application settings."""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BOT_NAME: str = "Fal Gram Bot"
    BOT_VERSION: str = "3.1.1"
    
    # Admin Configuration
    ADMIN_ID: str = os.getenv("ADMIN_ID", "")
    
    # Payment Configuration
    PAYMENT_PROVIDER_TOKEN: str = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Database Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Premium Features
    PREMIUM_ENABLED: bool = True
    FREE_DAILY_LIMIT: int = 3
    PREMIUM_DAILY_LIMIT: int = 50
    
    # Supported Languages
    SUPPORTED_LANGUAGES: list = ["en", "tr", "es"]
    DEFAULT_LANGUAGE: str = "en"
    
    # File Paths
    LOCALES_DIR: str = "locales"
    CONFIG_DIR: str = "config"
    
    # Webhook Configuration (if using webhooks)
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8443"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required settings are present."""
        required_vars = [
            "BOT_TOKEN",
            "GEMINI_API_KEY", 
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "PAYMENT_PROVIDER_TOKEN"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Check admin ID (optional but recommended)
        if not cls.ADMIN_ID:
            print("⚠️  Warning: ADMIN_ID not set. Admin features will be disabled.")
        
        return True
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "bot_token": cls.BOT_TOKEN,
            "bot_name": cls.BOT_NAME,
            "bot_version": cls.BOT_VERSION,
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "rate_limit_enabled": cls.RATE_LIMIT_ENABLED,
            "rate_limit_requests": cls.RATE_LIMIT_REQUESTS,
            "rate_limit_window": cls.RATE_LIMIT_WINDOW,
            "premium_enabled": cls.PREMIUM_ENABLED,
            "free_daily_limit": cls.FREE_DAILY_LIMIT,
            "premium_daily_limit": cls.PREMIUM_DAILY_LIMIT,
            "supported_languages": cls.SUPPORTED_LANGUAGES,
            "default_language": cls.DEFAULT_LANGUAGE
        }

# Global settings instance
settings = Settings()
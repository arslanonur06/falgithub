"""
Database configuration for the Fal Gram Bot.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration settings."""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Database Tables
    TABLES = {
        "users": "users",
        "referrals": "referrals", 
        "payments": "payments",
        "premium_plans": "premium_plans",
        "user_usage": "user_usage",
        "prompts": "prompts",
        "tarot_cards": "tarot_cards",
        "horoscopes": "horoscopes"
    }
    
    # Connection Settings
    CONNECTION_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    # Query Settings
    DEFAULT_LIMIT: int = 100
    MAX_LIMIT: int = 1000
    
    @classmethod
    def get_connection_config(cls) -> Dict[str, Any]:
        """Get database connection configuration."""
        return {
            "url": cls.SUPABASE_URL,
            "key": cls.SUPABASE_KEY,
            "timeout": cls.CONNECTION_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY
        }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate database configuration."""
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            print("❌ Missing Supabase configuration")
            return False
        return True

# Global database config instance
db_config = DatabaseConfig()
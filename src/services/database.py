"""
Database service for the Fal Gram Bot.
"""

import asyncio
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from config.database import db_config
from src.utils.logger import get_logger

logger = get_logger("database")

class DatabaseService:
    """Database service class."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize database connection."""
        try:
            if not db_config.validate():
                logger.error("Database configuration validation failed")
                return False
            
            self.client = create_client(
                db_config.SUPABASE_URL,
                db_config.SUPABASE_KEY
            )
            
            # Test connection
            await self._test_connection()
            
            self._initialized = True
            logger.info("Database service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            return False
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        try:
            # Simple query to test connection
            result = self.client.table("users").select("count", count="exact").limit(1).execute()
            logger.debug("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if database service is initialized."""
        return self._initialized
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            result = self.client.table("users").select("*").eq("user_id", user_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create new user."""
        try:
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                logger.info(f"User created successfully: {user_data.get('user_id')}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user data."""
        try:
            result = self.client.table("users").update(update_data).eq("user_id", user_id).execute()
            
            if result.data:
                logger.info(f"User updated successfully: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        try:
            result = self.client.table("users").delete().eq("user_id", user_id).execute()
            
            if result.data:
                logger.info(f"User deleted successfully: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_users_by_referral(self, referral_code: str) -> List[Dict[str, Any]]:
        """Get users referred by a specific referral code."""
        try:
            result = self.client.table("users").select("*").eq("referred_by", referral_code).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting users by referral {referral_code}: {e}")
            return []
    
    async def get_user_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user usage statistics."""
        try:
            result = self.client.table("user_usage").select("*").eq("user_id", user_id).execute()
            
            if result.data:
                return result.data[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting usage stats for user {user_id}: {e}")
            return {}
    
    async def increment_user_usage(self, user_id: int) -> bool:
        """Increment user usage counter."""
        try:
            # Get current usage
            current_usage = await self.get_user_usage_stats(user_id)
            
            if current_usage:
                # Update existing record
                new_count = current_usage.get('daily_count', 0) + 1
                result = self.client.table("user_usage").update({
                    "daily_count": new_count,
                    "total_count": current_usage.get('total_count', 0) + 1,
                    "last_used": "now()"
                }).eq("user_id", user_id).execute()
            else:
                # Create new record
                result = self.client.table("user_usage").insert({
                    "user_id": user_id,
                    "daily_count": 1,
                    "total_count": 1,
                    "last_used": "now()"
                }).execute()
            
            if result.data:
                logger.debug(f"Usage incremented for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error incrementing usage for user {user_id}: {e}")
            return False
    
    async def get_premium_plans(self) -> List[Dict[str, Any]]:
        """Get available premium plans."""
        try:
            result = self.client.table("premium_plans").select("*").eq("active", True).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting premium plans: {e}")
            return []
    
    async def create_payment_record(self, payment_data: Dict[str, Any]) -> bool:
        """Create payment record."""
        try:
            result = self.client.table("payments").insert(payment_data).execute()
            
            if result.data:
                logger.info(f"Payment record created: {payment_data.get('id')}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            return False
    
    async def close(self) -> None:
        """Close database connection."""
        try:
            if self.client:
                # Supabase client doesn't have explicit close method
                # but we can clean up our reference
                self.client = None
                self._initialized = False
                logger.info("Database service closed")
        except Exception as e:
            logger.error(f"Error closing database service: {e}")

# Global database service instance
db_service = DatabaseService()
"""
Database service for the Fal Gram Bot.
Handles all database operations using Supabase.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config.settings import settings
from src.utils.logger import logger

# Optional supabase import
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase not available - database features will be limited")


class DatabaseService:
    """Database service for Supabase operations."""
    
    def __init__(self):
        self.supabase: Client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Supabase client."""
        try:
            if not SUPABASE_AVAILABLE:
                logger.warning("Supabase library not available")
                return
                
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.warning("Supabase credentials not configured")
                return
            
            self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Supabase client: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.supabase is not None
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user. Be tolerant to schema differences."""
        try:
            if not self.is_connected():
                return False

            # First attempt: direct insert
            response = self.supabase.table('users').insert(user_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            # Retry without optional columns that might not exist
            try:
                sanitized = dict(user_data)
                for optional_key in (
                    'last_activity', 'total_readings', 'daily_readings_used',
                    'premium_expires_at', 'premium_plan', 'referral_code',
                    'premium_purchased_at', 'updated_at'
                ):
                    sanitized.pop(optional_key, None)
                response = self.supabase.table('users').insert(sanitized).execute()
                return len(response.data) > 0
            except Exception as e2:
                logger.error(f"Fallback insert failed: {e2}")
                return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID. Try common key names to match existing schema."""
        if not self.is_connected():
            return None
        errors = []
        for key in ('user_id', 'id', 'telegram_id'):
            try:
                response = (
                    self.supabase.table('users').select('*').eq(key, user_id).limit(1).execute()
                )
                if response.data:
                    # If record found but target key missing, ensure we mirror it to user_id for consistency
                    record = response.data[0]
                    if 'user_id' not in record and key != 'user_id':
                        try:
                            self.supabase.table('users').update({'user_id': user_id}).eq(key, user_id).execute()
                        except Exception:
                            pass
                    return record
            except Exception as e:
                errors.append(f"{key}={e}")
                continue
        logger.error(f"Error getting user {user_id}: tried keys user_id/id/telegram_id → {' | '.join(errors)}")
        return None
    
    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user data. Try multiple key names; drop unknown columns on failure."""
        if not self.is_connected():
            return False
        # Always stamp updated_at locally; may be dropped if schema lacks it
        enriched_updates = dict(updates)
        enriched_updates['updated_at'] = datetime.now().isoformat()

        for key in ('user_id', 'id', 'telegram_id'):
            try:
                response = self.supabase.table('users').update(enriched_updates).eq(key, user_id).execute()
                if len(response.data) > 0:
                    return True
            except Exception as e:
                last_err = e
                continue
        # Retry with sanitized fields to avoid unknown column errors
        try:
            sanitized = dict(enriched_updates)
            for optional_key in (
                'last_activity', 'total_readings', 'daily_readings_used', 'updated_at',
                'premium_expires_at', 'premium_plan', 'referral_code', 'premium_purchased_at'
            ):
                sanitized.pop(optional_key, None)
            for key in ('user_id', 'id', 'telegram_id'):
                try:
                    response = self.supabase.table('users').update(sanitized).eq(key, user_id).execute()
                    if len(response.data) > 0:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        logger.error(f"Error updating user {user_id}: {str(last_err) if 'last_err' in locals() else 'unknown'}")
        return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        try:
            if not self.is_connected():
                return []
            
            response = self.supabase.table('users').select('*').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    # Usage tracking
    async def increment_usage(self, user_id: int, usage_type: str = "reading") -> bool:
        """Increment user usage count."""
        try:
            if not self.is_connected():
                return False
            
            # Get current usage
            user = await self.get_user(user_id)
            if not user:
                return False
            
            # Update usage
            updates = {
                'total_readings': user.get('total_readings', 0) + 1,
                'daily_readings_used': user.get('daily_readings_used', 0) + 1,
                'last_activity': datetime.now().isoformat()
            }
            
            return await self.update_user(user_id, updates)
        except Exception as e:
            logger.error(f"Error incrementing usage for user {user_id}: {e}")
            return False
    
    async def reset_daily_usage(self) -> bool:
        """Reset daily usage for all users."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('users').update({
                'daily_readings_used': 0
            }).execute()
            
            logger.info(f"Reset daily usage for {len(response.data)} users")
            return True
        except Exception as e:
            logger.error(f"Error resetting daily usage: {e}")
            return False
    
    # Premium operations
    async def create_subscription_record(self, subscription_data: Dict[str, Any]) -> bool:
        """Create a subscription record."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('subscriptions').insert(subscription_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating subscription record: {e}")
            return False
    
    async def update_subscription_status(self, user_id: int, status: str) -> bool:
        """Update subscription status."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('subscriptions').update({
                'status': status,
                'cancelled_at': datetime.now().isoformat() if status == 'cancelled' else None
            }).eq('user_id', user_id).eq('status', 'active').execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating subscription status: {e}")
            return False
    
    # Payment operations
    async def create_payment_record(self, payment_data: Dict[str, Any]) -> bool:
        """Create a payment record."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('payments').insert(payment_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            return False
    
    async def update_payment_status(self, payment_id: str, status: str) -> bool:
        """Update payment status."""
        try:
            if not self.is_connected():
                return False
            
            updates = {'status': status}
            if status == 'completed':
                updates['completed_at'] = datetime.now().isoformat()
            elif status == 'failed':
                updates['failed_at'] = datetime.now().isoformat()
            elif status == 'refunded':
                updates['refunded_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('payments').update(updates).eq('payment_id', payment_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    # Referral operations
    async def create_referral_record(self, referral_data: Dict[str, Any]) -> bool:
        """Create a referral record."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('referrals').insert(referral_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating referral record: {e}")
            return False
    
    async def get_user_referrals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's referrals."""
        try:
            if not self.is_connected():
                return []
            
            response = self.supabase.table('referrals').select('*').eq('referrer_id', user_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting referrals for user {user_id}: {e}")
            return []
    
    # Logging operations
    async def add_log(self, message: str, level: str = "info", user_id: Optional[int] = None) -> bool:
        """Add a log entry."""
        try:
            if not self.is_connected():
                return False
            
            log_data = {
                'message': message,
                'level': level,
                'user_id': user_id,
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('logs').insert(log_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error adding log: {e}")
            return False
    
    async def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs."""
        try:
            if not self.is_connected():
                return []
            
            response = self.supabase.table('logs').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    # Prompts operations
    async def get_prompts(self) -> Dict[str, Any]:
        """Get AI prompts configuration."""
        try:
            if not self.is_connected():
                return {}
            
            response = self.supabase.table('prompts').select('*').execute()
            prompts = {}
            for prompt in response.data:
                prompts[prompt['key']] = prompt['value']
            return prompts
        except Exception as e:
            logger.error(f"Error getting prompts: {e}")
            return {}
    
    async def update_prompt(self, key: str, value: str) -> bool:
        """Update a prompt."""
        try:
            if not self.is_connected():
                return False
            
            response = self.supabase.table('prompts').upsert({
                'key': key,
                'value': value,
                'updated_at': datetime.now().isoformat()
            }).execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating prompt {key}: {e}")
            return False


# Global database service instance
db_service = DatabaseService() 
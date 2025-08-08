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

    async def get_premium_users(self) -> List[Dict[str, Any]]:
        """Get users with an active premium plan if possible; fallback to any non-free plan."""
        try:
            if not self.is_connected():
                return []
            try:
                # Prefer active based on expiry
                response = (
                    self.supabase
                    .table('users')
                    .select('*')
                    .neq('premium_plan', 'free')
                    .execute()
                )
                users = response.data or []
                # Filter locally by expiry if available
                now = datetime.utcnow()
                active: List[Dict[str, Any]] = []
                for u in users:
                    exp = u.get('premium_expires_at')
                    if not exp:
                        active.append(u)
                        continue
                    try:
                        dt = datetime.fromisoformat(str(exp).replace('Z', '+00:00'))
                        if dt > now:
                            active.append(u)
                    except Exception:
                        active.append(u)
                return active
            except Exception:
                # Fallback: any user marked is_premium
                response2 = self.supabase.table('users').select('*').eq('is_premium', True).execute()
                return response2.data or []
        except Exception as e:
            logger.error(f"Error getting premium users: {e}")
            return []

    async def get_payment_statistics(self) -> Dict[str, int]:
        """Aggregate payment stats from payment_transactions if available."""
        result = {'total_revenue': 0, 'revenue_today': 0, 'revenue_month': 0}
        if not self.is_connected():
            return result
        try:
            # Fetch recent payments to aggregate locally
            resp = (
                self.supabase
                .table('payment_transactions')
                .select('*')
                .eq('status', 'completed')
                .order('created_at', desc=True)
                .limit(1000)
                .execute()
            )
            rows = resp.data or []
            now = datetime.utcnow()
            start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for r in rows:
                amount = int(r.get('amount') or 0)
                result['total_revenue'] += amount
                ts = r.get('created_at')
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                except Exception:
                    dt = None
                if dt:
                    if dt >= start_today:
                        result['revenue_today'] += amount
                    if dt >= start_month:
                        result['revenue_month'] += amount
        except Exception as e:
            logger.error(f"Error aggregating payment statistics: {e}")
        return result
    
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

    async def get_top_referrers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return top referrers based on referred_count/referral_count."""
        try:
            if not self.is_connected():
                return []
            # Try sort by referred_count
            try:
                resp = (
                    self.supabase
                    .table('users')
                    .select('id, user_id, username, first_name, referred_count, referral_count')
                    .order('referred_count', desc=True)
                    .limit(limit)
                    .execute()
                )
                if resp.data:
                    return resp.data
            except Exception:
                pass
            # Fallback sort by referral_count
            resp2 = (
                self.supabase
                .table('users')
                .select('id, user_id, username, first_name, referred_count, referral_count')
                .order('referral_count', desc=True)
                .limit(limit)
                .execute()
            )
            return resp2.data or []
        except Exception as e:
            logger.error(f"Error getting top referrers: {e}")
            return []

    async def get_referral_counts_by_day(self, days: int = 7) -> List[Dict[str, Any]]:
        """Return counts of referrals per day for the last N days (client-side aggregation)."""
        if not self.is_connected():
            return []
        try:
            since = datetime.utcnow() - timedelta(days=days)
            resp = (
                self.supabase
                .table('referrals')
                .select('created_at')
                .gte('created_at', since.isoformat())
                .order('created_at')
                .limit(5000)
                .execute()
            )
            rows = resp.data or []
            buckets: Dict[str, int] = {}
            for r in rows:
                ts = r.get('created_at')
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    key = dt.strftime('%Y-%m-%d')
                except Exception:
                    key = 'unknown'
                buckets[key] = buckets.get(key, 0) + 1
            # Prepare sorted list
            keys = sorted(buckets.keys())
            return [{ 'date': k, 'count': buckets[k] } for k in keys]
        except Exception as e:
            logger.error(f"Error computing referral counts by day: {e}")
            return []

    async def get_referral_counts_by_month(self, months: int = 6) -> List[Dict[str, Any]]:
        """Return counts of referrals per calendar month for the last N months."""
        if not self.is_connected():
            return []
        try:
            now = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Approximate N months back by subtracting months*31 days, then filter client-side by month keys
            since = now - timedelta(days=31 * months)
            resp = (
                self.supabase
                .table('referrals')
                .select('created_at')
                .gte('created_at', since.isoformat())
                .order('created_at')
                .limit(10000)
                .execute()
            )
            rows = resp.data or []
            buckets: Dict[str, int] = {}
            for r in rows:
                ts = r.get('created_at')
                try:
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    key = dt.strftime('%Y-%m')
                except Exception:
                    key = 'unknown'
                buckets[key] = buckets.get(key, 0) + 1
            keys = sorted(buckets.keys())
            return [{ 'month': k, 'count': buckets[k] } for k in keys]
        except Exception as e:
            logger.error(f"Error computing referral counts by month: {e}")
            return []

    async def get_revenue_per_referral(self, days: Optional[int] = None) -> Dict[str, Any]:
        """Compute revenue per referral in Stars.

        If days is provided, restrict both revenue and referrals to last N days.
        Returns dict with totals and average.
        """
        result = {
            'total_revenue': 0,
            'total_referrals': 0,
            'avg_revenue_per_referral': 0.0,
        }
        if not self.is_connected():
            return result
        try:
            # Time window
            since_iso = None
            if days is not None:
                since_iso = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Revenue
            q = self.supabase.table('payment_transactions').select('amount, created_at').eq('status', 'completed')
            if since_iso:
                q = q.gte('created_at', since_iso)
            rev_rows = q.limit(10000).execute().data or []
            total_rev = 0
            for r in rev_rows:
                try:
                    total_rev += int(r.get('amount') or 0)
                except Exception:
                    continue

            # Referrals count
            q2 = self.supabase.table('referrals').select('id, created_at')
            if since_iso:
                q2 = q2.gte('created_at', since_iso)
            ref_rows = q2.limit(10000).execute().data or []
            total_refs = len(ref_rows)

            avg = (total_rev / total_refs) if total_refs > 0 else 0.0
            result.update({
                'total_revenue': total_rev,
                'total_referrals': total_refs,
                'avg_revenue_per_referral': round(avg, 2),
            })
        except Exception as e:
            logger.error(f"Error computing revenue per referral: {e}")
        return result

    async def get_referral_summary(self, user_id: int) -> Dict[str, Any]:
        """Compute referral summary (this week, this month, last invite) for a user.

        Falls back to zeros if table or fields are missing.
        """
        try:
            referrals = await self.get_user_referrals(user_id)
            if not referrals:
                return {
                    'this_week': 0,
                    'this_month': 0,
                    'last_invite_at': None,
                    'total_count': 0,
                }

            now = datetime.utcnow()
            week_start = now - timedelta(days=now.weekday())  # Monday
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            def parse_dt(value: Any) -> Optional[datetime]:
                if not value:
                    return None
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except Exception:
                    try:
                        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        return None

            dates: List[datetime] = []
            for r in referrals:
                dt = parse_dt(r.get('created_at') or r.get('inserted_at'))
                if dt:
                    dates.append(dt)

            this_week = sum(1 for d in dates if d >= week_start)
            this_month = sum(1 for d in dates if d >= month_start)
            last_invite_at = max(dates).isoformat() if dates else None

            return {
                'this_week': this_week,
                'this_month': this_month,
                'last_invite_at': last_invite_at,
                'total_count': len(referrals),
            }
        except Exception as e:
            logger.error(f"Error building referral summary for user {user_id}: {e}")
            return {
                'this_week': 0,
                'this_month': 0,
                'last_invite_at': None,
                'total_count': 0,
            }
    
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

    async def get_prompt(self, prompt_type: str, language: str) -> Optional[str]:
        """Fetch a single prompt text by type and language from Supabase.

        Supports both schemas:
        - columns: prompt_type, language, content


        
        - or: key, language, value
        """
        try:
            if not self.is_connected():
                return None

            # Try schema with prompt_type/content
            try:
                response = (
                    self.supabase
                    .table('prompts')
                    .select('*')
                    .eq('prompt_type', prompt_type)
                    .eq('language', language)
                    .limit(1)
                    .execute()
                )
                if response.data:
                    record = response.data[0]
                    if 'content' in record and record['content']:
                        return record['content']
            except Exception:
                pass

            # Try schema with key/value
            try:
                response2 = (
                    self.supabase
                    .table('prompts')
                    .select('*')
                    .eq('key', prompt_type)
                    .eq('language', language)
                    .limit(1)
                    .execute()
                )
                if response2.data:
                    record2 = response2.data[0]
                    if 'value' in record2 and record2['value']:
                        return record2['value']
            except Exception:
                pass

            # Fallback: single key like f"{prompt_type}.{language}"
            try:
                compound_key = f"{prompt_type}.{language}"
                response3 = (
                    self.supabase
                    .table('prompts')
                    .select('*')
                    .eq('key', compound_key)
                    .limit(1)
                    .execute()
                )
                if response3.data:
                    record3 = response3.data[0]
                    text = record3.get('value') or record3.get('content')
                    if text:
                        return text
            except Exception:
                pass

            return None
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_type}/{language}: {e}")
            return None
    
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
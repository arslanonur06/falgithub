"""
Payment service for the Fal Gram Bot.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from src.services.database import db_service
from src.utils.logger import get_logger
from config.settings import settings

logger = get_logger("payment_service")

class PaymentService:
    """Payment service for handling subscriptions and payments."""
    
    def __init__(self):
        self.provider_token = getattr(settings, 'PAYMENT_PROVIDER_TOKEN', None)
        self.currency = "TRY"
    
    def get_provider_token(self) -> str:
        """Get payment provider token."""
        if not self.provider_token:
            raise ValueError("Payment provider token not configured")
        return self.provider_token
    
    async def create_subscription(self, user_id: int, plan_name: str, duration_days: int) -> Dict[str, Any]:
        """Create a new subscription."""
        try:
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=duration_days)
            
            # Update user premium status
            success = await db_service.update_user(user_id, {
                'is_premium': True,
                'premium_plan': plan_name,
                'premium_expires_at': expiry_date.isoformat(),
                'premium_purchased_at': datetime.now().isoformat()
            })
            
            if success:
                # Create subscription record
                subscription_data = {
                    'user_id': user_id,
                    'plan_name': plan_name,
                    'status': 'active',
                    'start_date': datetime.now().isoformat(),
                    'end_date': expiry_date.isoformat(),
                    'created_at': datetime.now().isoformat()
                }
                
                await db_service.create_subscription_record(subscription_data)
                
                logger.info(f"Subscription created for user {user_id}, plan: {plan_name}")
                
                return {
                    'success': True,
                    'subscription_id': f"sub_{user_id}_{int(datetime.now().timestamp())}",
                    'expires_at': expiry_date.isoformat()
                }
            
            return {'success': False, 'error': 'Failed to update user'}
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_subscription(self, user_id: int) -> bool:
        """Cancel a subscription."""
        try:
            # Update user premium status
            success = await db_service.update_user(user_id, {
                'is_premium': False,
                'premium_plan': None,
                'premium_expires_at': None,
                'premium_cancelled_at': datetime.now().isoformat()
            })
            
            if success:
                # Update subscription record
                await db_service.update_subscription_status(user_id, 'cancelled')
                
                logger.info(f"Subscription cancelled for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False
    
    async def extend_subscription(self, user_id: int, additional_days: int) -> bool:
        """Extend an existing subscription."""
        try:
            # Get current user data
            user_data = await db_service.get_user(user_id)
            if not user_data or not user_data.get('is_premium'):
                return False
            
            # Calculate new expiry date
            current_expiry = user_data.get('premium_expires_at')
            if current_expiry:
                try:
                    expiry_date = datetime.fromisoformat(current_expiry)
                    new_expiry = expiry_date + timedelta(days=additional_days)
                except:
                    new_expiry = datetime.now() + timedelta(days=additional_days)
            else:
                new_expiry = datetime.now() + timedelta(days=additional_days)
            
            # Update user
            success = await db_service.update_user(user_id, {
                'premium_expires_at': new_expiry.isoformat()
            })
            
            if success:
                # Update subscription record
                await db_service.update_subscription_end_date(user_id, new_expiry.isoformat())
                
                logger.info(f"Subscription extended for user {user_id} by {additional_days} days")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error extending subscription: {e}")
            return False
    
    async def check_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """Check subscription status for a user."""
        try:
            user_data = await db_service.get_user(user_id)
            if not user_data:
                return {'has_subscription': False, 'error': 'User not found'}
            
            is_premium = user_data.get('is_premium', False)
            if not is_premium:
                return {'has_subscription': False}
            
            # Check if subscription has expired
            expires_at = user_data.get('premium_expires_at')
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expiry_date:
                        # Subscription has expired, update user
                        await db_service.update_user(user_id, {
                            'is_premium': False,
                            'premium_plan': None,
                            'premium_expires_at': None
                        })
                        return {'has_subscription': False, 'expired': True}
                except:
                    pass
            
            return {
                'has_subscription': True,
                'plan': user_data.get('premium_plan'),
                'expires_at': expires_at,
                'purchased_at': user_data.get('premium_purchased_at')
            }
            
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            return {'has_subscription': False, 'error': str(e)}
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics."""
        try:
            # Get all users
            all_users = await db_service.get_all_users()
            premium_users = await db_service.get_premium_users()
            
            total_users = len(all_users) if all_users else 0
            premium_count = len(premium_users) if premium_users else 0
            
            # Calculate plan distribution
            plan_distribution = {}
            if premium_users:
                for user in premium_users:
                    plan = user.get('premium_plan', 'unknown')
                    plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
            
            # Calculate revenue (this would come from payment records)
            revenue_stats = await db_service.get_payment_statistics()
            
            return {
                'total_users': total_users,
                'premium_users': premium_count,
                'conversion_rate': (premium_count / total_users * 100) if total_users > 0 else 0,
                'plan_distribution': plan_distribution,
                'revenue': revenue_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription analytics: {e}")
            return {
                'total_users': 0,
                'premium_users': 0,
                'conversion_rate': 0,
                'plan_distribution': {},
                'revenue': {}
            }
    
    async def process_refund(self, user_id: int, payment_id: str) -> bool:
        """Process a refund for a payment."""
        try:
            # Update payment record
            success = await db_service.update_payment_status(payment_id, 'refunded')
            
            if success:
                # Cancel subscription
                await self.cancel_subscription(user_id)
                
                logger.info(f"Refund processed for user {user_id}, payment {payment_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            return False
    
    async def get_payment_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get payment history for a user."""
        try:
            # This would fetch from payment records table
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return []
    
    async def validate_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Validate payment data."""
        try:
            required_fields = ['user_id', 'amount', 'currency', 'payment_id']
            
            for field in required_fields:
                if field not in payment_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate amount
            amount = payment_data.get('amount', 0)
            if amount <= 0:
                logger.error("Invalid payment amount")
                return False
            
            # Validate currency
            currency = payment_data.get('currency', '')
            if currency != self.currency:
                logger.error(f"Invalid currency: {currency}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating payment: {e}")
            return False
    
    async def create_invoice(self, user_id: int, plan_name: str, amount: float) -> Dict[str, Any]:
        """Create an invoice for payment."""
        try:
            plan_info = self._get_plan_info(plan_name)
            
            invoice_data = {
                'user_id': user_id,
                'plan_name': plan_name,
                'amount': amount,
                'currency': self.currency,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            # Store invoice in database
            await db_service.create_invoice_record(invoice_data)
            
            return {
                'success': True,
                'invoice_id': f"inv_{user_id}_{int(datetime.now().timestamp())}",
                'amount': amount,
                'currency': self.currency,
                'plan_name': plan_name
            }
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_plan_info(self, plan_name: str) -> Dict[str, Any]:
        """Get plan information."""
        plans = {
            'basic': {
                'price': 500,
                'duration': 30,
                'name': 'Basic Plan'
            },
            'premium': {
                'price': 1000,
                'duration': 30,
                'name': 'Premium Plan'
            },
            'vip': {
                'price': 2000,
                'duration': 30,
                'name': 'VIP Plan'
            }
        }
        
        return plans.get(plan_name, plans['premium'])

# Global payment service instance
payment_service = PaymentService()
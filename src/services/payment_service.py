"""
Payment service for the Fal Gram Bot.
Handles subscriptions, payments, and payment processing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config.settings import settings
from src.utils.logger import logger
from src.services.database import db_service


class PaymentService:
    """Payment service for handling subscriptions and payments."""
    
    def __init__(self):
        self.provider_token = getattr(settings, 'PAYMENT_PROVIDER_TOKEN', None)
        self.currency = "STARS"
    
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
                return {'active': False, 'plan': None, 'expires_at': None}
            
            is_premium = user_data.get('is_premium', False)
            plan_name = user_data.get('premium_plan')
            expires_at = user_data.get('premium_expires_at')
            
            if not is_premium:
                return {'active': False, 'plan': None, 'expires_at': None}
            
            # Check if subscription has expired
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
                        return {'active': False, 'plan': None, 'expires_at': None}
                except:
                    pass
            
            return {
                'active': True,
                'plan': plan_name,
                'expires_at': expires_at
            }
            
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            return {'active': False, 'plan': None, 'expires_at': None}
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics."""
        try:
            users = await db_service.get_all_users()
            
            total_users = len(users)
            premium_users = sum(1 for user in users if user.get('is_premium', False))
            active_subscriptions = 0
            
            for user in users:
                if user.get('is_premium', False):
                    expires_at = user.get('premium_expires_at')
                    if expires_at:
                        try:
                            expiry_date = datetime.fromisoformat(expires_at)
                            if datetime.now() < expiry_date:
                                active_subscriptions += 1
                        except:
                            pass
                    else:
                        active_subscriptions += 1
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'active_subscriptions': active_subscriptions,
                'premium_rate': (premium_users / total_users * 100) if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription analytics: {e}")
            return {
                'total_users': 0,
                'premium_users': 0,
                'active_subscriptions': 0,
                'premium_rate': 0
            }
    
    async def process_refund(self, user_id: int, payment_id: str) -> bool:
        """Process a refund."""
        try:
            # Update payment status
            success = await db_service.update_payment_status(payment_id, 'refunded')
            
            if success:
                # Cancel subscription if it exists
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
            # This would typically query the payments table
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return []
    
    async def validate_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Validate payment data."""
        try:
            required_fields = ['payment_id', 'user_id', 'amount', 'status']
            
            for field in required_fields:
                if field not in payment_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate amount
            try:
                amount = float(payment_data['amount'])
                if amount <= 0:
                    logger.error("Invalid payment amount")
                    return False
            except:
                logger.error("Invalid payment amount format")
                return False
            
            # Validate status
            valid_statuses = ['pending', 'completed', 'failed', 'refunded']
            if payment_data['status'] not in valid_statuses:
                logger.error("Invalid payment status")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating payment: {e}")
            return False
    
    async def create_invoice(self, user_id: int, plan_name: str, amount: float) -> Dict[str, Any]:
        """Create a payment invoice."""
        try:
            invoice_id = f"inv_{user_id}_{int(datetime.now().timestamp())}"
            
            invoice_data = {
                'invoice_id': invoice_id,
                'user_id': user_id,
                'amount': amount,
                'currency': self.currency,
                'description': f"Premium subscription - {plan_name}",
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            # Store invoice data (this would typically go to database)
            logger.info(f"Invoice created: {invoice_id} for user {user_id}")
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'amount': amount,
                'currency': self.currency,
                'description': invoice_data['description']
            }
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_plan_info(self, plan_name: str) -> Dict[str, Any]:
        """Get plan information."""
        plans = {
            'basic': {
                'name': 'Basic Plan',
                'price': 500,
                'duration_days': 30,
                'features': [
                    'Unlimited readings',
                    'Advanced astrology features',
                    'Priority support'
                ]
            },
            'premium': {
                'name': 'Premium Plan',
                'price': 1000,
                'duration_days': 30,
                'features': [
                    'All Basic features',
                    'VIP astrology readings',
                    'Exclusive content',
                    '24/7 support'
                ]
            },
            'vip': {
                'name': 'VIP Plan',
                'price': 2000,
                'duration_days': 30,
                'features': [
                    'All Premium features',
                    'Personal consultant',
                    'Exclusive events',
                    'Custom readings'
                ]
            }
        }
        
        return plans.get(plan_name.lower(), {})
    
    async def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans."""
        return [
            self._get_plan_info('basic'),
            self._get_plan_info('premium'),
            self._get_plan_info('vip')
        ]


# Global payment service instance
payment_service = PaymentService() 
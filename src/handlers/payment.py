"""
Payment handlers for the Fal Gram Bot.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from src.services.database import db_service
from src.services.payment_service import payment_service
from src.keyboards.payment import PaymentKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
from src.utils.helpers import format_currency

logger = get_logger("payment_handlers")

class PaymentHandlers:
    """Payment and premium subscription handlers."""
    
    @staticmethod
    async def show_premium_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show premium menu."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Get user's current premium status
        user_data = await db_service.get_user(user.id)
        is_premium = user_data.get('is_premium', False) if user_data else False
        
        if is_premium:
            # Show premium user info
            await PaymentHandlers._show_premium_user_info(query, user_data, language)
        else:
            # Show premium plans
            await PaymentHandlers._show_premium_plans(query, language)
    
    @staticmethod
    async def show_premium_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show available premium plans."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        await PaymentHandlers._show_premium_plans(query, language)
    
    @staticmethod
    async def show_plan_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show detailed plan information."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Parse plan name from callback data
        plan_name = query.data.replace("plan_details_", "")
        
        await PaymentHandlers._show_plan_details(query, plan_name, language)
    
    @staticmethod
    async def initiate_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Initiate premium plan purchase."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Parse plan name from callback data
        plan_name = query.data.replace("buy_plan_", "")
        
        await PaymentHandlers._initiate_purchase(query, plan_name, language)
    
    @staticmethod
    async def handle_pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle pre-checkout query."""
        query = update.pre_checkout_query
        await query.answer(ok=True)
        
        logger.info(f"Pre-checkout for user {query.from_user.id}: {query.invoice_payload}")
    
    @staticmethod
    async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle successful payment."""
        payment_info = update.message.successful_payment
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        try:
            # Parse plan from invoice payload
            plan_name = payment_info.invoice_payload
            
            # Process the payment
            success = await PaymentHandlers._process_payment(user.id, plan_name, payment_info)
            
            if success:
                text = i18n.get_text("payment.success", language).format(
                    plan=i18n.get_text(f"premium.plans.{plan_name}.name", language)
                )
                keyboard = PaymentKeyboards.get_main_menu_keyboard(language)
            else:
                text = i18n.get_text("payment.processing_error", language)
                keyboard = PaymentKeyboards.get_support_keyboard(language)
            
            await update.message.reply_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            text = i18n.get_text("payment.error", language)
            keyboard = PaymentKeyboards.get_support_keyboard(language)
            await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def show_subscription_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show subscription management for premium users."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        user_data = await db_service.get_user(user.id)
        if not user_data or not user_data.get('is_premium'):
            text = i18n.get_text("payment.not_premium", language)
            keyboard = PaymentKeyboards.get_premium_upgrade_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            return
        
        await PaymentHandlers._show_subscription_management(query, user_data, language)
    
    @staticmethod
    async def cancel_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle subscription cancellation request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Show confirmation
        text = i18n.get_text("payment.cancel_confirmation", language)
        keyboard = PaymentKeyboards.get_cancel_confirmation_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def confirm_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Confirm subscription cancellation."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        try:
            # Cancel subscription
            success = await payment_service.cancel_subscription(user.id)
            
            if success:
                text = i18n.get_text("payment.cancellation_success", language)
                keyboard = PaymentKeyboards.get_main_menu_keyboard(language)
            else:
                text = i18n.get_text("payment.cancellation_error", language)
                keyboard = PaymentKeyboards.get_support_keyboard(language)
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            text = i18n.get_text("payment.error", language)
            keyboard = PaymentKeyboards.get_support_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_premium_plans(query, language: str) -> None:
        """Show premium plans."""
        text = i18n.get_text("premium.plans_title", language)
        keyboard = PaymentKeyboards.get_premium_plans_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_plan_details(query, plan_name: str, language: str) -> None:
        """Show detailed plan information."""
        plan_info = PaymentHandlers._get_plan_info(plan_name)
        
        text = i18n.get_text("premium.plan_details_title", language).format(
            plan_name=i18n.get_text(f"premium.plans.{plan_name}.name", language)
        )
        
        text += f"\n\n{i18n.get_text('premium.price', language)}: {format_currency(plan_info['price'], 'TRY')}"
        text += f"\n{i18n.get_text('premium.duration', language)}: {plan_info['duration']} {i18n.get_text('premium.days', language)}"
        
        text += f"\n\n{i18n.get_text('premium.features', language)}:"
        for feature in plan_info['features']:
            text += f"\n• {feature}"
        
        keyboard = PaymentKeyboards.get_plan_details_keyboard(language, plan_name)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _initiate_purchase(query, plan_name: str, language: str) -> None:
        """Initiate purchase process."""
        plan_info = PaymentHandlers._get_plan_info(plan_name)
        
        try:
            # Create invoice
            title = i18n.get_text(f"premium.plans.{plan_name}.name", language)
            description = i18n.get_text(f"premium.plans.{plan_name}.description", language)
            
            prices = [LabeledPrice(title, int(plan_info['price'] * 100))]  # Convert to kopeks
            
            # Send invoice
            await query.bot.send_invoice(
                chat_id=query.from_user.id,
                title=title,
                description=description,
                payload=plan_name,
                provider_token=payment_service.get_provider_token(),
                currency="TRY",
                prices=prices,
                start_parameter=f"premium_{plan_name}",
                protect_content=True
            )
            
            # Update message
            text = i18n.get_text("payment.invoice_sent", language)
            keyboard = PaymentKeyboards.get_back_button(language, "premium_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            text = i18n.get_text("payment.invoice_error", language)
            keyboard = PaymentKeyboards.get_support_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _process_payment(user_id: int, plan_name: str, payment_info) -> bool:
        """Process successful payment."""
        try:
            plan_info = PaymentHandlers._get_plan_info(plan_name)
            
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=plan_info['duration'])
            
            # Update user premium status
            success = await db_service.update_user(user_id, {
                'is_premium': True,
                'premium_plan': plan_name,
                'premium_expires_at': expiry_date.isoformat(),
                'premium_purchased_at': datetime.now().isoformat()
            })
            
            if success:
                # Create payment record
                payment_data = {
                    'user_id': user_id,
                    'plan_name': plan_name,
                    'amount': payment_info.total_amount / 100,  # Convert from kopeks
                    'currency': payment_info.currency,
                    'payment_id': payment_info.telegram_payment_charge_id,
                    'status': 'completed',
                    'created_at': datetime.now().isoformat()
                }
                
                await db_service.create_payment_record(payment_data)
                
                logger.info(f"Payment processed successfully for user {user_id}, plan: {plan_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False
    
    @staticmethod
    async def _show_premium_user_info(query, user_data: Dict[str, Any], language: str) -> None:
        """Show premium user information."""
        expiry_date = user_data.get('premium_expires_at')
        plan_name = user_data.get('premium_plan', 'premium')
        
        text = i18n.get_text("premium.user_info_title", language)
        text += f"\n\n{i18n.get_text('premium.current_plan', language)}: {i18n.get_text(f'premium.plans.{plan_name}.name', language)}"
        
        if expiry_date:
            try:
                expiry = datetime.fromisoformat(expiry_date)
                text += f"\n{i18n.get_text('premium.expires_at', language)}: {expiry.strftime('%Y-%m-%d %H:%M')}"
            except:
                text += f"\n{i18n.get_text('premium.expires_at', language)}: {expiry_date}"
        
        keyboard = PaymentKeyboards.get_premium_user_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_subscription_management(query, user_data: Dict[str, Any], language: str) -> None:
        """Show subscription management options."""
        text = i18n.get_text("payment.subscription_management", language)
        keyboard = PaymentKeyboards.get_subscription_management_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    def _get_plan_info(plan_name: str) -> Dict[str, Any]:
        """Get plan information."""
        plans = {
            'basic': {
                'price': 500,
                'duration': 30,
                'features': [
                    'Unlimited fortune readings',
                    'Weekly horoscopes',
                    'Birth chart analysis',
                    'Advanced features'
                ]
            },
            'premium': {
                'price': 1000,
                'duration': 30,
                'features': [
                    'All Basic features',
                    'Monthly horoscopes',
                    'Compatibility analysis',
                    'Moon calendar',
                    'Priority support'
                ]
            },
            'vip': {
                'price': 2000,
                'duration': 30,
                'features': [
                    'All Premium features',
                    '24/7 AI chatbot',
                    'Personal consultations',
                    'Exclusive content',
                    'VIP support'
                ]
            }
        }
        
        return plans.get(plan_name, plans['premium'])

# Global handlers instance
payment_handlers = PaymentHandlers()
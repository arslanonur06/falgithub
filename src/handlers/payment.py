"""
Payment handlers for the Fal Gram Bot.
Handles payment and subscription processes.
"""

from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings
from src.utils.i18n import i18n
from src.utils.logger import logger
from src.services.database import db_service
from src.services.payment_service import payment_service
from src.keyboards.payment import PaymentKeyboards


class PaymentHandlers:
    """Payment command and callback handlers."""
    
    @staticmethod
    async def show_premium_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show premium menu."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            text = i18n.get_text("premium_menu_title", language)
            keyboard = PaymentKeyboards.get_premium_menu_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing premium menu: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_premium_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show premium plans."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            basic = i18n.get_text('premium_plan_basic', language)
            premium = i18n.get_text('premium_plan_premium', language)
            vip = i18n.get_text('premium_plan_vip', language)
            separator = i18n.get_text('premium_plans.separator', language)
            
            text = f"{i18n.get_text('premium_menu', language)}\n{separator}\n\n{basic}\n{premium}\n{vip}"
            
            keyboard = PaymentKeyboards.get_premium_plans_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing premium plans: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_plan_comparison(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show comparison of plans using Turkish i18n."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            title = i18n.get_text('plan_comparison.title', language)
            sep = i18n.get_text('plan_comparison.separator', language)
            free = i18n.get_text('plan_comparison.plans.free.title', language)
            basic = i18n.get_text('plan_comparison.plans.basic.title', language)
            premium = i18n.get_text('plan_comparison.plans.premium.title', language)
            vip = i18n.get_text('plan_comparison.plans.vip.title', language)
            
            text = f"{title}\n{sep}\n\n{free}\n{basic}\n{premium}\n{vip}"
            keyboard = PaymentKeyboards.get_payment_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error showing plan comparison: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle plan selection."""
        try:
            user = update.effective_user
            if not user:
                return
            
            callback_data = update.callback_query.data
            plan_name = callback_data.replace("plan_", "")
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            # Get plan info
            plan_info = payment_service._get_plan_info(plan_name)
            if not plan_info:
                await update.callback_query.answer(i18n.get_text("error_occurred", language))
                return
            
            # Localized plan details from tr.json
            plan_title = i18n.get_text(f"premium_plans.plans.{plan_name}.name", language)
            plan_price = i18n.get_text(f"premium_plans.plans.{plan_name}.price", language)
            plan_duration = i18n.get_text(f"premium_plans.plans.{plan_name}.duration", language)
            
            text = f"💳 **{i18n.get_text('premium.plan_details', language)}**\n\n"
            text += f"**{i18n.get_text('premium_plans.plan_details.description_label', language)}:** {plan_title}\n"
            text += f"**{i18n.get_text('premium_plans.plan_details.price_label', language)}:** {plan_price}\n"
            text += f"**{i18n.get_text('premium_plans.plan_details.duration_label', language)}:** {plan_duration}\n"
            
            keyboard = PaymentKeyboards.get_payment_confirmation_keyboard(plan_name, language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error handling plan selection: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle payment processing with Telegram Stars (simulated flow)."""
        try:
            user = update.effective_user
            if not user:
                return
            
            callback_data = update.callback_query.data
            plan_name = callback_data.replace("pay_", "")
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            # Get plan info
            plan_info = payment_service._get_plan_info(plan_name)
            if not plan_info:
                await update.callback_query.answer(i18n.get_text("error_occurred", language))
                return
            
            # Create invoice (placeholder for Telegram Stars)
            invoice_result = await payment_service.create_invoice(
                user.id, 
                plan_name, 
                plan_info['price']
            )
            
            if not invoice_result['success']:
                await update.callback_query.answer(i18n.get_text("premium.payment_error", language))
                return
            
            # Simulate payment success and activate subscription
            await update.callback_query.answer(i18n.get_text("premium.purchase_initiated", language))
            
            subscription_result = await payment_service.create_subscription(
                user.id,
                plan_name,
                plan_info['duration_days']
            )
            
            if subscription_result['success']:
                success_text = i18n.get_text("premium.payment_success", language)
                keyboard = PaymentKeyboards.get_payment_back_keyboard(language)
                await update.callback_query.edit_message_text(
                    success_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await update.callback_query.answer(i18n.get_text("premium.payment_error", language))
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_subscription_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show subscription management."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            # Check subscription status
            subscription_status = await payment_service.check_subscription_status(user.id)
            
            header = i18n.get_text("subscription_management", language)
            text = f"{header}\n\n"
            
            if subscription_status['active']:
                text += i18n.get_text("daily_card_already_subscribed", language)
            else:
                text += i18n.get_text("premium_required", language)
            
            keyboard = PaymentKeyboards.get_subscription_management_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing subscription management: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_cancel_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle subscription cancellation."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            # Check if user has active subscription
            subscription_status = await payment_service.check_subscription_status(user.id)
            
            if not subscription_status['active']:
                await update.callback_query.answer(i18n.get_text("premium_required", language))
                return
            
            # Cancel subscription
            success = await payment_service.cancel_subscription(user.id)
            
            if success:
                text = i18n.get_text("operation_successful", language)
                keyboard = PaymentKeyboards.get_payment_back_keyboard(language)
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await update.callback_query.answer(i18n.get_text("error_occurred", language))
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr')) 
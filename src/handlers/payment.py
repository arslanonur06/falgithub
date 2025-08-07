"""
Payment handlers for the Fal Gram Bot.
Handles payment and subscription processes.
"""

from telegram import Update, LabeledPrice
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
        """Show comparison of plans using Turkish i18n with features."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            def get_nested_list(path: str) -> list:
                keys = path.split('.')
                node = i18n.translations.get(language, {})
                for k in keys:
                    if isinstance(node, dict):
                        node = node.get(k)
                    else:
                        node = None
                        break
                return node if isinstance(node, list) else []
            
            title = i18n.get_text('plan_comparison.title', language)
            sep = i18n.get_text('plan_comparison.separator', language)
            
            sections = []
            for plan_key in ['free', 'basic', 'premium', 'vip']:
                plan_title = i18n.get_text(f'plan_comparison.plans.{plan_key}.title', language)
                features = get_nested_list(f'plan_comparison.plans.{plan_key}.features')
                feat_text = "\n".join(f"• {f}" for f in features) if features else ""
                sections.append(f"{plan_title}\n{feat_text}")
            
            text = f"{title}\n{sep}\n\n" + "\n\n".join(sections)
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
        """Handle payment processing with Telegram Stars by sending invoice."""
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
            
            plan_title = i18n.get_text(f"premium_plans.plans.{plan_name}.name", language)
            title = i18n.get_text("premium_menu_title", language)
            description = i18n.get_text("premium.telegram_stars_payment", language)
            prices = [LabeledPrice(label=plan_title, amount=int(plan_info['price']))]
            
            await update.callback_query.answer(i18n.get_text("premium.purchase_initiated", language))
            
            await context.bot.send_invoice(
                chat_id=user.id,
                title=title,
                description=description,
                payload=f"stars_{plan_name}",
                provider_token=None,
                currency="XTR",
                prices=prices,
            )
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle successful Stars payment and activate subscription."""
        try:
            user = update.effective_user
            if not user or not update.message or not update.message.successful_payment:
                return
            
            payload = update.message.successful_payment.invoice_payload or ""
            if not payload.startswith("stars_"):
                return
            plan_name = payload.replace("stars_", "")
            
            plan_info = payment_service._get_plan_info(plan_name)
            if not plan_info:
                return
            
            subscription_result = await payment_service.create_subscription(
                user.id,
                plan_name,
                plan_info['duration_days']
            )
            
            language = 'tr'
            user_data = await db_service.get_user(user.id)
            if user_data:
                language = user_data.get('language', 'tr')
            
            if subscription_result['success']:
                success_text = i18n.get_text("premium.payment_success", language)
                keyboard = PaymentKeyboards.get_payment_back_keyboard(language)
                await update.message.reply_text(success_text, reply_markup=keyboard, parse_mode='Markdown')
            else:
                await update.message.reply_text(i18n.get_text("premium.payment_error", language))
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
            # Avoid raising in message updates 
"""
Referral handlers for the Fal Gram Bot.
Handles referral system interactions.
"""

from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings
from src.utils.i18n import i18n
from src.utils.logger import logger
from src.services.database import db_service
from src.keyboards.referral import ReferralKeyboards


class ReferralHandlers:
    """Referral command and callback handlers."""
    
    @staticmethod
    async def show_referral_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral menu."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            title = i18n.get_text("referral_system.main_panel.title", language)
            desc = i18n.get_text("referral_system.main_panel.separator", language)
            text = f"{title}\n{desc}"
            
            keyboard = ReferralKeyboards.get_referral_menu_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral menu: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's referral information."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            language = user_data.get('language', 'tr')
            
            # Get referral stats
            referral_count = user_data.get('referral_count', 0)
            referral_earnings = user_data.get('referral_earnings', 0)
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                # Generate referral code
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            text = i18n.format_text(
                "referral_info_message",
                language,
                referred_count=referral_count,
                referral_earnings=referral_earnings,
                referral_link=referral_link
            )
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral info: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral statistics."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            language = user_data.get('language', 'tr')
            
            referral_count = user_data.get('referral_count', 0)
            referral_earnings = user_data.get('referral_earnings', 0)
            
            title = i18n.get_text("referral_system.stats_panel.title", language)
            total_label = i18n.get_text("referral_system.stats_panel.total_invites", language).format(count=referral_count)
            earnings_label = i18n.get_text("referral_system.stats_panel.total_readings", language).format(count=referral_earnings)
            
            text = f"{title}\n\n{total_label}\n{earnings_label}"
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral stats: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_referral_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral leaderboard."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            title = i18n.get_text("referral_system.main_panel.title", language)
            text = f"{title}\n\n{i18n.get_text('referral_system.rewards_panel.badges_label', language)}"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral leaderboard: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_referral_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral rewards."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            title = i18n.get_text("referral_system.rewards_panel.title", language)
            balance_label = i18n.get_text("referral_system.rewards_panel.balance_label", language)
            text = f"{title}\n\n{balance_label}"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral rewards: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_referral_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral share options."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            text = i18n.get_text("main_panel.share_label", language)
            keyboard = ReferralKeyboards.get_referral_share_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral share: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_referral_link_copy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle copy referral link."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            language = user_data.get('language', 'tr')
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            await update.callback_query.answer(
                i18n.format_text("referral.link_copied", language, link=referral_link),
                show_alert=True
            )
            context.user_data['referral_link'] = referral_link
            
        except Exception as e:
            logger.error(f"Error copying referral link: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_share_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle share on Telegram."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            referral_code = user_data.get('referral_code')
            if not referral_code:
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            share_text = i18n.get_text("main_panel.share_text", 'tr') + f"\n\n{referral_link}"
            await update.callback_query.answer(i18n.get_text("operation_successful", 'tr'))
            await context.bot.send_message(chat_id=user.id, text=share_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error sharing on Telegram: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_share_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle share on WhatsApp."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            referral_code = user_data.get('referral_code')
            if not referral_code:
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            share_text = i18n.get_text("main_panel.share_text", 'tr') + f"\n\n{referral_link}"
            whatsapp_url = f"https://wa.me/?text={share_text.replace(' ', '%20')}"
            
            await update.callback_query.answer(i18n.get_text("operation_successful", 'tr'))
            await context.bot.send_message(
                chat_id=user.id,
                text=f"📱 [WhatsApp]({whatsapp_url})",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sharing on WhatsApp: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr')) 
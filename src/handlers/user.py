"""
User handlers for the Fal Gram Bot.
Handles user commands and general interactions.
"""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import settings
from src.utils.i18n import i18n
from src.utils.logger import logger
from src.services.database import db_service
from src.keyboards.main import MainKeyboards
from datetime import datetime


class UserHandlers:
    """User command and callback handlers."""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        try:
            user = update.effective_user
            if not user:
                return
            
            # Get or create user in database
            user_data = await db_service.get_user(user.id)
            if not user_data:
                # Create new user
                new_user_data = {
                    'user_id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'language': 'tr',
                    'created_at': datetime.now().isoformat(),
                    'last_activity': datetime.now().isoformat()
                }
                await db_service.create_user(new_user_data)
                logger.info(f"New user created: {user.id}")
                user_data = new_user_data
            
            # Get user language
            language = user_data.get('language', 'tr')
            
            # Send welcome message
            welcome_text = i18n.get_text("start_message", language)
            keyboard = MainKeyboards.get_main_menu_keyboard(language)
            
            if update.message:
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=welcome_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show main menu."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            text = i18n.get_text("main_panel.title", language)
            keyboard = MainKeyboards.get_main_menu_keyboard(language)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error showing main menu: {e}")
            await update.message.reply_text(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user profile."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            language = user_data.get('language', 'tr')
            
            # Build profile text
            profile_text = i18n.get_text("profile.title", language) + "\n\n"
            profile_text += f"**{i18n.get_text('profile.name', language)}:** {user_data.get('first_name', 'N/A')}\n"
            profile_text += f"**{i18n.get_text('profile.username', language)}:** @{user_data.get('username', 'N/A')}\n"
            profile_text += f"**{i18n.get_text('profile.language', language)}:** {user_data.get('language', 'tr').upper()}\n\n"
            
            # Premium status
            is_premium = user_data.get('is_premium', False)
            premium_status = i18n.get_text("profile.premium_active", language) if is_premium else i18n.get_text("profile.premium_inactive", language)
            profile_text += f"**{i18n.get_text('profile.premium_status', language)}:** {premium_status}\n"
            
            if is_premium:
                plan_name = user_data.get('premium_plan', 'Unknown')
                profile_text += f"**Plan:** {plan_name}\n"
                
                expires_at = user_data.get('premium_expires_at')
                if expires_at:
                    profile_text += f"**{i18n.get_text('profile.premium_expires', language)}:** {expires_at[:10]}\n"
            
            # Usage stats
            total_readings = user_data.get('total_readings', 0)
            daily_readings = user_data.get('daily_readings_used', 0)
            profile_text += f"\n**{i18n.get_text('profile.usage_stats', language)}:**\n"
            profile_text += f"Total readings: {total_readings}\n"
            profile_text += f"Today's readings: {daily_readings}/{settings.FREE_DAILY_LIMIT}"
            
            keyboard = MainKeyboards.get_profile_keyboard(language)
            
            await update.callback_query.edit_message_text(
                profile_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing profile: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show language selection menu."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            text = i18n.get_text("language_selection.title", language)
            keyboard = MainKeyboards.get_language_selection_keyboard()
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing language menu: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle language change."""
        try:
            user = update.effective_user
            if not user:
                return
            
            callback_data = update.callback_query.data
            new_language = callback_data.replace("set_lang_", "")
            
            if new_language not in settings.SUPPORTED_LANGUAGES:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                return
            
            # Update user language
            success = await db_service.update_user(user.id, {
                'language': new_language
            })
            
            if success:
                lang_name = i18n.get_text("language_name", new_language)
                await update.callback_query.answer(i18n.format_text("language_change.success_default", new_language, lang_name=lang_name))
                await UserHandlers.show_main_menu(update, context)
            else:
                await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
                
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show help information."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            help_text = i18n.get_text("default_message_response", language)
            keyboard = MainKeyboards.get_help_keyboard(language)
            
            await update.callback_query.edit_message_text(
                help_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing help: {e}")
            await update.callback_query.answer(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'tr') if user_data else 'tr'
            
            # Default response for text messages
            response_text = i18n.get_text("default_message_response", language)
            keyboard = MainKeyboards.get_main_menu_keyboard(language)
            
            await update.message.reply_text(
                response_text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(i18n.get_text("error_occurred", 'tr'))
    
    @staticmethod
    async def handle_copy_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            
            # Create referral link
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
    async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle back button."""
        try:
            callback_data = update.callback_query.data
            
            if callback_data == "main_menu":
                await UserHandlers.show_main_menu(update, context)
            elif callback_data == "astrology":
                # This would be handled by astrology handler
                await update.callback_query.answer("Redirecting to astrology...")
            elif callback_data == "fortune":
                # This would be handled by fortune handler
                await update.callback_query.answer("Redirecting to fortune...")
            else:
                await update.callback_query.answer("Unknown back action")
                
        except Exception as e:
            logger.error(f"Error handling back button: {e}")
            await update.callback_query.answer("❌ An error occurred") 
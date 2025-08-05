"""
User management handlers for the Fal Gram Bot.
"""

from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional
from src.models.user import User
from src.services.database import db_service
from src.keyboards.main import MainKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
from src.utils.helpers import generate_referral_code

logger = get_logger("user_handlers")

class UserHandlers:
    """User management handlers."""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        if not user:
            return
        
        # Set user language
        language = user.language_code or "en"
        if language not in i18n.supported_languages:
            language = "en"
        
        # Check if user exists in database
        user_data = await db_service.get_user(user.id)
        
        if not user_data:
            # Create new user
            new_user = User(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=language,
                referral_code=generate_referral_code(user.id)
            )
            
            # Check for referral code in context
            if context.args and len(context.args) > 0:
                referral_code = context.args[0]
                # TODO: Validate referral code and set referred_by
            
            # Save to database
            await db_service.create_user(new_user.to_dict())
            logger.info(f"New user created: {user.id}")
        
        # Send welcome message
        welcome_text = i18n.get_text("welcome.message", language)
        if user_data and user_data.get('is_premium'):
            welcome_text += f"\n\n{i18n.get_text('welcome.premium_user', language)}"
        
        keyboard = MainKeyboards.get_main_menu(language)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        help_text = i18n.get_text("help.message", language)
        
        keyboard = MainKeyboards.get_back_button(language, "main_menu")
        
        await update.message.reply_text(
            help_text,
            reply_markup=keyboard
        )
    
    @staticmethod
    async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /profile command."""
        user = update.effective_user
        if not user:
            return
        
        language = user.language_code or "en"
        
        # Get user data from database
        user_data = await db_service.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text(
                i18n.get_text("error.user_not_found", language)
            )
            return
        
        # Format profile message
        profile_text = i18n.get_text("profile.info", language).format(
            name=user_data.get('first_name', 'Unknown'),
            username=f"@{user_data.get('username')}" if user_data.get('username') else "Not set",
            language=i18n.get_language_name(user_data.get('language_code', 'en')),
            premium_status=i18n.get_text("profile.premium" if user_data.get('is_premium') else "profile.free", language),
            total_usage=user_data.get('total_usage_count', 0),
            referral_code=user_data.get('referral_code', 'N/A')
        )
        
        keyboard = MainKeyboards.get_profile_menu(language)
        
        await update.message.reply_text(
            profile_text,
            reply_markup=keyboard
        )
    
    @staticmethod
    async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /language command."""
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        keyboard = MainKeyboards.get_language_selection()
        
        await update.message.reply_text(
            i18n.get_text("profile.select_language", language),
            reply_markup=keyboard
        )
    
    @staticmethod
    async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        if not query.data:
            return
        
        # Handle different callback data
        if query.data == "main_menu":
            keyboard = MainKeyboards.get_main_menu(language)
            await query.edit_message_text(
                i18n.get_text("menu.welcome", language),
                reply_markup=keyboard
            )
        
        elif query.data == "profile_menu":
            keyboard = MainKeyboards.get_profile_menu(language)
            await query.edit_message_text(
                i18n.get_text("profile.menu", language),
                reply_markup=keyboard
            )
        
        elif query.data == "change_language":
            keyboard = MainKeyboards.get_language_selection()
            await query.edit_message_text(
                i18n.get_text("profile.select_language", language),
                reply_markup=keyboard
            )
        
        elif query.data.startswith("set_language_"):
            new_language = query.data.replace("set_language_", "")
            
            if new_language in i18n.supported_languages:
                # Update user language in database
                await db_service.update_user(user.id, {"language_code": new_language})
                
                # Update i18n language
                i18n.set_language(new_language)
                
                await query.edit_message_text(
                    i18n.get_text("profile.language_changed", new_language),
                    reply_markup=MainKeyboards.get_back_button(new_language, "profile_menu")
                )
        
        elif query.data == "usage_stats":
            # Get usage statistics
            usage_stats = await db_service.get_user_usage_stats(user.id)
            
            stats_text = i18n.get_text("profile.usage_stats_text", language).format(
                daily_usage=usage_stats.get('daily_count', 0),
                total_usage=usage_stats.get('total_count', 0),
                last_used=usage_stats.get('last_used', 'Never')
            )
            
            await query.edit_message_text(
                stats_text,
                reply_markup=MainKeyboards.get_back_button(language, "profile_menu")
            )
        
        elif query.data == "cancel":
            await query.edit_message_text(
                i18n.get_text("common.cancelled", language)
            )
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user
        try:
            user = update.effective_user
            language = user.language_code or "en" if user else "en"
            
            await update.message.reply_text(
                i18n.get_text("error.general", language)
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

# Global handlers instance
user_handlers = UserHandlers()
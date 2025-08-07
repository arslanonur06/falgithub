"""
Admin handlers for the Fal Gram Bot.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.database import db_service
from src.keyboards.admin import AdminKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
from src.utils.helpers import format_currency, format_date
from config.settings import settings

logger = get_logger("admin_handlers")

class AdminHandlers:
    """Admin command and callback handlers."""
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /admin command."""
        user = update.effective_user
        
        # Check if user is admin
        if not AdminHandlers._is_admin(user.id):
            await update.message.reply_text(i18n.get_text("admin_unauthorized", 'tr'))
            return
        
        language = 'tr'
        keyboard = AdminKeyboards.get_admin_menu_keyboard(language)
        text = i18n.get_text("admin_panel.title", language)
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /gift command for giving premium subscriptions."""
        user = update.effective_user
        
        if not AdminHandlers._is_admin(user.id):
            await update.message.reply_text(i18n.get_text("admin_unauthorized", 'tr'))
            return
        
        args = context.args
        if len(args) != 3:
            await update.message.reply_text(i18n.get_text("admin_gift.example", 'tr'))
            return
        
        try:
            target_user_id = int(args[0])
            plan_name = args[1]
            days = int(args[2])
            
            success = await AdminHandlers._gift_premium(target_user_id, plan_name, days)
            
            if success:
                await update.message.reply_text(i18n.get_text("operation_successful", 'tr'))
            else:
                await update.message.reply_text(i18n.get_text("error_occurred", 'tr'))
                
        except ValueError:
            await update.message.reply_text(i18n.get_text("admin_invalid_format", 'tr'))
    
    @staticmethod
    async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cancel command for cancelling premium subscriptions."""
        user = update.effective_user
        
        if not AdminHandlers._is_admin(user.id):
            await update.message.reply_text(i18n.get_text("admin_unauthorized", 'tr'))
            return
        
        args = context.args
        if len(args) != 1:
            await update.message.reply_text(i18n.get_text("admin_cancel.command", 'tr'))
            return
        
        try:
            target_user_id = int(args[0])
            success = await AdminHandlers._cancel_premium(target_user_id)
            if success:
                await update.message.reply_text(i18n.get_text("operation_successful", 'tr'))
            else:
                await update.message.reply_text(i18n.get_text("error_occurred", 'tr'))
        except ValueError:
            await update.message.reply_text(i18n.get_text("admin_invalid_format", 'tr'))
    
    @staticmethod
    async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle admin callback queries."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if not AdminHandlers._is_admin(user.id):
            await query.edit_message_text(i18n.get_text("admin_unauthorized", 'tr'))
            return
        
        language = 'tr'
        
        if query.data == "admin_stats":
            await AdminHandlers._show_admin_stats(query, language)
        elif query.data == "admin_users":
            await AdminHandlers._show_admin_users(query, language)
        elif query.data == "admin_premium":
            await AdminHandlers._show_admin_premium(query, language)
        elif query.data == "admin_logs":
            await AdminHandlers._show_admin_logs(query, language)
        elif query.data == "admin_settings":
            await AdminHandlers._show_admin_settings(query, language)
        elif query.data == "admin_download_pdf":
            await AdminHandlers._download_admin_pdf(query, language)
        elif query.data == "back_to_admin":
            await AdminHandlers._show_admin_main_menu(query, language)
    
    @staticmethod
    def _is_admin(user_id: int) -> bool:
        """Check if user is admin."""
        admin_id = getattr(settings, 'ADMIN_ID', None)
        return admin_id and str(user_id) == str(admin_id)
    
    @staticmethod
    async def _gift_premium(user_id: int, plan_name: str, days: int) -> bool:
        """Gift premium subscription to user."""
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            success = await db_service.update_user(user_id, {
                'is_premium': True,
                'premium_plan': plan_name,
                'premium_expires_at': expiry_date.isoformat(),
                'premium_gifted_at': datetime.now().isoformat()
            })
            if success:
                await db_service.add_log(f"Admin gifted {plan_name} plan to user {user_id} for {days} days")
                logger.info(f"Admin gifted {plan_name} plan to user {user_id} for {days} days")
                return True
            return False
        except Exception as e:
            logger.error(f"Error gifting premium: {e}")
            return False
    
    @staticmethod
    async def _cancel_premium(user_id: int) -> bool:
        """Cancel premium subscription for user."""
        try:
            success = await db_service.update_user(user_id, {
                'is_premium': False,
                'premium_plan': None,
                'premium_expires_at': None,
                'premium_cancelled_at': datetime.now().isoformat()
            })
            if success:
                await db_service.add_log(f"Admin cancelled premium for user {user_id}")
                logger.info(f"Admin cancelled premium for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling premium: {e}")
            return False
    
    @staticmethod
    async def _show_admin_stats(query, language: str) -> None:
        """Show admin statistics."""
        try:
            stats = await AdminHandlers._get_admin_stats()
            title = i18n.get_text("admin_stats.title", language)
            text = title
            text += f"\n\n{i18n.get_text('admin_stats.user_stats', language)}"
            text += f"\n{i18n.format_text('admin_stats.total_users', language, count=stats['total_users'])}"
            text += f"\n{i18n.format_text('admin_stats.daily_subscribers', language, count=stats['active_users'])}"
            text += f"\n{i18n.get_text('admin_stats.referral_stats', language)}"
            text += f"\n{i18n.format_text('admin_stats.total_referrers', language, count=0)}"
            text += f"\n{i18n.format_text('admin_stats.total_referred', language, count=0)}"
            text += f"\n{i18n.format_text('admin_stats.total_earnings', language, count=0)}"
            text += f"\n{i18n.format_text('admin_stats.referral_rate', language, rate=0.0)}"
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing admin stats: {e}")
            text = i18n.get_text("error_occurred", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_users(query, language: str) -> None:
        """Show admin users management."""
        try:
            users = await db_service.get_all_users()
            recent_users = users[:10] if users else []
            title = i18n.get_text("admin_users.title", language)
            text = title + "\n\n"
            if recent_users:
                for user in recent_users:
                    user_name = user.get('first_name', 'Unknown')
                    user_id = user.get('user_id', 'N/A')
                    is_premium = "✅" if user.get('is_premium') else "❌"
                    text += f"• {user_name} (ID: {user_id}) {is_premium}\n"
            else:
                text += i18n.get_text("admin_users.no_users", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing admin users: {e}")
            text = i18n.get_text("error_occurred", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_premium(query, language: str) -> None:
        """Show admin premium management."""
        text = i18n.get_text("admin_premium.title", language)
        keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_logs(query, language: str) -> None:
        """Show admin logs."""
        try:
            logs = await db_service.get_logs(limit=20)
            title = i18n.get_text("admin_logs.title", language)
            text = title + "\n\n"
            if logs:
                for log in logs:
                    timestamp = log.get('created_at', 'Unknown')
                    message = log.get('message', 'No message')
                    text += f"• {timestamp}: {message}\n"
            else:
                text += i18n.get_text("admin_logs.no_logs", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing admin logs: {e}")
            text = i18n.get_text("error_occurred", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_settings(query, language: str) -> None:
        """Show admin settings."""
        text = i18n.get_text("admin_settings.title", language)
        keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _download_admin_pdf(query, language: str) -> None:
        """Download admin PDF report."""
        try:
            # Placeholder PDF generation
            await query.bot.send_message(chat_id=query.from_user.id, text=i18n.get_text("admin_report", language))
            text = i18n.get_text("admin_report", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error generating admin PDF: {e}")
            text = i18n.get_text("error_occurred", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_main_menu(query, language: str) -> None:
        """Show admin main menu."""
        text = i18n.get_text("admin_panel.title", language)
        keyboard = AdminKeyboards.get_admin_menu_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _get_admin_stats() -> Dict[str, Any]:
        """Get admin statistics."""
        try:
            all_users = await db_service.get_all_users()
            premium_users = []
            total_users = len(all_users) if all_users else 0
            active_users = 0
            today = datetime.now().date()
            if all_users:
                for user in all_users:
                    last_activity = user.get('last_activity')
                    if last_activity:
                        try:
                            activity_date = datetime.fromisoformat(last_activity).date()
                            if activity_date == today:
                                active_users += 1
                        except:
                            pass
            return {
                'total_users': total_users,
                'active_users': active_users
            }
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return {
                'total_users': 0,
                'active_users': 0
            }

# Global handlers instance
admin_handlers = AdminHandlers()
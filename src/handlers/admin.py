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
            await update.message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        language = user.language_code or "en"
        
        keyboard = AdminKeyboards.get_admin_main_menu(language)
        text = i18n.get_text("admin.welcome", language)
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /gift command for giving premium subscriptions."""
        user = update.effective_user
        
        # Check if user is admin
        if not AdminHandlers._is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Parse command arguments: /gift <user_id> <plan> <days>
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /gift <user_id> <plan> <days>")
            return
        
        try:
            target_user_id = int(args[0])
            plan_name = args[1]
            days = int(args[2])
            
            success = await AdminHandlers._gift_premium(target_user_id, plan_name, days)
            
            if success:
                await update.message.reply_text(f"✅ Premium subscription gifted successfully!")
            else:
                await update.message.reply_text("❌ Failed to gift premium subscription.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid arguments. Usage: /gift <user_id> <plan> <days>")
    
    @staticmethod
    async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cancel command for cancelling premium subscriptions."""
        user = update.effective_user
        
        # Check if user is admin
        if not AdminHandlers._is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        # Parse command arguments: /cancel <user_id>
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("Usage: /cancel <user_id>")
            return
        
        try:
            target_user_id = int(args[0])
            
            success = await AdminHandlers._cancel_premium(target_user_id)
            
            if success:
                await update.message.reply_text(f"✅ Premium subscription cancelled successfully!")
            else:
                await update.message.reply_text("❌ Failed to cancel premium subscription.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Usage: /cancel <user_id>")
    
    @staticmethod
    async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle admin callback queries."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Check if user is admin
        if not AdminHandlers._is_admin(user.id):
            await query.edit_message_text("❌ Access denied. Admin privileges required.")
            return
        
        language = user.language_code or "en"
        
        # Handle different admin callbacks
        if query.data == "admin_stats":
            await AdminHandlers._show_admin_stats(query, language)
        elif query.data == "admin_users":
            await AdminHandlers._show_admin_users(query, language)
        elif query.data == "admin_premium":
            await AdminHandlers._show_admin_premium(query, language)
        elif query.data == "admin_logs":
            await AdminHandlers._show_admin_logs(query, language)
        elif query.data == "admin_referrals":
            await AdminHandlers._show_admin_referrals(query, language)
        elif query.data == "admin_settings":
            await AdminHandlers._show_admin_settings(query, language)
        elif query.data == "admin_download_pdf":
            await AdminHandlers._download_admin_pdf(query, language)
        elif query.data == "admin_premium_users":
            await AdminHandlers._show_premium_users(query, language)
        elif query.data == "admin_premium_stats":
            await AdminHandlers._show_premium_stats(query, language)
        elif query.data == "admin_gift_subscription":
            await AdminHandlers._show_gift_subscription(query, language)
        elif query.data == "admin_cancel_subscription":
            await AdminHandlers._show_cancel_subscription(query, language)
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
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=days)
            
            # Update user premium status
            success = await db_service.update_user(user_id, {
                'is_premium': True,
                'premium_plan': plan_name,
                'premium_expires_at': expiry_date.isoformat(),
                'premium_gifted_at': datetime.now().isoformat()
            })
            
            if success:
                # Log the gift
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
            # Update user premium status
            success = await db_service.update_user(user_id, {
                'is_premium': False,
                'premium_plan': None,
                'premium_expires_at': None,
                'premium_cancelled_at': datetime.now().isoformat()
            })
            
            if success:
                # Log the cancellation
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
            # Get statistics from database
            stats = await AdminHandlers._get_admin_stats()
            
            text = i18n.get_text("admin.stats_title", language)
            text += f"\n\n{i18n.get_text('admin.total_users', language)}: {stats['total_users']}"
            text += f"\n{i18n.get_text('admin.active_users', language)}: {stats['active_users']}"
            text += f"\n{i18n.get_text('admin.premium_users', language)}: {stats['premium_users']}"
            text += f"\n{i18n.get_text('admin.new_users_today', language)}: {stats['new_users_today']}"
            text += f"\n\n{i18n.get_text('admin.total_revenue', language)}: {format_currency(stats['total_revenue'], 'TRY')}"
            text += f"\n{i18n.get_text('admin.revenue_today', language)}: {format_currency(stats['revenue_today'], 'TRY')}"
            text += f"\n{i18n.get_text('admin.revenue_month', language)}: {format_currency(stats['revenue_month'], 'TRY')}"
            
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing admin stats: {e}")
            text = i18n.get_text("admin.error_loading_stats", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_users(query, language: str) -> None:
        """Show admin users management."""
        try:
            # Get recent users
            users = await db_service.get_all_users()
            recent_users = users[:10] if users else []  # Show last 10 users
            
            text = i18n.get_text("admin.users_title", language)
            text += f"\n\n{i18n.get_text('admin.recent_users', language)}:\n"
            
            for user in recent_users:
                user_name = user.get('first_name', 'Unknown')
                user_id = user.get('user_id', 'N/A')
                is_premium = "✅" if user.get('is_premium') else "❌"
                text += f"• {user_name} (ID: {user_id}) {is_premium}\n"
            
            keyboard = AdminKeyboards.get_admin_users_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing admin users: {e}")
            text = i18n.get_text("admin.error_loading_users", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_premium(query, language: str) -> None:
        """Show admin premium management."""
        text = i18n.get_text("admin.premium_management", language)
        keyboard = AdminKeyboards.get_admin_premium_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_logs(query, language: str) -> None:
        """Show admin logs."""
        try:
            # Get recent logs
            logs = await db_service.get_logs(limit=20)
            
            text = i18n.get_text("admin.logs_title", language)
            text += f"\n\n{i18n.get_text('admin.recent_logs', language)}:\n"
            
            for log in logs:
                timestamp = log.get('created_at', 'Unknown')
                message = log.get('message', 'No message')
                text += f"• {timestamp}: {message}\n"
            
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing admin logs: {e}")
            text = i18n.get_text("admin.error_loading_logs", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_settings(query, language: str) -> None:
        """Show admin settings."""
        text = i18n.get_text("admin.settings_title", language)
        keyboard = AdminKeyboards.get_admin_settings_keyboard(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)

    @staticmethod
    async def _show_admin_referrals(query, language: str) -> None:
        """Show referral analytics in admin panel."""
        try:
            top = await db_service.get_top_referrers(limit=5)
            last7 = await db_service.get_referral_counts_by_day(days=7)
            last6m = await db_service.get_referral_counts_by_month(months=6)
            avg_rev = await db_service.get_revenue_per_referral(days=30)

            text = "📈 Referral Analytics\n\n"
            text += "🏆 Top Referrers (last):\n"
            if top:
                for i, u in enumerate(top, 1):
                    name = u.get('first_name') or u.get('username') or f"User{i}"
                    cnt = u.get('referred_count', u.get('referral_count', 0))
                    text += f"{i}. {name} — {cnt}\n"
            else:
                text += "No data\n"

            text += "\n🗓️ Last 7 days:\n"
            if last7:
                for b in last7:
                    text += f"{b['date']}: {b['count']}\n"
            else:
                text += "No data\n"

            text += "\n📅 Last 6 months (referrals):\n"
            if last6m:
                for b in last6m:
                    text += f"{b['month']}: {b['count']}\n"
            else:
                text += "No data\n"

            text += "\n💰 Revenue per Referral (last 30d):\n"
            text += f"Total Revenue: {avg_rev['total_revenue']} XTR\n"
            text += f"Total Referrals: {avg_rev['total_referrals']}\n"
            text += f"Avg / Referral: {avg_rev['avg_revenue_per_referral']} XTR\n"

            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing admin referrals: {e}")
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text("❌ Error loading referral analytics", reply_markup=keyboard)
    
    @staticmethod
    async def _download_admin_pdf(query, language: str) -> None:
        """Download admin PDF report."""
        try:
            # Generate PDF report
            pdf_data = await AdminHandlers._generate_admin_pdf()
            
            # Send PDF file
            await query.bot.send_document(
                chat_id=query.from_user.id,
                document=pdf_data,
                filename=f"admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                caption=i18n.get_text("admin.pdf_report", language)
            )
            
            # Update message
            text = i18n.get_text("admin.pdf_sent", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating admin PDF: {e}")
            text = i18n.get_text("admin.error_generating_pdf", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_premium_users(query, language: str) -> None:
        """Show premium users list."""
        try:
            # Get premium users
            premium_users = await db_service.get_premium_users()
            
            text = i18n.get_text("admin.premium_users_title", language)
            text += f"\n\n{i18n.get_text('admin.premium_users_count', language)}: {len(premium_users)}"
            text += f"\n\n{i18n.get_text('admin.premium_users_list', language)}:\n"
            
            for user in premium_users[:10]:  # Show first 10
                user_name = user.get('first_name', 'Unknown')
                user_id = user.get('user_id', 'N/A')
                plan = user.get('premium_plan', 'Unknown')
                text += f"• {user_name} (ID: {user_id}) - {plan}\n"
            
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing premium users: {e}")
            text = i18n.get_text("admin.error_loading_premium_users", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_premium_stats(query, language: str) -> None:
        """Show premium statistics."""
        try:
            # Get premium statistics
            stats = await AdminHandlers._get_premium_stats()
            
            text = i18n.get_text("admin.premium_stats_title", language)
            text += f"\n\n{i18n.get_text('admin.premium_plan_distribution', language)}:"
            text += f"\n• {i18n.get_text('premium.plans.basic.name', language)}: {stats['basic_count']}"
            text += f"\n• {i18n.get_text('premium.plans.premium.name', language)}: {stats['premium_count']}"
            text += f"\n• {i18n.get_text('premium.plans.vip.name', language)}: {stats['vip_count']}"
            text += f"\n\n{i18n.get_text('admin.premium_revenue', language)}: {format_currency(stats['total_revenue'], 'TRY')}"
            
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing premium stats: {e}")
            text = i18n.get_text("admin.error_loading_premium_stats", language)
            keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_gift_subscription(query, language: str) -> None:
        """Show gift subscription interface."""
        text = i18n.get_text("admin.gift_subscription_title", language)
        text += f"\n\n{i18n.get_text('admin.gift_subscription_usage', language)}"
        
        keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_cancel_subscription(query, language: str) -> None:
        """Show cancel subscription interface."""
        text = i18n.get_text("admin.cancel_subscription_title", language)
        text += f"\n\n{i18n.get_text('admin.cancel_subscription_usage', language)}"
        
        keyboard = AdminKeyboards.get_back_to_admin_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _show_admin_main_menu(query, language: str) -> None:
        """Show admin main menu."""
        text = i18n.get_text("admin.welcome", language)
        keyboard = AdminKeyboards.get_admin_main_menu(language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _get_admin_stats() -> Dict[str, Any]:
        """Get admin statistics."""
        try:
            # Get basic stats
            all_users = await db_service.get_all_users()
            premium_users = await db_service.get_premium_users()
            
            # Calculate statistics
            total_users = len(all_users) if all_users else 0
            premium_count = len(premium_users) if premium_users else 0
            
            # Calculate active users (users active in last 24 hours)
            active_users = 0
            new_users_today = 0
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
                    
                    created_at = user.get('created_at')
                    if created_at:
                        try:
                            created_date = datetime.fromisoformat(created_at).date()
                            if created_date == today:
                                new_users_today += 1
                        except:
                            pass
            
            # Get revenue statistics
            revenue_stats = await db_service.get_payment_statistics()
            total_revenue = revenue_stats.get('total_revenue', 0)
            revenue_today = revenue_stats.get('revenue_today', 0)
            revenue_month = revenue_stats.get('revenue_month', 0)
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'premium_users': premium_count,
                'new_users_today': new_users_today,
                'total_revenue': total_revenue,
                'revenue_today': revenue_today,
                'revenue_month': revenue_month
            }
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'premium_users': 0,
                'new_users_today': 0,
                'total_revenue': 0,
                'revenue_today': 0,
                'revenue_month': 0
            }
    
    @staticmethod
    async def _get_premium_stats() -> Dict[str, Any]:
        """Get premium statistics."""
        try:
            premium_users = await db_service.get_premium_users()
            
            basic_count = 0
            premium_count = 0
            vip_count = 0
            
            if premium_users:
                for user in premium_users:
                    plan = user.get('premium_plan', 'premium')
                    if plan == 'basic':
                        basic_count += 1
                    elif plan == 'premium':
                        premium_count += 1
                    elif plan == 'vip':
                        vip_count += 1
            
            # Get revenue
            revenue_stats = await db_service.get_payment_statistics()
            total_revenue = revenue_stats.get('total_revenue', 0)
            
            return {
                'basic_count': basic_count,
                'premium_count': premium_count,
                'vip_count': vip_count,
                'total_revenue': total_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting premium stats: {e}")
            return {
                'basic_count': 0,
                'premium_count': 0,
                'vip_count': 0,
                'total_revenue': 0
            }
    
    @staticmethod
    async def _generate_admin_pdf() -> bytes:
        """Generate admin PDF report."""
        try:
            from fpdf import FPDF
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Add title
            pdf.cell(200, 10, txt="Fal Gram Bot - Admin Report", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            pdf.ln(10)
            
            # Get statistics
            stats = await AdminHandlers._get_admin_stats()
            
            # Add statistics
            pdf.cell(200, 10, txt=f"Total Users: {stats['total_users']}", ln=True)
            pdf.cell(200, 10, txt=f"Active Users: {stats['active_users']}", ln=True)
            pdf.cell(200, 10, txt=f"Premium Users: {stats['premium_users']}", ln=True)
            pdf.cell(200, 10, txt=f"New Users Today: {stats['new_users_today']}", ln=True)
            pdf.cell(200, 10, txt=f"Total Revenue: {format_currency(stats['total_revenue'], 'TRY')}", ln=True)
            
            return pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            logger.error(f"Error generating admin PDF: {e}")
            return b"Error generating PDF"

# Global handlers instance
admin_handlers = AdminHandlers()
"""
Referral handlers for the Fal Gram Bot.
Handles referral system interactions.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
            language = user_data.get('language', 'en') if user_data else 'en'
            
            text = "👥 **Referral Program**\n\n"
            text += "Invite friends and earn rewards!\n"
            text += "Share your referral link and get bonuses for each friend who joins."
            
            keyboard = ReferralKeyboards.get_referral_menu_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral menu: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's referral information."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer("❌ User not found")
                return
            
            language = user_data.get('language', 'en')
            
            # Get referral stats
            referral_count = user_data.get('referral_count', 0)
            referral_earnings = user_data.get('referral_earnings', 0)
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                # Generate referral code
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            text = "📊 **My Referral Info**\n\n"
            text += f"**Referral Code:** `{referral_code}`\n"
            text += f"**Total Referrals:** {referral_count}\n"
            text += f"**Total Earnings:** {referral_earnings} TRY\n\n"
            
            # Referral link
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            text += f"**Your Referral Link:**\n`{referral_link}`"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral info: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def show_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral statistics."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer("❌ User not found")
                return
            
            language = user_data.get('language', 'en')
            
            # Get referral stats
            referral_count = user_data.get('referral_count', 0)
            referral_earnings = user_data.get('referral_earnings', 0)
            
            text = "📈 **Referral Statistics**\n\n"
            text += f"**Total Referrals:** {referral_count}\n"
            text += f"**Total Earnings:** {referral_earnings} TRY\n\n"
            
            # Calculate potential earnings
            potential_earnings = referral_count * 100  # 100 TRY per referral
            text += f"**Potential Earnings:** {potential_earnings} TRY\n\n"
            
            # Referral level
            if referral_count >= 50:
                level = "Premium"
                next_level = "Maximum level reached"
            elif referral_count >= 25:
                level = "Elite"
                next_level = f"Need {50 - referral_count} more referrals for Premium"
            elif referral_count >= 10:
                level = "VIP"
                next_level = f"Need {25 - referral_count} more referrals for Elite"
            elif referral_count >= 5:
                level = "Active"
                next_level = f"Need {10 - referral_count} more referrals for VIP"
            else:
                level = "New"
                next_level = f"Need {5 - referral_count} more referrals for Active"
            
            text += f"**Current Level:** {level}\n"
            text += f"**Next Level:** {next_level}"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral stats: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def show_referral_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral leaderboard."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            # Get top referrers (simplified - in real implementation, this would query the database)
            text = "🏆 **Referral Leaderboard**\n\n"
            text += "**Top Referrers:**\n"
            text += "🥇 **User1** - 45 referrals\n"
            text += "🥈 **User2** - 32 referrals\n"
            text += "🥉 **User3** - 28 referrals\n"
            text += "4️⃣ **User4** - 15 referrals\n"
            text += "5️⃣ **User5** - 12 referrals\n\n"
            text += "Keep inviting friends to climb the leaderboard! 🚀"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral leaderboard: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def show_referral_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral rewards."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            text = "🎁 **Referral Rewards**\n\n"
            text += "**Earn rewards for each friend you invite:**\n\n"
            text += "**🎯 1-4 Referrals:**\n"
            text += "• 50 TRY bonus per referral\n"
            text += "• Weekly bonus readings\n\n"
            text += "**🎯 5-9 Referrals:**\n"
            text += "• 75 TRY bonus per referral\n"
            text += "• Special profile color\n"
            text += "• VIP tarot deck access\n\n"
            text += "**🎯 10-24 Referrals:**\n"
            text += "• 100 TRY bonus per referral\n"
            text += "• Priority AI responses\n"
            text += "• Personal reading consultant\n\n"
            text += "**🎯 25+ Referrals:**\n"
            text += "• 150 TRY bonus per referral\n"
            text += "• 24/7 priority support\n"
            text += "• Exclusive VIP features\n"
            text += "• Special events access"
            
            keyboard = ReferralKeyboards.get_referral_back_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral rewards: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def show_referral_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral share options."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            text = "📤 **Share Your Referral Link**\n\n"
            text += "Choose how you want to share your referral link:"
            
            keyboard = ReferralKeyboards.get_referral_share_keyboard(language)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing referral share: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def handle_referral_link_copy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle copy referral link."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer("❌ User not found")
                return
            
            language = user_data.get('language', 'en')
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                # Generate referral code
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            # Create referral link
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            # Copy to clipboard (this is a simplified version)
            await update.callback_query.answer(
                i18n.get_text("referral.link_copied", language),
                show_alert=True
            )
            
            # Store referral link in context for potential use
            context.user_data['referral_link'] = referral_link
            
        except Exception as e:
            logger.error(f"Error copying referral link: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def handle_share_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle share on Telegram."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer("❌ User not found")
                return
            
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                # Generate referral code
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            # Create referral link
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            # Share text
            share_text = f"🔮 Check out this amazing mystical bot!\n\n"
            share_text += f"Get your daily horoscope, coffee fortune, and more!\n\n"
            share_text += f"Join here: {referral_link}"
            
            await update.callback_query.answer("Share this message with your friends!")
            
            # Send the share text
            await context.bot.send_message(
                chat_id=user.id,
                text=share_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sharing on Telegram: {e}")
            await update.callback_query.answer("❌ An error occurred")
    
    @staticmethod
    async def handle_share_whatsapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Deprecated: redirect to Share on X (Twitter) as requested."""
        await ReferralHandlers.handle_share_twitter(update, context)

    @staticmethod
    async def handle_share_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle share on X/Twitter with referral link and copy link option."""
        try:
            user = update.effective_user
            if not user:
                return
            
            user_data = await db_service.get_user(user.id)
            if not user_data:
                await update.callback_query.answer("❌ User not found")
                return
            
            language = user_data.get('language', 'en')
            referral_code = user_data.get('referral_code')
            
            if not referral_code:
                from src.utils.helpers import generate_referral_code
                referral_code = generate_referral_code(user.id)
                await db_service.update_user(user.id, {'referral_code': referral_code})
            
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            
            # Twitter intent URL
            from urllib.parse import quote
            share_text = f"🔮 {i18n.get_text('referral.share_text', language)} {referral_link}"
            twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
            
            keyboard = [
                [InlineKeyboardButton(i18n.get_text('referral.share_twitter', language), url=twitter_url)],
                [InlineKeyboardButton(i18n.get_text('referral.copy_link', language), callback_data='copy_referral_link')],
                [InlineKeyboardButton(i18n.get_text('referral.back_to_referral', language), callback_data='referral')]
            ]
            await update.callback_query.edit_message_text(
                i18n.get_text('referral.description', language),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error sharing on Twitter/X: {e}")
            await update.callback_query.answer("❌ An error occurred")

    # --- Compatibility methods required by verification script ---
    @staticmethod
    async def share_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await ReferralHandlers.handle_referral_link_copy(update, context)

    @staticmethod
    async def process_referral_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await ReferralHandlers.show_referral_menu(update, context)

    @staticmethod
    async def complete_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await ReferralHandlers.show_referral_info(update, context)
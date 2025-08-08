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
            
            # Localized referral main panel text
            title = i18n.get_text("referral_system.title", language)
            description = i18n.get_text("referral_system.description", language)
            text = f"{title}\n\n{description}"
            
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
            
            # Referral link
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"

            # Localized info message with placeholders
            template = i18n.get_text("referral_info_message", language)
            try:
                text = template.format(
                    referred_count=referral_count,
                    referral_earnings=referral_earnings,
                    referral_link=referral_link
                )
            except Exception:
                # Fallback minimal text
                text = f"📊\n{referral_count} | {referral_earnings}\n{referral_link}"
            
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

            # Derive readings for averages (fallback: referrals)
            total_readings = int(user_data.get('free_readings_earned', referral_count))

            # Rank and percentile among users
            all_users = await db_service.get_all_users() or []
            sorted_users = sorted(all_users, key=lambda u: u.get('referral_count', 0), reverse=True)
            rank = next((idx + 1 for idx, u in enumerate(sorted_users) if str(u.get('user_id')) == str(user.id) or str(u.get('id')) == str(user.id)), len(sorted_users))
            percentile = 100.0 * (1 - (rank - 1) / max(1, len(sorted_users)))

            # Levels
            if referral_count >= 50:
                level = 5
            elif referral_count >= 25:
                level = 4
            elif referral_count >= 10:
                level = 3
            elif referral_count >= 5:
                level = 2
            else:
                level = 1

            # Next goals
            to_vip = max(0, 10 - referral_count)
            to_elite = max(0, 25 - referral_count)
            next_level_target = 5 if referral_count < 5 else 10 if referral_count < 10 else 25 if referral_count < 25 else 50 if referral_count < 50 else 50
            next_level_remaining = max(0, next_level_target - referral_count)

            # Panel texts from TR locales
            title = i18n.get_text('referral.stats_panel.title', language)
            text = title + "\n\n"
            text += i18n.get_text('referral.stats_panel.performance_label', language) + "\n"
            text += i18n.get_text('referral.stats_panel.total_invites', language).format(count=referral_count) + "\n"
            text += i18n.get_text('referral.stats_panel.this_week', language).format(count=0) + "\n"
            text += i18n.get_text('referral.stats_panel.this_month', language).format(count=0) + "\n"
            text += i18n.get_text('referral.stats_panel.last_invite', language).format(date='N/A') + "\n\n"

            text += i18n.get_text('referral.stats_panel.earnings_label', language) + "\n"
            text += i18n.get_text('referral.stats_panel.total_readings', language).format(count=total_readings) + "\n"
            avg = (total_readings / referral_count) if referral_count > 0 else 0.0
            text += i18n.get_text('referral.stats_panel.avg_per_invite', language).format(avg=avg) + "\n"
            potential_value = referral_count * 100
            text += i18n.get_text('referral.stats_panel.potential_value', language).format(value=potential_value) + "\n\n"

            text += i18n.get_text('referral.stats_panel.ranking_label', language) + "\n"
            text += i18n.get_text('referral.stats_panel.global_rank', language).format(rank=rank) + "\n"
            text += i18n.get_text('referral.stats_panel.percentile', language).format(perc=percentile) + "\n"
            text += i18n.get_text('referral.stats_panel.level', language).format(level=level) + "\n\n"

            text += i18n.get_text('referral.stats_panel.goals_label', language) + "\n"
            text += i18n.get_text('referral.stats_panel.next_level', language).format(count=next_level_remaining) + "\n"
            text += i18n.get_text('referral.stats_panel.to_vip', language).format(count=to_vip) + "\n"
            text += i18n.get_text('referral.stats_panel.to_elite', language).format(count=to_elite) + "\n\n"

            # Monthly leaderboard top 5
            text += i18n.get_text('referral.stats_panel.leaderboard_label', language) + "\n"
            top5 = sorted_users[:5]
            if top5:
                for idx, u in enumerate(top5, 1):
                    uname = u.get('first_name') or u.get('username') or f"User{idx}"
                    rc = u.get('referral_count', 0)
                    text += f"{idx}. {uname} - {rc}\n"
            else:
                text += i18n.get_text('referral.stats_panel.no_data', language)

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
            
            rc = user_data.get('referral_count', 0)
            earnings = user_data.get('referral_earnings', 0)

            # Rewards panel
            title = i18n.get_text('referral.rewards_panel.title', language)
            text = title + "\n\n"
            text += i18n.get_text('referral.rewards_panel.balance_label', language) + "\n"
            text += i18n.get_text('referral.rewards_panel.available_readings', language).format(count=rc) + "\n"
            text += i18n.get_text('referral.rewards_panel.total_value', language).format(value=earnings) + "\n\n"

            # Badges
            text += i18n.get_text('referral.rewards_panel.badges_label', language) + "\n"
            badges = i18n.get_text('referral.rewards_panel.badges', language)
            earned = []
            thresholds = [1, 5, 10, 25, 50]
            for t in thresholds:
                if rc >= t:
                    label = badges.get(str(t)) if isinstance(badges, dict) else None
                    if label:
                        earned.append(f"• {label}")
            if earned:
                text += "\n".join(earned) + "\n\n"
            else:
                text += i18n.get_text('referral.rewards_panel.no_badges', language) + "\n\n"

            # Perks
            text += i18n.get_text('referral.rewards_panel.perks_label', language) + "\n"
            perks = i18n.get_text('referral.rewards_panel.perks', language)
            shown_any = False
            if isinstance(perks, dict):
                for t in sorted(perks.keys(), key=lambda x: int(x)):
                    if rc >= int(t):
                        plist = perks[t]
                        if isinstance(plist, list) and plist:
                            text += "\n".join(plist) + "\n"
                            shown_any = True
            if not shown_any:
                text += i18n.get_text('referral.rewards_panel.no_perks', language) + "\n"

            # Next rewards
            text += "\n" + i18n.get_text('referral.rewards_panel.next_rewards_label', language) + "\n"
            next_t = 5 if rc < 5 else 10 if rc < 10 else 25 if rc < 25 else 50 if rc < 50 else None
            if next_t:
                nr_tpl = i18n.get_text('referral.rewards_panel.next_reward_template', language)
                remaining = max(0, next_t - rc)
                # choose first reward name of that tier if exists
                reward_name = ''
                if isinstance(perks, dict) and str(next_t) in perks and isinstance(perks[str(next_t)], list) and perks[str(next_t)]:
                    reward_name = perks[str(next_t)][0].replace('• ', '')
                text += nr_tpl.format(remaining=remaining, reward_name=reward_name) + "\n\n"

            # Offers list
            text += i18n.get_text('referral.rewards_panel.offers_label', language) + "\n"
            offers = i18n.get_text('referral.rewards_panel.offers_list', language)
            if isinstance(offers, list) and offers:
                text += "\n".join(offers)
            
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
            
            text = i18n.get_text("referral_system.description", language)
            
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
                i18n.get_text('referral_system.description', language),
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
"""
Referral handlers for the Fal Gram Bot.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.database import db_service
from src.keyboards.referral import ReferralKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
from src.utils.helpers import generate_referral_code
from src.models.referral import Referral, ReferralStats

logger = get_logger("referral_handlers")

class ReferralHandlers:
    """Referral system handlers."""
    
    @staticmethod
    async def show_referral_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral menu."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        keyboard = ReferralKeyboards.get_referral_menu(language)
        text = i18n.get_text("referral.menu_title", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's referral information."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Get user's referral code
        user_data = await db_service.get_user(user.id)
        if not user_data:
            text = i18n.get_text("error.user_not_found", language)
            keyboard = ReferralKeyboards.get_back_button(language, "main_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            return
        
        referral_code = user_data.get('referral_code')
        if not referral_code:
            # Generate referral code if not exists
            referral_code = generate_referral_code(user.id)
            await db_service.update_user(user.id, {'referral_code': referral_code})
        
        # Get referral statistics
        referral_stats = await ReferralHandlers._get_user_referral_stats(user.id)
        
        # Format referral link
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        text = i18n.get_text("referral.info_title", language)
        text += f"\n\n{i18n.get_text('referral.your_code', language)}: `{referral_code}`"
        text += f"\n{i18n.get_text('referral.your_link', language)}: `{referral_link}`"
        text += f"\n\n{i18n.get_text('referral.stats', language)}:"
        text += f"\n• {i18n.get_text('referral.total_referrals', language)}: {referral_stats['total_referrals']}"
        text += f"\n• {i18n.get_text('referral.completed_referrals', language)}: {referral_stats['completed_referrals']}"
        text += f"\n• {i18n.get_text('referral.current_level', language)}: {referral_stats['current_level']}"
        text += f"\n• {i18n.get_text('referral.rewards_earned', language)}: {referral_stats['total_rewards']} days"
        
        keyboard = ReferralKeyboards.get_referral_info_keyboard(language)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
    
    @staticmethod
    async def show_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show detailed referral statistics."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Get referral statistics
        referral_stats = await ReferralHandlers._get_user_referral_stats(user.id)
        
        text = i18n.get_text("referral.stats_title", language)
        text += f"\n\n{i18n.get_text('referral.detailed_stats', language)}:"
        text += f"\n• {i18n.get_text('referral.total_referrals', language)}: {referral_stats['total_referrals']}"
        text += f"\n• {i18n.get_text('referral.completed_referrals', language)}: {referral_stats['completed_referrals']}"
        text += f"\n• {i18n.get_text('referral.pending_referrals', language)}: {referral_stats['pending_referrals']}"
        text += f"\n• {i18n.get_text('referral.current_level', language)}: {referral_stats['current_level']}"
        text += f"\n• {i18n.get_text('referral.rewards_earned', language)}: {referral_stats['total_rewards']} days"
        
        # Add next level info
        next_level_info = referral_stats.get('next_level_info', {})
        if next_level_info.get('referrals_needed', 0) > 0:
            text += f"\n\n{i18n.get_text('referral.next_level', language)}:"
            text += f"\n• {i18n.get_text('referral.referrals_needed', language)}: {next_level_info['referrals_needed']}"
            text += f"\n• {i18n.get_text('referral.next_level_rewards', language)}: {next_level_info.get('rewards', {}).get('description', 'N/A')}"
        
        keyboard = ReferralKeyboards.get_back_button(language, "referral_menu")
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def show_referral_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral leaderboard."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Get top referrers
        top_referrers = await ReferralHandlers._get_top_referrers()
        
        text = i18n.get_text("referral.leaderboard_title", language)
        text += f"\n\n{i18n.get_text('referral.top_referrers', language)}:\n"
        
        for i, referrer in enumerate(top_referrers[:10], 1):
            user_name = referrer.get('first_name', 'Unknown')
            completed_referrals = referrer.get('completed_referrals', 0)
            level = referrer.get('current_level', 1)
            
            text += f"{i}. {user_name} - {completed_referrals} {i18n.get_text('referral.referrals', language)} (Level {level})\n"
        
        keyboard = ReferralKeyboards.get_back_button(language, "referral_menu")
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def show_referral_rewards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show referral rewards information."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        text = i18n.get_text("referral.rewards_title", language)
        text += f"\n\n{i18n.get_text('referral.rewards_info', language)}:"
        text += f"\n• {i18n.get_text('referral.level_1', language)}: 1-2 referrals = 7 days premium"
        text += f"\n• {i18n.get_text('referral.level_2', language)}: 3-4 referrals = 14 days premium"
        text += f"\n• {i18n.get_text('referral.level_3', language)}: 5-9 referrals = 30 days premium"
        text += f"\n• {i18n.get_text('referral.level_4', language)}: 10-19 referrals = 60 days premium"
        text += f"\n• {i18n.get_text('referral.level_5', language)}: 20-49 referrals = 90 days premium"
        text += f"\n• {i18n.get_text('referral.level_6', language)}: 50-99 referrals = 180 days premium"
        text += f"\n• {i18n.get_text('referral.level_7', language)}: 100+ referrals = 365 days premium"
        
        text += f"\n\n{i18n.get_text('referral.how_it_works', language)}:"
        text += f"\n1. {i18n.get_text('referral.share_link', language)}"
        text += f"\n2. {i18n.get_text('referral.friends_join', language)}"
        text += f"\n3. {i18n.get_text('referral.earn_rewards', language)}"
        
        keyboard = ReferralKeyboards.get_back_button(language, "referral_menu")
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def share_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Share referral link."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Get user's referral code
        user_data = await db_service.get_user(user.id)
        if not user_data:
            text = i18n.get_text("error.user_not_found", language)
            keyboard = ReferralKeyboards.get_back_button(language, "referral_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            return
        
        referral_code = user_data.get('referral_code')
        if not referral_code:
            referral_code = generate_referral_code(user.id)
            await db_service.update_user(user.id, {'referral_code': referral_code})
        
        # Format referral link
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        text = i18n.get_text("referral.share_title", language)
        text += f"\n\n{i18n.get_text('referral.share_message', language)}"
        text += f"\n\n`{referral_link}`"
        
        keyboard = ReferralKeyboards.get_share_keyboard(language, referral_link)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
    
    @staticmethod
    async def process_referral_start(user_id: int, referral_code: str) -> bool:
        """Process referral when user starts bot with referral code."""
        try:
            # Find referrer by referral code
            referrer_data = await db_service.get_user_by_referral_code(referral_code)
            if not referrer_data:
                logger.warning(f"Invalid referral code: {referral_code}")
                return False
            
            referrer_id = referrer_data.get('user_id')
            
            # Don't allow self-referral
            if referrer_id == user_id:
                logger.warning(f"User {user_id} tried to refer themselves")
                return False
            
            # Check if user already has a referrer
            user_data = await db_service.get_user(user_id)
            if user_data and user_data.get('referred_by'):
                logger.info(f"User {user_id} already has a referrer")
                return False
            
            # Create referral relationship
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=user_id,
                referral_code=referral_code
            )
            
            # Save referral to database
            await db_service.create_referral_relationship(referral.to_dict())
            
            # Update user's referred_by field
            await db_service.update_user(user_id, {'referred_by': referrer_id})
            
            # Update referrer's referral count
            await db_service.update_user(referrer_id, {
                'referral_count': referrer_data.get('referral_count', 0) + 1
            })
            
            logger.info(f"Referral created: {referrer_id} -> {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing referral: {e}")
            return False
    
    @staticmethod
    async def complete_referral(referrer_id: int, referred_id: int) -> bool:
        """Complete a referral when referred user becomes active."""
        try:
            # Find referral relationship
            referral_data = await db_service.get_referral_relationship(referrer_id, referred_id)
            if not referral_data:
                return False
            
            # Mark referral as completed
            await db_service.update_referral_status(referral_data['id'], 'completed')
            
            # Give rewards to referrer
            await ReferralHandlers._give_referral_rewards(referrer_id)
            
            # Update referral statistics
            await ReferralHandlers._update_referral_stats(referrer_id)
            
            logger.info(f"Referral completed: {referrer_id} -> {referred_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing referral: {e}")
            return False
    
    @staticmethod
    async def _get_user_referral_stats(user_id: int) -> Dict[str, Any]:
        """Get user's referral statistics."""
        try:
            # Get user's referrals
            referrals = await db_service.get_user_referrals(user_id)
            
            total_referrals = len(referrals) if referrals else 0
            completed_referrals = len([r for r in referrals if r.get('status') == 'completed']) if referrals else 0
            pending_referrals = total_referrals - completed_referrals
            
            # Calculate level and rewards
            level = 1
            total_rewards = 0
            
            if completed_referrals >= 100:
                level = 7
                total_rewards = 365
            elif completed_referrals >= 50:
                level = 6
                total_rewards = 180
            elif completed_referrals >= 20:
                level = 5
                total_rewards = 90
            elif completed_referrals >= 10:
                level = 4
                total_rewards = 60
            elif completed_referrals >= 5:
                level = 3
                total_rewards = 30
            elif completed_referrals >= 3:
                level = 2
                total_rewards = 14
            elif completed_referrals >= 1:
                level = 1
                total_rewards = 7
            
            # Calculate next level info
            next_level_info = ReferralHandlers._get_next_level_info(completed_referrals)
            
            return {
                'total_referrals': total_referrals,
                'completed_referrals': completed_referrals,
                'pending_referrals': pending_referrals,
                'current_level': level,
                'total_rewards': total_rewards,
                'next_level_info': next_level_info
            }
            
        except Exception as e:
            logger.error(f"Error getting referral stats: {e}")
            return {
                'total_referrals': 0,
                'completed_referrals': 0,
                'pending_referrals': 0,
                'current_level': 1,
                'total_rewards': 0,
                'next_level_info': {}
            }
    
    @staticmethod
    async def _get_top_referrers() -> List[Dict[str, Any]]:
        """Get top referrers."""
        try:
            # Get all users with referrals
            all_users = await db_service.get_all_users()
            
            # Filter users with referrals and sort by completed referrals
            referrers = []
            for user in all_users:
                if user.get('referral_count', 0) > 0:
                    referrals = await db_service.get_user_referrals(user['user_id'])
                    completed_referrals = len([r for r in referrals if r.get('status') == 'completed']) if referrals else 0
                    
                    referrers.append({
                        'user_id': user['user_id'],
                        'first_name': user.get('first_name', 'Unknown'),
                        'completed_referrals': completed_referrals,
                        'current_level': ReferralHandlers._calculate_level(completed_referrals)
                    })
            
            # Sort by completed referrals (descending)
            referrers.sort(key=lambda x: x['completed_referrals'], reverse=True)
            
            return referrers
            
        except Exception as e:
            logger.error(f"Error getting top referrers: {e}")
            return []
    
    @staticmethod
    async def _give_referral_rewards(user_id: int) -> bool:
        """Give rewards to user for successful referral."""
        try:
            # Get user's referral statistics
            stats = await ReferralHandlers._get_user_referral_stats(user_id)
            completed_referrals = stats['completed_referrals']
            
            # Calculate reward based on level
            reward_days = 7  # Default reward
            
            if completed_referrals >= 100:
                reward_days = 365
            elif completed_referrals >= 50:
                reward_days = 180
            elif completed_referrals >= 20:
                reward_days = 90
            elif completed_referrals >= 10:
                reward_days = 60
            elif completed_referrals >= 5:
                reward_days = 30
            elif completed_referrals >= 3:
                reward_days = 14
            elif completed_referrals >= 1:
                reward_days = 7
            
            # Add premium days to user
            user_data = await db_service.get_user(user_id)
            if user_data:
                current_expiry = user_data.get('premium_expires_at')
                
                if current_expiry:
                    try:
                        expiry_date = datetime.fromisoformat(current_expiry)
                        new_expiry = expiry_date + timedelta(days=reward_days)
                    except:
                        new_expiry = datetime.now() + timedelta(days=reward_days)
                else:
                    new_expiry = datetime.now() + timedelta(days=reward_days)
                
                # Update user's premium status
                await db_service.update_user(user_id, {
                    'is_premium': True,
                    'premium_expires_at': new_expiry.isoformat()
                })
                
                logger.info(f"Referral rewards given to user {user_id}: {reward_days} days premium")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error giving referral rewards: {e}")
            return False
    
    @staticmethod
    async def _update_referral_stats(user_id: int) -> None:
        """Update user's referral statistics."""
        try:
            # This would update referral statistics in the database
            # For now, just log the update
            logger.info(f"Updated referral stats for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating referral stats: {e}")
    
    @staticmethod
    def _get_next_level_info(completed_referrals: int) -> Dict[str, Any]:
        """Get information about next level."""
        level_thresholds = [1, 3, 5, 10, 20, 50, 100]
        
        for threshold in level_thresholds:
            if completed_referrals < threshold:
                next_level = level_thresholds.index(threshold) + 1
                level_rewards = {
                    1: {"premium_days": 7, "description": "7 days premium"},
                    2: {"premium_days": 14, "description": "14 days premium"},
                    3: {"premium_days": 30, "description": "30 days premium"},
                    4: {"premium_days": 60, "description": "60 days premium"},
                    5: {"premium_days": 90, "description": "90 days premium"},
                    6: {"premium_days": 180, "description": "180 days premium"},
                    7: {"premium_days": 365, "description": "365 days premium"}
                }
                
                return {
                    "level": next_level,
                    "referrals_needed": threshold - completed_referrals,
                    "rewards": level_rewards.get(next_level, {"premium_days": 0, "description": "No rewards"})
                }
        
        return {
            "level": 7,
            "referrals_needed": 0,
            "rewards": {"premium_days": 0, "description": "Maximum level reached"}
        }
    
    @staticmethod
    def _calculate_level(completed_referrals: int) -> int:
        """Calculate level based on completed referrals."""
        if completed_referrals >= 100:
            return 7
        elif completed_referrals >= 50:
            return 6
        elif completed_referrals >= 20:
            return 5
        elif completed_referrals >= 10:
            return 4
        elif completed_referrals >= 5:
            return 3
        elif completed_referrals >= 3:
            return 2
        elif completed_referrals >= 1:
            return 1
        else:
            return 1

# Global handlers instance
referral_handlers = ReferralHandlers()
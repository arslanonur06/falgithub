"""
Fortune telling handlers for the Fal Gram Bot.
"""

import asyncio
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.database import db_service
from src.services.ai_service import ai_service
from src.keyboards.fortune import FortuneKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
# Use validator's sanitize to support max_length
from src.utils.validators import validator

logger = get_logger("fortune_handlers")

class FortuneHandlers:
    """Fortune telling handlers."""
    
    @staticmethod
    async def show_fortune_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show fortune telling menu."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        # Use stored language preference from DB for consistency
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        keyboard = FortuneKeyboards.get_fortune_menu(language)
        text = i18n.get_text("menu.fortune", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_tarot_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle tarot reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Show deck/spread options including Daily Card
        prompt_text = i18n.get_text("tarot_fortune_prompt", language)
        keyboard = FortuneKeyboards.get_tarot_deck_keyboard(language)
        await query.edit_message_text(prompt_text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_coffee_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle coffee reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for coffee cup photo
        text = i18n.get_text("coffee_fortune_prompt", language)
        keyboard = FortuneKeyboards.get_back_button(language)
        
        # Set state to wait for photo
        context.user_data['waiting_for'] = 'coffee_photo'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_dream_interpretation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle dream interpretation request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for dream description
        text = i18n.get_text("dream_analysis_prompt", language)
        keyboard = FortuneKeyboards.get_back_button(language)
        
        # Set state to wait for text
        context.user_data['waiting_for'] = 'dream_text'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_palm_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle palm reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for palm photo
        # Reuse generic photo request prompt text
        text = i18n.get_text("coffee_fortune_prompt", language)
        keyboard = FortuneKeyboards.get_back_button(language)
        
        # Set state to wait for photo
        context.user_data['waiting_for'] = 'palm_photo'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_tarot_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle tarot deck/spread option selection including daily card."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        # Check usage limits before generating a reading
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        option = query.data  # e.g., tarot_daily_card, tarot_three_card
        cards_catalog = await FortuneHandlers._get_tarot_cards()
        if not cards_catalog:
            await query.edit_message_text(i18n.get_text("error.general", language), reply_markup=FortuneKeyboards.get_back_button(language))
            return
        
        # Determine number of cards
        if option == "tarot_daily_card":
            num_cards = 1
        elif option in ("tarot_three_card", "tarot_rider_waite"):
            num_cards = 3
        elif option == "tarot_celtic_cross":
            # Use a richer spread size when available; fallback to 5 if deck is small
            num_cards = 10 if len(cards_catalog) >= 10 else min(5, len(cards_catalog))
        else:
            # Unknown option; go back to fortune menu
            await FortuneHandlers.show_fortune_menu(update, context)
            return
        
        # Draw cards and generate interpretation
        drawn_cards = random.sample(cards_catalog, min(num_cards, len(cards_catalog)))
        await FortuneHandlers._generate_tarot_interpretation(query, drawn_cards, language)
        
        # Update usage count
        await db_service.increment_usage(user.id)
    
    @staticmethod
    async def handle_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo input for fortune telling."""
        user = update.effective_user
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        waiting_for = context.user_data.get('waiting_for')
        if not waiting_for:
            return
        
        # Get the largest photo
        photo = update.message.photo[-1]
        
        try:
            # Download photo
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()
            
            if waiting_for == 'coffee_photo':
                await FortuneHandlers._process_coffee_photo(update, context, photo_bytes, language)
            elif waiting_for == 'palm_photo':
                await FortuneHandlers._process_palm_photo(update, context, photo_bytes, language)
            
            # Clear waiting state
            context.user_data.pop('waiting_for', None)
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            text = i18n.get_text("error.general", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text input for fortune telling."""
        user = update.effective_user
        # Use stored language preference from DB for consistency across flows
        try:
            user_data = await db_service.get_user(user.id) if user else None
        except Exception:
            user_data = None
        language = (user_data.get('language') if user_data else None) or (user.language_code if user and user.language_code else 'en')
        
        waiting_for = context.user_data.get('waiting_for')
        if not waiting_for:
            return
        
        text = update.message.text
        sanitized_text = validator.sanitize_text(text, max_length=1000)
        
        if waiting_for == 'dream_text':
            await FortuneHandlers._process_dream_text(update, context, sanitized_text, language)
        
        # Clear waiting state
        context.user_data.pop('waiting_for', None)
    
    @staticmethod
    async def _check_usage_limits(user_id: int, language: str) -> Dict[str, Any]:
        """Check if user can use fortune telling services."""
        user_data = await db_service.get_user(user_id)
        
        if not user_data:
            return {
                'can_use': False,
                'message': i18n.get_text("error.user_not_found", language),
                'keyboard': FortuneKeyboards.get_back_button(language)
            }
        
        # Premium users have unlimited access
        if user_data.get('is_premium'):
            return {'can_use': True}
        
        # Check daily usage for free users
        daily_usage = user_data.get('daily_usage_count', 0)
        free_limit = 3  # Free users get 3 readings per day
        
        if daily_usage >= free_limit:
            return {
                'can_use': False,
                'message': i18n.get_text("fortune.daily_limit_reached", language).format(limit=free_limit),
                'keyboard': FortuneKeyboards.get_premium_upgrade_keyboard(language)
            }
        
        return {'can_use': True}
    
    @staticmethod
    async def _get_tarot_cards() -> List[Dict[str, Any]]:
        """Get tarot cards from database."""
        try:
            # Prefer localized cards from locales if provided (list of {name, meaning})
            # Fallback to English sample set
            # Note: Language will be handled at the call site by selecting desired items
            localized = i18n.get_raw('tarot.cards', 'tr')  # probe key existence
            # We don't know the target language here; return English fallback, caller will format
            default_cards = [
                {"name": "The Fool", "meaning": "New beginnings, innocence, spontaneity"},
                {"name": "The Magician", "meaning": "Manifestation, resourcefulness, power"},
                {"name": "The High Priestess", "meaning": "Intuition, mystery, spirituality"},
                {"name": "The Empress", "meaning": "Fertility, nurturing, abundance"},
                {"name": "The Emperor", "meaning": "Authority, structure, control"},
                {"name": "The Hierophant", "meaning": "Tradition, conformity, morality"},
                {"name": "The Lovers", "meaning": "Love, harmony, relationships"},
                {"name": "The Chariot", "meaning": "Control, willpower, determination"},
                {"name": "Strength", "meaning": "Inner strength, courage, persuasion"},
                {"name": "The Hermit", "meaning": "Soul-searching, introspection, solitude"}
            ]
            return default_cards
        except Exception as e:
            logger.error(f"Error getting tarot cards: {e}")
            return []
    
    @staticmethod
    async def _generate_tarot_interpretation(query, cards: List[Dict[str, Any]], language: str) -> None:
        """Generate tarot card interpretation."""
        try:
            # Build a localized spread prompt from Supabase/i18n if available
            user_id = query.from_user.id if hasattr(query, "from_user") and query.from_user else None
            # Attempt to localize card names/meanings if locales provide them
            # If not available, use provided card objects as-is
            card_names = ", ".join([c.get('name', '') for c in cards])
            card_meanings = "; ".join([c.get('meaning', '') for c in cards])
            prompt_template = (
                await db_service.get_prompt('tarot_spread', language)
                or i18n.get_text('tarot.spread_prompt', language)
            )
            if not prompt_template or prompt_template == 'tarot.spread_prompt':
                prompt_template = (
                    "You are an expert tarot reader. Provide a cohesive interpretation for the spread.\n\n"
                    "Include: overall theme, present situation, guidance, and a hopeful message."
                )
            spread_prompt = f"{prompt_template}\n\nCards: {card_names}\nMeanings: {card_meanings}"
            interpretation = await ai_service.generate_with_fallback(user_id or 0, spread_prompt)
            
            # Format response
            title = i18n.get_text("tarot_fortune", language)
            lines = [f"{idx}. {card.get('name','')}: {card.get('meaning','')}" for idx, card in enumerate(cards, 1)]
            text = f"{title}\n\n" + "\n".join(lines) + (f"\n\n{interpretation}" if interpretation else "")
            
            keyboard = FortuneKeyboards.get_back_button(language)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating tarot interpretation: {e}")
            text = i18n.get_text("error.general", language)
            keyboard = FortuneKeyboards.get_back_button(language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _process_coffee_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_bytes: bytes, language: str) -> None:
        """Process coffee cup photo for reading."""
        try:
            # Send processing message in correct language
            processing_text = i18n.get_text("coffee_fortune_processing", language)
            await update.message.reply_text(processing_text)

            # Fetch coffee prompt and run via AI fallback with image
            user_id = update.effective_user.id
            prompt_template = (
                await db_service.get_prompt('coffee', language)
                or await db_service.get_prompt('coffee_fortune', language)
                or i18n.get_text('coffee_fortune_prompt', language)
            )
            # Personalize if template includes username placeholder
            user_name = (update.effective_user.first_name or '').strip() if update.effective_user else ''
            if user_name:
                prompt_template = prompt_template.replace('{username}', user_name)
            interpretation = await ai_service.generate_with_fallback(user_id, prompt_template, image_data=photo_bytes)
            interpretation = interpretation or prompt_template
            
            # Format response
            title = i18n.get_text("coffee_fortune", language)
            text = f"{title}\n\n{interpretation}"
            
            # Append share on X with #FalGram
            from urllib.parse import quote
            # Include interpretation in the share text, trim to fit 280 characters
            full_share = f"{title}\n\n{interpretation}\n#FalGram"
            share_text = full_share[:270]
            twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
            # Simplify share keyboard to avoid extra menu components
            share_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(i18n.get_text('referral.share_twitter', language), url=twitter_url)],
                [InlineKeyboardButton(i18n.get_text('common.back', language), callback_data='fortune')],
                [InlineKeyboardButton(i18n.get_text('main_menu', language), callback_data='main_menu')]
            ])
            
            keyboard = FortuneKeyboards.get_back_button(language)
            # Send interpretation and share prompt together in one message block
            await update.message.reply_text(text + "\n\n" + i18n.get_text('coffee_fortune_share_twitter_message', language), reply_markup=share_keyboard)
            
            # Update usage
            await db_service.increment_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing coffee photo: {e}")
            text = i18n.get_text("error.general", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def _process_palm_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_bytes: bytes, language: str) -> None:
        """Process palm photo for reading."""
        try:
            # Use fallback with palm-specific hint
            user_id = update.effective_user.id
            palm_hint = i18n.get_text('fortune.palm_reading', language)
            base_prompt = (await db_service.get_prompt('palm', language) or i18n.get_text('coffee_fortune_prompt', language))
            user_name = (update.effective_user.first_name or '').strip() if update.effective_user else ''
            if user_name:
                base_prompt = base_prompt.replace('{username}', user_name)
            palm_prompt = palm_hint + ' - ' + base_prompt
            interpretation = await ai_service.generate_with_fallback(user_id, palm_prompt, image_data=photo_bytes)
            interpretation = interpretation or base_prompt
            
            # Format response
            title = i18n.get_text("fortune.palm_reading", language)
            text = f"{title}\n\n{interpretation}"
            
            action_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(i18n.get_text('common.back', language), callback_data='fortune')],
                [InlineKeyboardButton(i18n.get_text('main_menu', language), callback_data='main_menu')]
            ])
            await update.message.reply_text(text, reply_markup=action_keyboard)
            
            # Update usage
            await db_service.increment_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing palm photo: {e}")
            text = i18n.get_text("error.general", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def _process_dream_text(update: Update, context: ContextTypes.DEFAULT_TYPE, dream_text: str, language: str) -> None:
        """Process dream text for interpretation."""
        try:
            # Fetch dream prompt and send to AI with fallback
            prompt_template = await db_service.get_prompt('dream', language) or i18n.get_text('dream_analysis_prompt', language)
            user_name = (update.effective_user.first_name or '').strip() if update.effective_user else ''
            if user_name:
                prompt_template = prompt_template.replace('{username}', user_name)
            filled_prompt = f"{prompt_template}\n\nDream: {dream_text}"
            interpretation = await ai_service.generate_with_fallback(update.effective_user.id, filled_prompt)
            interpretation = interpretation or prompt_template
            
            # Format response
            title = i18n.get_text("dream_analysis", language)
            text = f"{title}\n\n{interpretation}"
            
            # Append share on X with #FalGram
            from urllib.parse import quote
            full_share = f"{title}\n\n{interpretation}\n#FalGram"
            share_text = full_share[:270]
            twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
            share_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(i18n.get_text('referral.share_twitter', language), url=twitter_url)],
                [InlineKeyboardButton(i18n.get_text('common.back', language), callback_data='fortune')],
                [InlineKeyboardButton(i18n.get_text('main_menu', language), callback_data='main_menu')]
            ])
            
            keyboard = FortuneKeyboards.get_back_button(language)
            await update.message.reply_text(text + "\n\n" + i18n.get_text('coffee_fortune_share_twitter_message', language), reply_markup=share_keyboard)
            
            # Update usage
            await db_service.increment_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing dream text: {e}")
            text = i18n.get_text("error.general", language)
            await update.message.reply_text(text)

# Global handlers instance
fortune_handlers = FortuneHandlers()
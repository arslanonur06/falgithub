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
from src.utils.helpers import sanitize_text
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
        language = user.language_code or "en" if user else "en"
        
        keyboard = FortuneKeyboards.get_fortune_menu(language)
        text = i18n.get_text("fortune.menu_title", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_tarot_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle tarot reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Get tarot cards
        cards = await FortuneHandlers._get_tarot_cards()
        if not cards:
            text = i18n.get_text("fortune.tarot_cards_unavailable", language)
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            return
        
        # Draw random cards
        drawn_cards = random.sample(cards, min(3, len(cards)))
        
        # Generate interpretation
        await FortuneHandlers._generate_tarot_interpretation(query, drawn_cards, language)
        
        # Update usage
        await db_service.increment_user_usage(user.id)
    
    @staticmethod
    async def handle_coffee_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle coffee reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for coffee cup photo
        text = i18n.get_text("fortune.coffee_photo_request", language)
        keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
        
        # Set state to wait for photo
        context.user_data['waiting_for'] = 'coffee_photo'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_dream_interpretation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle dream interpretation request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for dream description
        text = i18n.get_text("fortune.dream_description_request", language)
        keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
        
        # Set state to wait for text
        context.user_data['waiting_for'] = 'dream_text'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_palm_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle palm reading request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check usage limits
        usage_check = await FortuneHandlers._check_usage_limits(user.id, language)
        if not usage_check['can_use']:
            await query.edit_message_text(usage_check['message'], reply_markup=usage_check['keyboard'])
            return
        
        # Ask for palm photo
        text = i18n.get_text("fortune.palm_photo_request", language)
        keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
        
        # Set state to wait for photo
        context.user_data['waiting_for'] = 'palm_photo'
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_photo_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo input for fortune telling."""
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
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
            text = i18n.get_text("error.photo_processing_failed", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text input for fortune telling."""
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        waiting_for = context.user_data.get('waiting_for')
        if not waiting_for:
            return
        
        text = update.message.text
        sanitized_text = sanitize_text(text, max_length=1000)
        
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
                'keyboard': FortuneKeyboards.get_back_button(language, "fortune_menu")
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
            # This would fetch from database in a real implementation
            # For now, return sample cards
            return [
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
        except Exception as e:
            logger.error(f"Error getting tarot cards: {e}")
            return []
    
    @staticmethod
    async def _generate_tarot_interpretation(query, cards: List[Dict[str, Any]], language: str) -> None:
        """Generate tarot card interpretation."""
        try:
            # Create prompt for tarot interpretation
            card_names = [card['name'] for card in cards]
            card_meanings = [card['meaning'] for card in cards]
            
            prompt = i18n.get_text("fortune.tarot_interpretation_prompt", language).format(
                cards=", ".join(card_names),
                meanings=", ".join(card_meanings)
            )
            
            # Generate interpretation using AI
            interpretation = await ai_service.generate_fortune_interpretation(prompt, language)
            
            # Format response
            text = i18n.get_text("fortune.tarot_reading_title", language)
            text += f"\n\n{i18n.get_text('fortune.drawn_cards', language)}:\n"
            
            for i, card in enumerate(cards, 1):
                text += f"{i}. {card['name']}: {card['meaning']}\n"
            
            text += f"\n{i18n.get_text('fortune.interpretation', language)}:\n{interpretation}"
            
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating tarot interpretation: {e}")
            text = i18n.get_text("error.generation_failed", language)
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _process_coffee_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_bytes: bytes, language: str) -> None:
        """Process coffee cup photo for reading."""
        try:
            # Create prompt for coffee reading
            prompt = i18n.get_text("fortune.coffee_reading_prompt", language)
            
            # Generate interpretation using AI with image
            interpretation = await ai_service.generate_image_interpretation(prompt, photo_bytes, language)
            
            # Format response
            text = i18n.get_text("fortune.coffee_reading_title", language)
            text += f"\n\n{interpretation}"
            
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await update.message.reply_text(text, reply_markup=keyboard)
            
            # Update usage
            await db_service.increment_user_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing coffee photo: {e}")
            text = i18n.get_text("error.generation_failed", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def _process_palm_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_bytes: bytes, language: str) -> None:
        """Process palm photo for reading."""
        try:
            # Create prompt for palm reading
            prompt = i18n.get_text("fortune.palm_reading_prompt", language)
            
            # Generate interpretation using AI with image
            interpretation = await ai_service.generate_image_interpretation(prompt, photo_bytes, language)
            
            # Format response
            text = i18n.get_text("fortune.palm_reading_title", language)
            text += f"\n\n{interpretation}"
            
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await update.message.reply_text(text, reply_markup=keyboard)
            
            # Update usage
            await db_service.increment_user_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing palm photo: {e}")
            text = i18n.get_text("error.generation_failed", language)
            await update.message.reply_text(text)
    
    @staticmethod
    async def _process_dream_text(update: Update, context: ContextTypes.DEFAULT_TYPE, dream_text: str, language: str) -> None:
        """Process dream text for interpretation."""
        try:
            # Create prompt for dream interpretation
            prompt = i18n.get_text("fortune.dream_interpretation_prompt", language).format(
                dream=dream_text
            )
            
            # Generate interpretation using AI
            interpretation = await ai_service.generate_fortune_interpretation(prompt, language)
            
            # Format response
            text = i18n.get_text("fortune.dream_interpretation_title", language)
            text += f"\n\n{i18n.get_text('fortune.your_dream', language)}:\n{dream_text}\n\n"
            text += f"{i18n.get_text('fortune.interpretation', language)}:\n{interpretation}"
            
            keyboard = FortuneKeyboards.get_back_button(language, "fortune_menu")
            await update.message.reply_text(text, reply_markup=keyboard)
            
            # Update usage
            await db_service.increment_user_usage(update.effective_user.id)
            
        except Exception as e:
            logger.error(f"Error processing dream text: {e}")
            text = i18n.get_text("error.generation_failed", language)
            await update.message.reply_text(text)

# Global handlers instance
fortune_handlers = FortuneHandlers()
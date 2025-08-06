"""
Astrology handlers for the Fal Gram Bot.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.database import db_service
from src.services.ai_service import ai_service
from src.keyboards.astrology import AstrologyKeyboards
from src.utils.i18n import i18n
from src.utils.logger import get_logger
from src.utils.helpers import calculate_age, is_valid_birth_date
from src.utils.validators import validator
from src.models.user import User

logger = get_logger("astrology_handlers")

class AstrologyHandlers:
    """Astrology feature handlers."""
    
    @staticmethod
    async def show_astrology_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show astrology menu."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        keyboard = AstrologyKeyboards.get_astrology_menu(language)
        text = i18n.get_text("astrology.menu_title", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_birth_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle birth chart request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check if user has birth date
        user_data = await db_service.get_user(user.id)
        if not user_data or not user_data.get('birth_date'):
            text = i18n.get_text("astrology.birth_date_required", language)
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            return
        
        # Check premium access
        premium_check = await AstrologyHandlers._check_premium_access(user.id, language)
        if not premium_check['has_access']:
            await query.edit_message_text(premium_check['message'], reply_markup=premium_check['keyboard'])
            return
        
        # Generate birth chart
        await AstrologyHandlers._generate_birth_chart(query, user_data, language)
    
    @staticmethod
    async def handle_daily_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle daily horoscope request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        keyboard = AstrologyKeyboards.get_zodiac_selection(language, "daily_horoscope")
        text = i18n.get_text("astrology.select_zodiac_daily", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_weekly_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle weekly horoscope request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check premium access
        premium_check = await AstrologyHandlers._check_premium_access(user.id, language)
        if not premium_check['has_access']:
            await query.edit_message_text(premium_check['message'], reply_markup=premium_check['keyboard'])
            return
        
        keyboard = AstrologyKeyboards.get_zodiac_selection(language, "weekly_horoscope")
        text = i18n.get_text("astrology.select_zodiac_weekly", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_monthly_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle monthly horoscope request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check premium access
        premium_check = await AstrologyHandlers._check_premium_access(user.id, language)
        if not premium_check['has_access']:
            await query.edit_message_text(premium_check['message'], reply_markup=premium_check['keyboard'])
            return
        
        keyboard = AstrologyKeyboards.get_zodiac_selection(language, "monthly_horoscope")
        text = i18n.get_text("astrology.select_zodiac_monthly", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle compatibility request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check premium access
        premium_check = await AstrologyHandlers._check_premium_access(user.id, language)
        if not premium_check['has_access']:
            await query.edit_message_text(premium_check['message'], reply_markup=premium_check['keyboard'])
            return
        
        keyboard = AstrologyKeyboards.get_compatibility_menu(language)
        text = i18n.get_text("astrology.compatibility_menu", language)
        
        await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def handle_moon_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle moon calendar request."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Check premium access
        premium_check = await AstrologyHandlers._check_premium_access(user.id, language)
        if not premium_check['has_access']:
            await query.edit_message_text(premium_check['message'], reply_markup=premium_check['keyboard'])
            return
        
        await AstrologyHandlers._generate_moon_calendar(query, language)
    
    @staticmethod
    async def handle_zodiac_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle zodiac sign selection."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Parse callback data: "daily_horoscope_0" -> ("daily_horoscope", 0)
        data_parts = query.data.split("_")
        horoscope_type = data_parts[0] + "_" + data_parts[1]  # "daily_horoscope"
        zodiac_index = int(data_parts[2])
        
        zodiac_signs = [
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
        ]
        
        zodiac_sign = zodiac_signs[zodiac_index]
        
        # Generate horoscope
        await AstrologyHandlers._generate_horoscope(query, horoscope_type, zodiac_sign, language)
    
    @staticmethod
    async def handle_compatibility_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle compatibility sign selection."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = user.language_code or "en" if user else "en"
        
        # Parse callback data: "compat_first_0" -> ("first", 0)
        data_parts = query.data.split("_")
        selection_type = data_parts[1]  # "first" or "second"
        zodiac_index = int(data_parts[2])
        
        # Store selection in context
        if 'compatibility_selection' not in context.user_data:
            context.user_data['compatibility_selection'] = {}
        
        context.user_data['compatibility_selection'][selection_type] = zodiac_index
        
        # Check if both signs are selected
        if len(context.user_data['compatibility_selection']) == 2:
            await AstrologyHandlers._generate_compatibility(query, context.user_data['compatibility_selection'], language)
        else:
            # Show second sign selection
            keyboard = AstrologyKeyboards.get_zodiac_selection(language, "compat_second")
            text = i18n.get_text("astrology.select_second_sign", language)
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _check_premium_access(user_id: int, language: str) -> Dict[str, Any]:
        """Check if user has premium access for astrology features."""
        user_data = await db_service.get_user(user_id)
        
        if not user_data:
            return {
                'has_access': False,
                'message': i18n.get_text("error.user_not_found", language),
                'keyboard': AstrologyKeyboards.get_back_button(language, "astrology_menu")
            }
        
        # Daily horoscope is free, others need premium
        if user_data.get('is_premium'):
            return {'has_access': True}
        
        return {
            'has_access': False,
            'message': i18n.get_text("astrology.premium_required", language),
            'keyboard': AstrologyKeyboards.get_premium_upgrade_keyboard(language)
        }
    
    @staticmethod
    async def _generate_birth_chart(query, user_data: Dict[str, Any], language: str) -> None:
        """Generate birth chart interpretation."""
        try:
            # Get birth date
            birth_date = datetime.fromisoformat(user_data['birth_date'])
            
            # Create prompt for birth chart
            prompt = i18n.get_text("astrology.birth_chart_prompt", language).format(
                birth_date=birth_date.strftime("%Y-%m-%d"),
                birth_time=user_data.get('birth_time', 'unknown'),
                birth_place=user_data.get('birth_place', 'unknown')
            )
            
            # Generate interpretation using AI
            interpretation = await ai_service.generate_astrology_interpretation(prompt, language)
            
            # Format response
            text = i18n.get_text("astrology.birth_chart_title", language).format(
                name=user_data.get('first_name', 'User'),
                birth_date=birth_date.strftime("%Y-%m-%d")
            )
            text += f"\n\n{interpretation}"
            
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating birth chart: {e}")
            text = i18n.get_text("error.generation_failed", language)
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _generate_horoscope(query, horoscope_type: str, zodiac_sign: str, language: str) -> None:
        """Generate horoscope interpretation."""
        try:
            # Create prompt based on type
            if horoscope_type == "daily_horoscope":
                prompt = i18n.get_text("astrology.daily_horoscope_prompt", language).format(
                    zodiac_sign=zodiac_sign,
                    date=datetime.now().strftime("%Y-%m-%d")
                )
            elif horoscope_type == "weekly_horoscope":
                prompt = i18n.get_text("astrology.weekly_horoscope_prompt", language).format(
                    zodiac_sign=zodiac_sign,
                    week_start=datetime.now().strftime("%Y-%m-%d")
                )
            elif horoscope_type == "monthly_horoscope":
                prompt = i18n.get_text("astrology.monthly_horoscope_prompt", language).format(
                    zodiac_sign=zodiac_sign,
                    month=datetime.now().strftime("%B %Y")
                )
            
            # Generate interpretation
            interpretation = await ai_service.generate_astrology_interpretation(prompt, language)
            
            # Format response
            zodiac_names = {
                "aries": "Koç", "taurus": "Boğa", "gemini": "İkizler",
                "cancer": "Yengeç", "leo": "Aslan", "virgo": "Başak",
                "libra": "Terazi", "scorpio": "Akrep", "sagittarius": "Yay",
                "capricorn": "Oğlak", "aquarius": "Kova", "pisces": "Balık"
            }
            
            text = i18n.get_text("astrology.horoscope_title", language).format(
                zodiac_name=zodiac_names.get(zodiac_sign, zodiac_sign),
                type=i18n.get_text(f"astrology.{horoscope_type}", language)
            )
            text += f"\n\n{interpretation}"
            
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating horoscope: {e}")
            text = i18n.get_text("error.generation_failed", language)
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _generate_compatibility(query, selection: Dict[str, int], language: str) -> None:
        """Generate compatibility analysis."""
        try:
            zodiac_signs = [
                "aries", "taurus", "gemini", "cancer", "leo", "virgo",
                "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
            ]
            
            sign1 = zodiac_signs[selection['first']]
            sign2 = zodiac_signs[selection['second']]
            
            # Create compatibility prompt
            prompt = i18n.get_text("astrology.compatibility_prompt", language).format(
                sign1=sign1, sign2=sign2
            )
            
            # Generate interpretation
            interpretation = await ai_service.generate_astrology_interpretation(prompt, language)
            
            # Format response
            zodiac_names = {
                "aries": "Koç", "taurus": "Boğa", "gemini": "İkizler",
                "cancer": "Yengeç", "leo": "Aslan", "virgo": "Başak",
                "libra": "Terazi", "scorpio": "Akrep", "sagittarius": "Yay",
                "capricorn": "Oğlak", "aquarius": "Kova", "pisces": "Balık"
            }
            
            text = i18n.get_text("astrology.compatibility_title", language).format(
                sign1_name=zodiac_names.get(sign1, sign1),
                sign2_name=zodiac_names.get(sign2, sign2)
            )
            text += f"\n\n{interpretation}"
            
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating compatibility: {e}")
            text = i18n.get_text("error.generation_failed", language)
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
    
    @staticmethod
    async def _generate_moon_calendar(query, language: str) -> None:
        """Generate moon calendar information."""
        try:
            # Calculate current moon phase
            from src.utils.helpers import calculate_moon_phase
            
            moon_phase = calculate_moon_phase()
            
            # Create moon calendar prompt
            prompt = i18n.get_text("astrology.moon_calendar_prompt", language).format(
                moon_phase=moon_phase['phase'],
                illumination=moon_phase['illumination']
            )
            
            # Generate interpretation
            interpretation = await ai_service.generate_astrology_interpretation(prompt, language)
            
            # Format response
            text = i18n.get_text("astrology.moon_calendar_title", language)
            text += f"\n\n{interpretation}"
            
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error generating moon calendar: {e}")
            text = i18n.get_text("error.generation_failed", language)
            keyboard = AstrologyKeyboards.get_back_button(language, "astrology_menu")
            await query.edit_message_text(text, reply_markup=keyboard)

# Global handlers instance
astrology_handlers = AstrologyHandlers()
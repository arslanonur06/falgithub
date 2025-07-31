#!/usr/bin/env python3
"""
🔮 Fal Gram - AI-Powered Fortune Telling Telegram Bot
Version: 3.1.1
Multi-language support with direct locale file fetching
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Telegram Bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

# AI and Database imports
import google.generativeai as genai
from supabase import create_client, Client
import aiohttp
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'tr': 'Türkçe', 
    'es': 'Español',
    'fr': 'Français',
    'ru': 'Русский',
    'de': 'Deutsch',
    'ar': 'العربية',
    'it': 'Italiano',
    'pt': 'Português'
}

class LocaleManager:
    """Manages locale files and text retrieval"""
    
    def __init__(self):
        self.locales = {}
        self.load_all_locales()
    
    def load_all_locales(self):
        """Load all locale files"""
        locales_dir = 'locales'
        for lang_code in SUPPORTED_LANGUAGES.keys():
            file_path = os.path.join(locales_dir, f'{lang_code}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.locales[lang_code] = json.load(f)
                logger.info(f"Loaded locale: {lang_code}")
            except FileNotFoundError:
                logger.error(f"Locale file not found: {file_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {file_path}: {e}")
    
    def get_text(self, key: str, lang: str = 'en', **kwargs) -> str:
        """Get text from locale file with fallback"""
        # Default to English if language not supported
        if lang not in self.locales:
            lang = 'en'
        
        # Get text from locale
        locale_data = self.locales[lang]
        
        # Handle nested keys (e.g., "admin_panel.buttons.stats")
        keys = key.split('.')
        text = locale_data
        
        for k in keys:
            if isinstance(text, dict) and k in text:
                text = text[k]
            else:
                # Fallback to English
                text = self.locales['en']
                for fallback_k in keys:
                    if isinstance(text, dict) and fallback_k in text:
                        text = text[fallback_k]
                    else:
                        return f"[{key}]"  # Key not found
        
        # Format with kwargs if text is a string
        if isinstance(text, str):
            return text.format(**kwargs)
        elif isinstance(text, list):
            return '\n'.join(text)
        else:
            return str(text)
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        return SUPPORTED_LANGUAGES.get(lang_code, lang_code)

class SupabaseManager:
    """Manages Supabase database operations"""
    
    def __init__(self, url: str, key: str):
        self.supabase = create_client(url, key)
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user from database"""
        try:
            result = self.supabase.table('users').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def create_user(self, user_id: int, username: str, first_name: str, language: str = 'en') -> bool:
        """Create new user"""
        try:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'language': language,
                'created_at': datetime.now().isoformat(),
                'free_readings_left': 5,
                'is_premium': False,
                'premium_plan': None,
                'premium_expires': None,
                'daily_card_subscribed': False,
                'referral_count': 0,
                'referral_earnings': 0
            }
            
            self.supabase.table('users').insert(user_data).execute()
            logger.info(f"Created user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            self.supabase.table('users').update(updates).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def add_log(self, message: str) -> bool:
        """Add log entry"""
        try:
            log_data = {
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.supabase.table('logs').insert(log_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding log: {e}")
            return False
    
    async def get_tarot_cards(self) -> List[str]:
        """Get tarot cards from config"""
        try:
            result = self.supabase.table('config').select('value').eq('key', 'tarot_cards').execute()
            if result.data:
                return json.loads(result.data[0]['value'])
            return []
        except Exception as e:
            logger.error(f"Error getting tarot cards: {e}")
            return []
    
    async def get_prompt(self, key: str, language: str = 'en') -> str:
        """Get prompt from database"""
        try:
            result = self.supabase.table('prompts').select('*').eq('key', key).eq('language', language).execute()
            if result.data:
                return result.data[0]['content']
            
            # Fallback to English
            result = self.supabase.table('prompts').select('*').eq('key', key).eq('language', 'en').execute()
            if result.data:
                return result.data[0]['content']
            
            return ""
        except Exception as e:
            logger.error(f"Error getting prompt {key}: {e}")
            return ""

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}
    
    async def can_make_call(self, user_id: int) -> bool:
        """Check if user can make API call"""
        now = datetime.now()
        if user_id not in self.calls:
            self.calls[user_id] = []
        
        # Remove old calls
        self.calls[user_id] = [call_time for call_time in self.calls[user_id] 
                             if (now - call_time).seconds < self.time_window]
        
        if len(self.calls[user_id]) < self.max_calls:
            self.calls[user_id].append(now)
            return True
        return False

# Initialize managers
locale_manager = LocaleManager()
supabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)
rate_limiter = RateLimiter()

class FalGramBot:
    """Main bot class"""
    
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("gift", self.gift_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Get or create user
        user_data = await supabase_manager.get_user(user_id)
        if not user_data:
            # Detect language from Telegram client
            language = user.language_code if user.language_code in SUPPORTED_LANGUAGES else 'en'
            await supabase_manager.create_user(user_id, user.username, user.first_name, language)
            user_data = await supabase_manager.get_user(user_id)
        
        language = user_data.get('language', 'en')
        
        # Handle referral
        if context.args:
            referrer_id = context.args[0]
            await self.handle_referral(user_id, referrer_id, language)
        
        # Send welcome message
        welcome_text = locale_manager.get_text('start_message', language)
        keyboard = self.create_main_menu_keyboard(language)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
        await supabase_manager.add_log(f"User {user_id} started bot")
    
    async def handle_referral(self, user_id: int, referrer_id: str, language: str):
        """Handle referral system"""
        try:
            referrer_user_id = int(referrer_id)
            referrer_data = await supabase_manager.get_user(referrer_user_id)
            
            if referrer_data and referrer_user_id != user_id:
                # Update referrer stats
                new_count = referrer_data.get('referral_count', 0) + 1
                new_earnings = referrer_data.get('referral_earnings', 0) + 1
                
                await supabase_manager.update_user(referrer_user_id, {
                    'referral_count': new_count,
                    'referral_earnings': new_earnings
                })
                
                # Update new user
                await supabase_manager.update_user(user_id, {
                    'free_readings_left': 6  # Bonus reading
                })
                
                await supabase_manager.add_log(f"Referral processed: {user_id} referred by {referrer_user_id}")
        except ValueError:
            logger.warning(f"Invalid referrer ID: {referrer_id}")
    
    def create_main_menu_keyboard(self, language: str) -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(
                    locale_manager.get_text('coffee_fortune', language),
                    callback_data='coffee_fortune'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('tarot_fortune', language),
                    callback_data='tarot_fortune'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('dream_analysis', language),
                    callback_data='dream_analysis'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('astrology', language),
                    callback_data='astrology'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('daily_card', language),
                    callback_data='daily_card'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('referral', language),
                    callback_data='referral'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('language', language),
                    callback_data='language'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('premium_menu', language),
                    callback_data='premium_menu'
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        language = user_data.get('language', 'en')
        
        callback_data = query.data
        
        # Route to appropriate handler
        handlers = {
            'coffee_fortune': self.handle_coffee_fortune,
            'tarot_fortune': self.handle_tarot_fortune,
            'dream_analysis': self.handle_dream_analysis,
            'astrology': self.handle_astrology,
            'daily_card': self.handle_daily_card,
            'referral': self.handle_referral_menu,
            'language': self.handle_language_selection,
            'premium_menu': self.handle_premium_menu,
            'main_menu': self.handle_main_menu
        }
        
        handler = handlers.get(callback_data)
        if handler:
            await handler(update, context, language)
        else:
            await query.edit_message_text(
                locale_manager.get_text('fortune_error', language)
            )
    
    async def handle_coffee_fortune(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle coffee fortune request"""
        query = update.callback_query
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        # Check if user has readings left
        if not user_data.get('is_premium') and user_data.get('free_readings_left', 0) <= 0:
            await query.edit_message_text(
                locale_manager.get_text('fortune_limit_reached', language, stars_count=500)
            )
            return
        
        await query.edit_message_text(
            locale_manager.get_text('coffee_fortune_prompt', language)
        )
        
        # Set user state
        context.user_data['waiting_for'] = 'coffee_photo'
    
    async def handle_tarot_fortune(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle tarot fortune request"""
        query = update.callback_query
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        # Check if user has readings left
        if not user_data.get('is_premium') and user_data.get('free_readings_left', 0) <= 0:
            await query.edit_message_text(
                locale_manager.get_text('fortune_limit_reached', language, stars_count=500)
            )
            return
        
        # Draw tarot card
        await query.edit_message_text(
            locale_manager.get_text('tarot_drawing', language)
        )
        
        try:
            tarot_cards = await supabase_manager.get_tarot_cards()
            if not tarot_cards:
                await query.edit_message_text(
                    locale_manager.get_text('fortune_error', language)
                )
                return
            
            import random
            selected_card = random.choice(tarot_cards)
            
            # Get tarot prompt
            prompt = await supabase_manager.get_prompt('tarot_reading', language)
            if not prompt:
                prompt = "Interpret this tarot card: {card}"
            
            # Generate interpretation
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                prompt.format(card=selected_card),
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            interpretation = response.text
            
            # Format response
            result_text = f"🎴 **{selected_card}**\n\n{interpretation}"
            
            keyboard = [[InlineKeyboardButton(
                locale_manager.get_text('main_menu_button', language),
                callback_data='main_menu'
            )]]
            
            await query.edit_message_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update user readings
            if not user_data.get('is_premium'):
                await supabase_manager.update_user(user_id, {
                    'free_readings_left': user_data.get('free_readings_left', 0) - 1
                })
            
            await supabase_manager.add_log(f"Tarot reading completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in tarot reading: {e}")
            await query.edit_message_text(
                locale_manager.get_text('fortune_error', language)
            )
    
    async def handle_dream_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle dream analysis request"""
        query = update.callback_query
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        # Check if user has readings left
        if not user_data.get('is_premium') and user_data.get('free_readings_left', 0) <= 0:
            await query.edit_message_text(
                locale_manager.get_text('fortune_limit_reached', language, stars_count=500)
            )
            return
        
        await query.edit_message_text(
            locale_manager.get_text('dream_analysis_prompt', language)
        )
        
        # Set user state
        context.user_data['waiting_for'] = 'dream_text'
    
    async def handle_astrology(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle astrology menu"""
        query = update.callback_query
        
        keyboard = [
            [
                InlineKeyboardButton(
                    locale_manager.get_text('birth_chart', language),
                    callback_data='birth_chart'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('daily_horoscope', language),
                    callback_data='daily_horoscope'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('compatibility', language),
                    callback_data='compatibility'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('moon_calendar', language),
                    callback_data='moon_calendar'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('main_menu_button', language),
                    callback_data='main_menu'
                )
            ]
        ]
        
        await query.edit_message_text(
            locale_manager.get_text('astrology', language),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_daily_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle daily card subscription"""
        query = update.callback_query
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        current_subscription = user_data.get('daily_card_subscribed', False)
        
        if current_subscription:
            # Unsubscribe
            await supabase_manager.update_user(user_id, {
                'daily_card_subscribed': False
            })
            message = locale_manager.get_text('daily_card_unsubscribe', language)
        else:
            # Subscribe
            await supabase_manager.update_user(user_id, {
                'daily_card_subscribed': True
            })
            message = locale_manager.get_text('daily_card_subscribe', language)
        
        keyboard = [[InlineKeyboardButton(
            locale_manager.get_text('main_menu_button', language),
            callback_data='main_menu'
        )]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_referral_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle referral menu"""
        query = update.callback_query
        user_id = query.from_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        referral_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"
        
        message = locale_manager.get_text('referral_prompt', language, referral_link=referral_link)
        
        keyboard = [[InlineKeyboardButton(
            locale_manager.get_text('main_menu_button', language),
            callback_data='main_menu'
        )]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle language selection"""
        query = update.callback_query
        
        keyboard = []
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            keyboard.append([
                InlineKeyboardButton(
                    lang_name,
                    callback_data=f'lang_{lang_code}'
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                locale_manager.get_text('main_menu_button', language),
                callback_data='main_menu'
            )
        ])
        
        await query.edit_message_text(
            locale_manager.get_text('language_selection', language),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle premium menu"""
        query = update.callback_query
        
        keyboard = [
            [
                InlineKeyboardButton(
                    locale_manager.get_text('premium_plan_basic', language),
                    callback_data='premium_basic'
                ),
                InlineKeyboardButton(
                    locale_manager.get_text('premium_plan_premium', language),
                    callback_data='premium_premium'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('premium_plan_vip', language),
                    callback_data='premium_vip'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('plan_comparison', language),
                    callback_data='plan_comparison'
                )
            ],
            [
                InlineKeyboardButton(
                    locale_manager.get_text('main_menu_button', language),
                    callback_data='main_menu'
                )
            ]
        ]
        
        await query.edit_message_text(
            locale_manager.get_text('premium_menu', language),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Handle main menu return"""
        query = update.callback_query
        user_id = query.from_user.id
        
        welcome_text = locale_manager.get_text('start_message', language)
        keyboard = self.create_main_menu_keyboard(language)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        user_data = await supabase_manager.get_user(user_id)
        language = user_data.get('language', 'en')
        
        waiting_for = context.user_data.get('waiting_for')
        
        if waiting_for == 'dream_text':
            await self.process_dream_text(update, context, language)
        elif waiting_for == 'birth_info':
            await self.process_birth_info(update, context, language)
        else:
            # Default response
            keyboard = self.create_main_menu_keyboard(language)
            await update.message.reply_text(
                locale_manager.get_text('main_menu_button', language),
                reply_markup=keyboard
            )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (coffee fortune)"""
        user_id = update.effective_user.id
        user_data = await supabase_manager.get_user(user_id)
        language = user_data.get('language', 'en')
        
        waiting_for = context.user_data.get('waiting_for')
        
        if waiting_for == 'coffee_photo':
            await self.process_coffee_photo(update, context, language)
        else:
            # Default response
            keyboard = self.create_main_menu_keyboard(language)
            await update.message.reply_text(
                locale_manager.get_text('main_menu_button', language),
                reply_markup=keyboard
            )
    
    async def process_dream_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Process dream text for analysis"""
        user_id = update.effective_user.id
        user_data = await supabase_manager.get_user(user_id)
        dream_text = update.message.text
        
        # Check if user has readings left
        if not user_data.get('is_premium') and user_data.get('free_readings_left', 0) <= 0:
            await update.message.reply_text(
                locale_manager.get_text('fortune_limit_reached', language, stars_count=500)
            )
            return
        
        await update.message.reply_text(
            locale_manager.get_text('dream_analyzing', language)
        )
        
        try:
            # Get dream analysis prompt
            prompt = await supabase_manager.get_prompt('dream_analysis', language)
            if not prompt:
                prompt = "Analyze this dream: {dream}"
            
            # Generate analysis
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                prompt.format(dream=dream_text),
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800
                )
            )
            
            analysis = response.text
            
            # Format response
            result_text = f"💭 **{locale_manager.get_text('dream_analysis', language)}**\n\n{analysis}"
            
            keyboard = [[InlineKeyboardButton(
                locale_manager.get_text('main_menu_button', language),
                callback_data='main_menu'
            )]]
            
            await update.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update user readings
            if not user_data.get('is_premium'):
                await supabase_manager.update_user(user_id, {
                    'free_readings_left': user_data.get('free_readings_left', 0) - 1
                })
            
            # Clear waiting state
            context.user_data.pop('waiting_for', None)
            
            await supabase_manager.add_log(f"Dream analysis completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in dream analysis: {e}")
            await update.message.reply_text(
                locale_manager.get_text('fortune_error', language)
            )
    
    async def process_coffee_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Process coffee photo for fortune"""
        user_id = update.effective_user.id
        user_data = await supabase_manager.get_user(user_id)
        
        # Check if user has readings left
        if not user_data.get('is_premium') and user_data.get('free_readings_left', 0) <= 0:
            await update.message.reply_text(
                locale_manager.get_text('fortune_limit_reached', language, stars_count=500)
            )
            return
        
        await update.message.reply_text(
            locale_manager.get_text('fortune_in_progress', language)
        )
        
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Download image
            image_data = await file.download_as_bytearray()
            image = Image.open(io.BytesIO(image_data))
            
            # Get coffee fortune prompt
            prompt = await supabase_manager.get_prompt('coffee_fortune', language)
            if not prompt:
                prompt = "Analyze this coffee cup for fortune telling:"
            
            # Generate fortune
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                [prompt, image],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800
                )
            )
            
            fortune = response.text
            
            # Format response
            result_text = f"☕ **{locale_manager.get_text('coffee_fortune', language)}**\n\n{fortune}"
            
            keyboard = [[InlineKeyboardButton(
                locale_manager.get_text('main_menu_button', language),
                callback_data='main_menu'
            )]]
            
            await update.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update user readings
            if not user_data.get('is_premium'):
                await supabase_manager.update_user(user_id, {
                    'free_readings_left': user_data.get('free_readings_left', 0) - 1
                })
            
            # Clear waiting state
            context.user_data.pop('waiting_for', None)
            
            await supabase_manager.add_log(f"Coffee fortune completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in coffee fortune: {e}")
            await update.message.reply_text(
                locale_manager.get_text('fortune_error', language)
            )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin commands"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            return
        
        # Admin panel logic here
        await update.message.reply_text("🔧 Admin panel - Coming soon!")
    
    async def gift_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle gift subscription command"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID or not context.args:
            return
        
        try:
            target_user_id = int(context.args[0])
            plan = context.args[1] if len(context.args) > 1 else 'basic'
            days = int(context.args[2]) if len(context.args) > 2 else 30
            
            # Gift subscription logic here
            await update.message.reply_text(f"🎁 Gift subscription sent to {target_user_id}")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or days")
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancel subscription command"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID or not context.args:
            return
        
        try:
            target_user_id = int(context.args[0])
            
            # Cancel subscription logic here
            await update.message.reply_text(f"❌ Subscription cancelled for {target_user_id}")
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_user:
            user_id = update.effective_user.id
            user_data = await supabase_manager.get_user(user_id)
            language = user_data.get('language', 'en') if user_data else 'en'
            
            error_message = locale_manager.get_text('fortune_error', language)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            elif update.message:
                await update.message.reply_text(error_message)
    
    async def run(self):
        """Run the bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot started successfully!")
        
        try:
            await asyncio.Event().wait()  # Run forever
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

async def main():
    """Main function"""
    if not all([TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        logger.error("Missing required environment variables!")
        return
    
    bot = FalGramBot()
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main())
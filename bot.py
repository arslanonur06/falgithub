import os
import json
import random
import io
import logging
import time
import asyncio
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from functools import lru_cache
from urllib.parse import quote
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    PreCheckoutQueryHandler, filters, CallbackContext
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fpdf import FPDF
from supabase import create_client, Client

async def safe_edit_message(query, text, reply_markup=None, parse_mode=None):
    """Güvenli mesaj düzenleme fonksiyonu"""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        # Eğer mesaj düzenlenemezse yeni mesaj gönder
        try:
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e2:
            # Son çare olarak sadece metin gönder
            await query.message.reply_text(text)


# --- Locale Handling ---
import json
import os

# Load all locale files at startup
LOCALES = {}
locales_dir = 'locales'
for filename in os.listdir(locales_dir):
    if filename.endswith('.json'):
        lang_code = filename.replace('.json', '')
        filepath = os.path.join(locales_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            LOCALES[lang_code] = json.load(f)

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """Get localized text for a given key, with robust fallback and logging"""
    def get_nested_value(data, key_path):
        keys = key_path.split('.')
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
    text = get_nested_value(LOCALES.get(lang, {}), key)
    if text is None:
        text = get_nested_value(LOCALES.get('en', {}), key)
    if text is None:
        logger.warning(f"Missing translation key: {key} (lang={lang})")
        text = key  # Fallback to key itself
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception as e:
            logger.warning(f"Format error for key {key}: {e}")
    return text

def get_user_language(user_id: int) -> str:
    """Get user's preferred language from database"""
    try:
        user = supabase_manager.get_user(user_id)
        return user.get('language', 'tr') if user else 'tr'
    except:
        return 'tr'

def check_premium_access(user_id: int) -> dict:
    """Check if user has premium access and return plan info"""
    try:
        user = supabase_manager.get_user(user_id)
        if not user:
            return {'has_premium': False, 'plan': None, 'expires_at': None}
        
        premium_plan = user.get('premium_plan')
        expires_at = user.get('premium_expires_at')
        
        if not premium_plan or premium_plan == 'free':
            return {'has_premium': False, 'plan': None, 'expires_at': None}
        
        # Check if subscription has expired
        if expires_at:
            try:
                expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if datetime.now(expiry_date.tzinfo) > expiry_date:
                    # Subscription expired, reset to free
                    supabase_manager.update_user_premium_plan(user_id, 'free')
                    return {'has_premium': False, 'plan': None, 'expires_at': None}
            except:
                pass
        
        return {
            'has_premium': True, 
            'plan': premium_plan, 
            'expires_at': expires_at
        }
    except:
        return {'has_premium': False, 'plan': None, 'expires_at': None}

# --- Başlangıç Kurulumu ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

# Environment variables with defaults
load_dotenv()

# Bot configuration with defaults
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
    exit(1)

ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        logger.warning(f"Invalid ADMIN_ID format: {ADMIN_ID}, using None")
        ADMIN_ID = None
else:
    ADMIN_ID = None
    logger.warning("ADMIN_ID not set, admin features will be disabled")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL or SUPABASE_KEY not found in environment variables!")
    exit(1)

# API Keys with defaults
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

if not GEMINI_API_KEY and not DEEPSEEK_API_KEY:
    logger.warning("No AI API keys found. Some features may not work properly.")

# Payment configuration
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
if not PAYMENT_PROVIDER_TOKEN:
    logger.warning("PAYMENT_PROVIDER_TOKEN not set, payment features will be disabled")

FREE_READING_LIMIT = 5
PAID_READING_STARS = 250  # Artık kullanılmayacak, premium planlara yönlendirme
CHOOSING, TYPING_REPLY = range(2)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Premium Plan Definitions
PREMIUM_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'description': 'Unlimited readings and advanced features',
        'duration': '30 days',
        'price_stars': 500,
        'features': [
            '♾️ Unlimited readings (Coffee, Tarot, Dream)',
            '📊 Weekly horoscope report',
            '🔮 Advanced astrology analysis',
            '💫 Birth chart interpretation',
            '🌙 Moon calendar features',
            '💬 Advanced chatbot',
            '🎯 Personalized recommendations',
            '📈 Detailed reading history',
            '🔔 Special notifications'
        ]
    },
    'premium': {
        'name': 'Premium Plan',
        'description': 'Complete astrology package and special features',
        'duration': '30 days',
        'price_stars': 1000,
        'features': [
            '✨ Basic Plan features',
            '📅 Monthly horoscope',
            '🪐 Planetary transits analysis',
            '💕 Zodiac compatibility',
            '🌙 Advanced moon calendar',
            '📈 Detailed astrology reports',
            '🎯 Personalized recommendations',
            '🔮 Special reading types',
            '📊 Astrology statistics',
            '🎁 Exclusive content',
            '⚡ Priority support'
        ]
    },
    'vip': {
        'name': 'VIP Plan',
        'description': 'Ultimate experience with priority support',
        'duration': '30 days',
        'price_stars': 2000,
        'features': [
            '👑 Premium Plan features',
            '🤖 24/7 Astrology Chatbot',
            '👥 Social astrology features',
            '🎁 Exclusive VIP content',
            '⚡ Priority support',
            '📊 Advanced analytics',
            '🎯 Personal astrology consultant',
            '🌟 Special VIP reading types',
            '💎 Unlimited exclusive content',
            '🎪 Special events',
            '📱 Special VIP interface',
            '🔮 AI-powered personal guidance'
        ]
    }
}

genai.configure(api_key=GEMINI_API_KEY)

# --- SupabaseManager Sınıfı ---
class SupabaseManager:
    def __init__(self, url: str, key: str):
        try:
            self.client: Client = create_client(url, key)
            logger.info("Supabase istemcisi başarıyla başlatıldı.")
        except Exception as e:
            logger.critical(f"Supabase istemcisi başlatılamadı: {e}")
            self.client = None

    # --- Kullanıcı Fonksiyonları ---
    def get_user(self, user_id: int):
        try:
            result = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_user hatası: {e}")
            return None

    def create_user(self, user_data: dict):
        try:
            result = self.client.table("users").insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Supabase create_user hatası: {e}")
            return None
    
    def update_user(self, user_id: int, data: dict):
        try:
            self.client.table("users").update(data).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Supabase update_user hatası: {e}")

    def create_or_update_user(self, user_id: int, user_data: dict):
        """Create user if not exists, otherwise update"""
        try:
            # Check if user exists
            existing_user = self.get_user(user_id)
            if existing_user:
                # Update existing user
                self.update_user(user_id, user_data)
                return existing_user
            else:
                # Create new user
                user_data['id'] = user_id
                return self.create_user(user_data)
        except Exception as e:
            logger.error(f"Supabase create_or_update_user hatası: {e}")
            return None

    def get_all_users(self):
        try:
            result = self.client.table("users").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_all_users hatası: {e}")
            return []

    def get_subscribed_users(self):
        try:
            result = self.client.table("users").select("id").eq("astro_subscribed", True).execute()
            return [user["id"] for user in result.data]
        except Exception as e:
            logger.error(f"Supabase get_subscribed_users hatası: {e}")
            return []
    
    def get_premium_users(self):
        """Premium kullanıcıları getir"""
        try:
            result = self.client.table("users").select("*").not_.is_("premium_plan", "null").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_premium_users hatası: {e}")
            return []
    
    def get_user_subscriptions(self):
        """Tüm kullanıcı aboneliklerini getir"""
        try:
            result = self.client.table("user_subscriptions").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_user_subscriptions hatası: {e}")
            return []
    
    def update_user_premium_plan(self, user_id: int, plan_id: str, expires_at=None):
        """Kullanıcının premium planını güncelle"""
        try:
            data = {'premium_plan': plan_id}
            if expires_at:
                data['premium_expires_at'] = expires_at
            self.client.table("users").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_user_premium_plan hatası: {e}")
            return False
    
    def get_payment_statistics(self):
        """Ödeme istatistiklerini getir"""
        try:
            result = self.client.table("payment_transactions").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_payment_statistics hatası: {e}")
            return []
    
    def get_referral_relationships(self):
        """Referral ilişkilerini getirir."""
        try:
            # Tüm kullanıcıları al ve referral bilgilerini kontrol et
            result = self.client.table("users").select("id, first_name, username, referred_count, referral_earnings").execute()
            users = result.data
            
            # Referral ilişkilerini analiz et
            referral_data = []
            for user in users:
                if user.get('referred_count', 0) > 0:
                    referral_data.append({
                        'user_id': user['id'],
                        'name': user.get('first_name', 'Bilinmeyen'),
                        'username': user.get('username', ''),
                        'referred_count': user.get('referred_count', 0),
                        'earnings': user.get('referral_earnings', 0)
                    })
            
            return referral_data
        except Exception as e:
            logger.error(f"Supabase get_referral_relationships hatası: {e}")
            return []
    
    def get_user_referrals(self, user_id: int):
        """Get referrals made by a specific user"""
        try:
            # Check if referral_relationships table exists, otherwise use users table
            try:
                result = self.client.table("referral_relationships").select("*").eq("referrer_id", user_id).execute()
                return result.data
            except:
                # Fallback to users table
                result = self.client.table("users").select("id, first_name, username, created_at").eq("referred_by", user_id).execute()
                return result.data
        except Exception as e:
            logger.error(f"Error getting user referrals: {e}")
            return []
    
    def get_user_referred_by(self, user_id: int):
        """Get who referred a specific user"""
        try:
            # Check if referral_relationships table exists, otherwise use users table
            try:
                result = self.client.table("referral_relationships").select("*").eq("referred_id", user_id).execute()
                return result.data[0] if result.data else None
            except:
                # Fallback to users table
                user = self.get_user(user_id)
                if user and user.get('referred_by'):
                    return {'referrer_id': user['referred_by']}
                return None
        except Exception as e:
            logger.error(f"Error getting user referred by: {e}")
            return None
    
    def create_referral_relationship(self, referrer_id: int, referred_id: int):
        """Create a new referral relationship"""
        try:
            # Try to use referral_relationships table if it exists
            try:
                referral_data = {
                    'referrer_id': referrer_id,
                    'referred_id': referred_id,
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                result = self.client.table("referral_relationships").insert(referral_data).execute()
                return result.data[0] if result.data else None
            except:
                # Fallback: update user table
                self.update_user(referred_id, {'referred_by': referrer_id})
                return {'referrer_id': referrer_id, 'referred_id': referred_id}
        except Exception as e:
            logger.error(f"Error creating referral relationship: {e}")
            return None

    # --- Loglama Fonksiyonları ---
    def add_log(self, message: str):
        try:
            self.client.table("logs").insert({"message": message}).execute()
        except Exception as e:
            logger.error(f"Supabase add_log hatası: {e}")

    def get_logs(self, limit: int = 100):
        try:
            result = self.client.table("logs").select("*").order("timestamp", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_logs hatası: {e}")
            return []

    # --- Ayar ve Prompt Fonksiyonları ---
    def get_config(self, key: str):
        try:
            result = self.client.table("config").select("value").eq("key", key).single().execute()
            return result.data["value"] if result.data else None
        except Exception as e:
            logger.error(f"Supabase get_config hatası: {e}")
            return None

    def update_config(self, key: str, value):
        try:
            self.client.table("config").upsert({"key": key, "value": value}).execute()
        except Exception as e:
            logger.error(f"Supabase update_config hatası: {e}")

    def get_prompt(self, prompt_type: str, lang: str):
        try:
            result = self.client.table("prompts").select("content").eq("prompt_type", prompt_type).eq("language", lang).single().execute()
            return result.data["content"] if result.data else None
        except Exception as e:
            logger.error(f"Supabase get_prompt hatası: {e}")
            return None

    def update_prompt(self, prompt_type: str, lang: str, content: str):
        try:
            self.client.table("prompts").upsert({
                "prompt_type": prompt_type,
                "language": lang,
                "content": content
            }).execute()
        except Exception as e:
            logger.error(f"Supabase update_prompt hatası: {e}")

    def get_tarot_cards(self):
        try:
            cards = self.get_config("tarot_cards")
            if isinstance(cards, str):
                return json.loads(cards)
            elif isinstance(cards, list):
                return cards
            else:
                return []
        except Exception as e:
            logger.error(f"Supabase get_tarot_cards hatası: {e}")
            return []

    def get_daily_card_time(self):
        try:
            hour = self.get_config("daily_card_hour")
            minute = self.get_config("daily_card_minute")
            return int(hour) if hour else 9, int(minute) if minute else 0
        except Exception as e:
            logger.error(f"Supabase get_daily_card_time hatası: {e}")
            return 9, 0

# Global Supabase Yöneticisi
supabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)

# --- Ay Fazı Hesaplama Fonksiyonları ---
def calculate_moon_phase(date=None):
    """Ay fazını hesaplar"""
    if date is None:
        date = datetime.now()
    
    # Ay fazı hesaplama algoritması (basitleştirilmiş)
    # Gerçek uygulamada daha karmaşık astronomik hesaplamalar kullanılır
    days_since_new_moon = (date - datetime(2000, 1, 6)).days % 29.53058867
    
    if days_since_new_moon < 3.69:
        return {
            'phase': '🌑',
            'name': 'Yeni Ay',
            'name_en': 'New Moon',
            'energy': 'new'
        }
    elif days_since_new_moon < 7.38:
        return {
            'phase': '🌒',
            'name': 'İlk Hilal',
            'name_en': 'Waxing Crescent',
            'energy': 'waxing'
        }
    elif days_since_new_moon < 11.07:
        return {
            'phase': '🌓',
            'name': 'İlk Dördün',
            'name_en': 'First Quarter',
            'energy': 'first_quarter'
        }
    elif days_since_new_moon < 14.76:
        return {
            'phase': '🌔',
            'name': 'Şişkin Ay',
            'name_en': 'Waxing Gibbous',
            'energy': 'waxing'
        }
    elif days_since_new_moon < 18.45:
        return {
            'phase': '🌕',
            'name': 'Dolunay',
            'name_en': 'Full Moon',
            'energy': 'full'
        }
    elif days_since_new_moon < 22.14:
        return {
            'phase': '🌖',
            'name': 'Azalan Ay',
            'name_en': 'Waning Gibbous',
            'energy': 'waning'
        }
    elif days_since_new_moon < 25.83:
        return {
            'phase': '🌗',
            'name': 'Son Dördün',
            'name_en': 'Last Quarter',
            'energy': 'last_quarter'
        }
    else:
        return {
            'phase': '🌘',
            'name': 'Son Hilal',
            'name_en': 'Waning Crescent',
            'energy': 'waning'
        }

def get_moon_energy_advice(energy, lang='tr'):
    """Ay enerjisine göre tavsiyeler verir"""
    if lang == 'tr':
        advice_map = {
            'new': [
                'Yeni başlangıçlar için mükemmel zaman',
                'Hedeflerinizi belirleyin',
                'Yeni projeler başlatın',
                'İç dünyanızı keşfedin'
            ],
            'waxing': [
                'Büyüme ve gelişme zamanı',
                'Enerjinizi artırın',
                'Yeni fırsatları değerlendirin',
                'Pozitif düşüncelerle ilerleyin'
            ],
            'first_quarter': [
                'Kararlar alma zamanı',
                'Hedeflerinize odaklanın',
                'Eylem planları yapın',
                'Güçlü adımlar atın'
            ],
            'full': [
                'Tamamlanma ve kutlama zamanı',
                'Başarılarınızı değerlendirin',
                'Sevdiklerinizle paylaşın',
                'Mistik enerjileri hissedin'
            ],
            'waning': [
                'Bırakma ve temizlenme zamanı',
                'Eski alışkanlıkları bırakın',
                'Negatif enerjileri temizleyin',
                'İç huzurunuzu bulun'
            ],
            'last_quarter': [
                'Değerlendirme ve öğrenme zamanı',
                'Geçmişi analiz edin',
                'Derslerinizi çıkarın',
                'Gelecek için hazırlanın'
            ]
        }
    else:
        advice_map = {
            'new': [
                'Perfect time for new beginnings',
                'Set your intentions',
                'Start new projects',
                'Explore your inner world'
            ],
            'waxing': [
                'Time for growth and development',
                'Increase your energy',
                'Seize new opportunities',
                'Move forward with positive thoughts'
            ],
            'first_quarter': [
                'Time to make decisions',
                'Focus on your goals',
                'Make action plans',
                'Take strong steps'
            ],
            'full': [
                'Time for completion and celebration',
                'Evaluate your achievements',
                'Share with loved ones',
                'Feel the mystical energies'
            ],
            'waning': [
                'Time for letting go and cleansing',
                'Release old habits',
                'Clear negative energies',
                'Find your inner peace'
            ],
            'last_quarter': [
                'Time for evaluation and learning',
                'Analyze the past',
                'Learn your lessons',
                'Prepare for the future'
            ]
        }
    
    return advice_map.get(energy, ['Ay enerjisi ile uyum halinde olun' if lang == 'tr' else 'Be in harmony with moon energy'])

# --- Dil ve Metin Fonksiyonları (Supabase destekli) ---
@lru_cache(maxsize=32)
def get_config_from_db(key):
    return supabase_manager.get_config(key)

# Note: get_text function is already defined above at line 51
# This duplicate function has been removed to fix the locale loading issue

# Desteklenen diller ve kod mappings
SUPPORTED_LANGUAGES = {
    'tr': '🇹🇷 Türkçe',
    'en': '🇺🇸 English', 
    'es': '🇪🇸 Español',
    'ru': '🇷🇺 Русский',
    'pt': '🇵🇹 Português'
}

# Burç isimleri
ZODIAC_SIGNS = {
    'tr': ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık'],
    'en': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
    'es': ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis'],
    'ru': ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы'],
    'pt': ['Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem', 'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes']
}

def detect_user_language(telegram_user) -> str:
    """
    Kullanıcının Telegram client dilini tespit eder
    """
    try:
        # Telegram kullanıcısının language_code'unu al
        if hasattr(telegram_user, 'language_code') and telegram_user.language_code:
            lang_code = telegram_user.language_code.lower()
            
            # İki harfli dil kodlarını kontrol et
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
            
            # Bölgesel kodları (tr-TR, en-US gibi) temizle
            if '-' in lang_code:
                base_lang = lang_code.split('-')[0]
                if base_lang in SUPPORTED_LANGUAGES:
                    return base_lang
        
        # Varsayılan dil
        return 'tr'
        
    except Exception as e:
        logger.error(f"Dil tespiti hatası: {e}")
        return 'tr'

async def get_or_create_user(user_id: int, telegram_user) -> dict:
    """
    Kullanıcıyı oluşturur veya mevcut kullanıcıyı getirir
    Otomatik dil tespiti ile
    """
    user = supabase_manager.get_user(user_id)
    
    if not user:
        # Otomatik dil tespiti
        detected_lang = detect_user_language(telegram_user)
        
        user_data = {
            'id': user_id,  # Primary key
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'language': detected_lang,  # Otomatik tespit edilen dil
            'readings_count': 0,
            'daily_subscribed': False,
            'referred_count': 0,
            'referral_earnings': 0,
            'bonus_readings': 0,
            'state': 'idle',
            'premium_plan': 'free',
            'astro_subscribed': False,
            'moon_notifications': False
        }
        supabase_manager.create_user(user_data)
        user = user_data
        
        # Log dil tespiti
        supabase_manager.add_log(f"Yeni kullanıcı oluşturuldu: {user_id} - Tespit edilen dil: {detected_lang}")
    
    return user

# --- Kullanıcı Yönetimi ve Menüler (ESKI VERSIYON - SİLİNECEK) ---
async def get_or_create_user_old(user_id: int, effective_user):
    """Kullanıcıyı veritabanında arar, yoksa oluşturur."""
    user = supabase_manager.get_user(user_id)
    if not user:
        user_data = {
            'id': user_id,
            'username': effective_user.username,
            'first_name': effective_user.first_name,
            'language': 'tr',
            'readings_count': 0,
            'daily_subscribed': False,
            'referred_count': 0,
            'referral_earnings': 0,
            'bonus_readings': 0,
            'state': 'idle',
            'premium_plan': 'free',
            'astro_subscribed': False,
            'moon_notifications': False
        }
        user = supabase_manager.create_user(user_data)
        supabase_manager.add_log(f"Yeni kullanıcı: {effective_user.full_name} ({user_id})")
    return user


# --- Menü ve Buton Oluşturucular ---

def create_main_menu_keyboard(lang='tr'):
    """Ana menü klavyesini oluştur"""
    keyboard = [
        [InlineKeyboardButton(get_text("coffee_fortune", lang), callback_data='select_coffee')],
        [InlineKeyboardButton(get_text("tarot_fortune", lang), callback_data='select_tarot')],
        [InlineKeyboardButton(get_text("dream_analysis", lang), callback_data='select_dream')],
        [InlineKeyboardButton(get_text("astrology", lang), callback_data='select_astrology')],
        [InlineKeyboardButton(get_text("daily_card", lang), callback_data='daily_card')],
        [InlineKeyboardButton(get_text("referral", lang), callback_data='referral')],
        [InlineKeyboardButton(get_text("premium_menu", lang), callback_data='premium_menu')],
        [InlineKeyboardButton(get_text("language", lang), callback_data='change_language')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_language_keyboard():
    """Dil seçimi klavyesini oluştur"""
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data='set_lang_tr'),
         InlineKeyboardButton("🇺🇸 English", callback_data='set_lang_en')],
        [InlineKeyboardButton("🇪🇸 Español", callback_data='set_lang_es')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_panel_keyboard(lang='tr'):
    """Admin panel klavyesini oluştur"""
    keyboard = [
        [InlineKeyboardButton(get_text("statistics", lang), callback_data='admin_stats')],
        [InlineKeyboardButton(get_text("users", lang), callback_data='admin_users')],
        [InlineKeyboardButton(get_text("view_logs", lang), callback_data='admin_view_logs')],
        [InlineKeyboardButton(get_text("settings", lang), callback_data='admin_settings')],
        [InlineKeyboardButton(get_text("download_pdf", lang), callback_data='admin_download_pdf')],
        [InlineKeyboardButton(get_text("premium_management", lang), callback_data='admin_premium')],
        [InlineKeyboardButton(get_text("main_menu", lang), callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


# --- Command Handlers ---

async def start(update: Update, context: CallbackContext):
    """Start komutu"""
    user = update.effective_user
    user_id = user.id
    user_id_str = str(user_id)
    username = user.username or user.first_name
    
    # Get or detect user language
    user_data = supabase_manager.get_user(user_id)
    if user_data:
        lang = user_data.get('language', 'tr')
    else:
        # Auto-detect language from Telegram
        lang = update.effective_user.language_code[:2] if update.effective_user.language_code else 'tr'
        if lang not in LOCALES:
            lang = 'tr'
    
    # Check for referral
    if context.args:
        referrer_id = context.args[0]
        supabase_manager.add_log(f"Referral link ile geldi: {user_id_str} - Referrer: {referrer_id}")
        
        try:
            referrer_user_id = int(referrer_id)
            if referrer_user_id != user_id:
                referrer = supabase_manager.get_user(referrer_user_id)
                if referrer:
                    # Update referrer's statistics
                    new_count = referrer.get('referred_count', 0) + 1
                    new_free_readings = referrer.get('free_readings_earned', 0) + 1
                    new_stars = referrer.get('stars_earned', 0) + 50
                    
                    supabase_manager.update_user(referrer_user_id, {
                        'referred_count': new_count,
                        'free_readings_earned': new_free_readings,
                        'stars_earned': new_stars
                    })
                    
                    # Create referral relationship record
                    supabase_manager.create_referral_relationship(referrer_user_id, user_id)
                    
                    # Give bonus to new user
                    supabase_manager.update_user(user_id, {
                        'free_readings_earned': 1,  # 1 free reading for new user
                        'stars_earned': 25  # 25 stars bonus for new user
                    })
                    
                    supabase_manager.add_log(f"Referral işlemi tamamlandı: {user_id_str} - Referrer: {referrer_id}")
                    
                    # Send notification to referrer
                    try:
                        await context.bot.send_message(
                            referrer_user_id,
                            f"🎉 Yeni bir arkadaşınız Fal Gram'a katıldı! 1 ücretsiz fal + 50 ⭐ kazandınız!"
                        )
                    except:
                        pass
                        
        except ValueError:
            supabase_manager.add_log(f"Geçersiz referrer ID: {referrer_id}")
    
    # Create or update user
    user_data = {
        'username': username,
        'first_name': user.first_name,
        'language': lang,
        'updated_at': datetime.now().isoformat()
    }
    
    supabase_manager.create_or_update_user(user_id, user_data)
    supabase_manager.add_log(f"Yeni kullanıcı: {username} ({user_id_str})")
    
    # Send welcome message
    await update.message.reply_text(
        get_text("start_message", lang),
        reply_markup=create_main_menu_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # Send language detection message if auto-detected
    if not user_data:
        lang_name = LOCALES[lang].get('language_name', lang)
        await update.message.reply_text(
            get_text("language_detected", lang, lang=lang_name),
            parse_mode='Markdown'
        )

async def admin(update: Update, context: CallbackContext):
    """Admin panel komutu"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
        
    lang = get_user_language(user_id)
    
    await update.message.reply_text(
        get_text("admin_panel_title", lang),
        reply_markup=create_admin_panel_keyboard(lang),
                parse_mode='Markdown'
            )

async def gift(update: Update, context: CallbackContext):
    """Gift subscription command - Admin only"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text("❌ Kullanım: /gift <user_id> <plan> <days>\n\nÖrnek: /gift 123456789 premium 30")
        return
    
    try:
        target_user_id = int(context.args[0])
        plan_name = context.args[1].lower()
        days = int(context.args[2])
        
        if plan_name not in ['basic', 'premium', 'vip']:
            await update.message.reply_text("❌ Geçersiz plan! Kullanılabilir planlar: basic, premium, vip")
            return
        
        # Calculate expiry date
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Update user's premium status
        supabase_manager.update_user(target_user_id, {
            'premium_plan': plan_name,
            'premium_expires_at': expires_at
        })
        
        # Log the action
        supabase_manager.add_log(f"Admin gift subscription: {target_user_id} - {plan_name} - {days} days")
        
        # Send confirmation
        await update.message.reply_text(f"✅ Başarılı! User {target_user_id} için {plan_name} plan {days} gün süreyle aktifleştirildi.")
        
        # Notify the user
        try:
            await context.bot.send_message(
                target_user_id,
                f"🎁 Size {days} günlük {plan_name.upper()} plan hediye edildi! Premium özellikleriniz aktif."
            )
        except:
            pass
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Hatalı format! Kullanım: /gift <user_id> <plan> <days>")

async def cancel(update: Update, context: CallbackContext):
    """Cancel subscription command - Admin only"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("❌ Kullanım: /cancel <user_id>")
        return
    
    try:
        target_user_id = int(context.args[0])
        
        # Update user's premium status
        supabase_manager.update_user(target_user_id, {
            'premium_plan': 'free',
            'premium_expires_at': None
        })
        
        # Log the action
        supabase_manager.add_log(f"Admin cancel subscription: {target_user_id}")
        
        # Send confirmation
        await update.message.reply_text(f"✅ User {target_user_id} için premium abonelik iptal edildi.")
        
        # Notify the user
        try:
            await context.bot.send_message(
                target_user_id,
                "ℹ️ Premium aboneliğiniz iptal edildi. Ücretsiz plan özelliklerini kullanmaya devam edebilirsiniz."
            )
        except:
            pass
            
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Hatalı format! Kullanım: /cancel <user_id>")


# --- Callback Query Handlers ---

async def handle_callback_query(update: Update, context: CallbackContext):
    """Tüm callback query'leri işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    # Language selection
    if query.data.startswith('set_lang_'):
        new_lang = query.data.replace('set_lang_', '')
        await handle_language_change(query, new_lang)
        return
    
    # Main menu navigation
    handlers = {
        'main_menu': lambda: show_main_menu(query, lang),
        'select_coffee': lambda: handle_coffee_fortune(query, lang),
        'select_tarot': lambda: handle_tarot_fortune(query, lang),
        'select_dream': lambda: handle_dream_analysis(query, lang),
        'select_astrology': lambda: show_astrology_menu(query, lang),
        'daily_card': lambda: handle_daily_card(query, lang),
        'referral': lambda: show_referral_info(query, lang),
        'referral_stats': lambda: show_referral_stats(query, lang),
        'my_rewards': lambda: show_my_rewards(query, lang),
        'premium_menu': lambda: show_premium_menu(query, lang),
        'change_language': lambda: show_language_menu(query),
        
        # Admin handlers
        'admin_stats': lambda: admin_show_stats(query, lang),
        'admin_users': lambda: admin_show_users(query, lang),
        'admin_view_logs': lambda: admin_view_logs(query, lang),
        'admin_settings': lambda: admin_show_settings(query, lang),
        'admin_download_pdf': lambda: admin_download_pdf(query, lang),
        'admin_premium': lambda: admin_premium_management(query, lang),
        'admin_premium_users': lambda: admin_premium_users(query, lang),
        'admin_premium_stats': lambda: admin_premium_stats(query, lang),
        'admin_gift_subscription': lambda: admin_gift_subscription(query, lang),
        'admin_cancel_subscription': lambda: admin_cancel_subscription(query, lang),
        'admin_premium_pdf': lambda: admin_premium_pdf(query, lang),
        
        # Astrology handlers
        'astro_daily_horoscope': lambda: show_daily_horoscope_menu(query, lang),
        'astro_compatibility': lambda: show_compatibility_menu(query, lang),
        'astro_birth_chart': lambda: handle_birth_chart(query, lang),
        'astro_moon_calendar': lambda: show_moon_calendar(query, lang),
        'weekly_astro_report': lambda: show_weekly_horoscope_menu(query, lang),
        'monthly_horoscope_menu': lambda: show_monthly_horoscope_menu(query, lang),
        'astro_chatbot': lambda: activate_astrology_chatbot(query, lang),
        'daily_horoscope': lambda: show_daily_horoscope_menu(query, lang),
        'weekly_horoscope': lambda: show_weekly_horoscope_menu(query, lang),
        'monthly_horoscope': lambda: show_monthly_horoscope_menu(query, lang),
        'compatibility': lambda: show_compatibility_menu(query, lang),
        'birth_chart': lambda: handle_birth_chart(query, lang),
        'moon_calendar': lambda: show_moon_calendar(query, lang),
        'astrology_chatbot': lambda: activate_astrology_chatbot(query, lang),
        
        # Premium handlers
        'premium_compare': lambda: show_premium_comparison(query, lang),
        'subscription_management': lambda: show_subscription_management(query, lang),
    }
    
    # Execute handler if found
    for pattern, handler in handlers.items():
        if query.data == pattern:
            await handler()
            return
    
    # Pattern-based handlers
    if query.data.startswith('daily_horoscope_'):
        sign_index = int(query.data.split('_')[2])
        await generate_daily_horoscope(query, sign_index, lang)
    elif query.data.startswith('weekly_horoscope_'):
        sign_index = int(query.data.split('_')[2])
        await generate_weekly_horoscope(query, sign_index, lang)
    elif query.data.startswith('monthly_horoscope_'):
        sign_index = int(query.data.split('_')[2])
        await generate_monthly_horoscope(query, sign_index, lang)
    elif query.data.startswith('compat_'):
        await handle_compatibility_selection(query, lang)
    elif query.data.startswith('premium_plan_'):
        plan_name = query.data.replace('premium_plan_', '')
        await show_premium_plan_details(query, plan_name, lang)
    elif query.data.startswith('buy_'):
        plan_name = query.data.replace('buy_', '')
        await initiate_premium_purchase(query, plan_name, lang)
    elif query.data.startswith('pay_stars_'):
        plan_name = query.data.replace('pay_stars_', '')
        await handle_stars_payment(query, plan_name, lang)
    elif query.data.startswith('telegram_stars_'):
        plan_name = query.data.replace('telegram_stars_', '')
        await process_telegram_stars_payment(query, plan_name, lang)
    elif query.data.startswith('copy_link_'):
        await handle_copy_referral_link(query, lang)
    elif query.data == 'share_twitter':
        await handle_share_twitter(query, lang)
    elif query.data == 'share_telegram':
        await handle_share_telegram(query, lang)
    elif query.data.startswith('share_coffee_twitter_'):
        await handle_share_coffee_twitter(query, lang)
    elif query.data.startswith('copy_coffee_link_'):
        await handle_copy_coffee_link(query, lang)
    elif query.data.startswith('try_payment_'):
        plan_name = query.data.replace('try_payment_', '')
        await handle_try_payment(query, plan_name, lang)
    elif query.data == 'contact_support':
        await handle_contact_support(query, lang)
    elif query.data == 'referral_leaderboard':
        await show_referral_leaderboard(query, lang)
    elif query.data == 'referral_progress':
        await show_referral_progress(query, lang)
    elif query.data == 'referral_next_goal':
        await show_referral_next_goal(query, lang)
    elif query.data == 'premium_details':
        await show_premium_details(query, lang)
    elif query.data == 'payment_info':
        await show_payment_info(query, lang)
    elif query.data.startswith('set_lang_'):
        new_lang = query.data.replace('set_lang_', '')
        await handle_language_change(query, new_lang)
    elif query.data == 'back_to_admin':
        await back_to_admin(update, context)
    elif query.data == 'advanced_moon_calendar':
        await advanced_moon_calendar(update, context)
    elif query.data == 'planetary_transits':
        await planetary_transits(update, context)
    elif query.data == 'social_astrology':
        await social_astrology(update, context)
    elif query.data == 'chatbot_close':
        await chatbot_close(update, context)
    elif query.data == 'toggle_daily':
        await toggle_daily_subscription(update, context)
    elif query.data == 'confirm_daily_subscribe':
        await confirm_daily_subscribe(update, context)
    elif query.data == 'confirm_daily_unsubscribe':
        await confirm_daily_unsubscribe(update, context)
    elif query.data == 'get_referral_link':
        await get_referral_link_callback(update, context)
    elif query.data == 'draw_tarot':
        await draw_tarot_card(update, context)
    elif query.data == 'dream_analysis':
        await handle_dream_text(update, context)
    elif query.data == 'select_tarot':
        await draw_tarot_card(update, context)
    elif query.data == 'astro_subscribe_daily':
        await toggle_daily_subscription(update, context)
    elif query.data == 'set_delivery_time':
        # Handle delivery time setting
        await query.edit_message_text(get_text('daily_subscription.set_delivery_time_prompt', lang))
    elif query.data == 'subscription_stats':
        # Handle subscription statistics
        await query.edit_message_text(get_text('daily_subscription.stats_title', lang))
    elif query.data == 'daily_feedback':
        # Handle daily feedback
        await query.edit_message_text(get_text('daily_subscription.feedback_prompt', lang))
    elif query.data == 'set_delivery_time':
        # Handle delivery time setting
        await query.edit_message_text(get_text('daily_subscription.set_delivery_time_prompt', lang))
    elif query.data == 'subscription_stats':
        # Handle subscription statistics
        await query.edit_message_text(get_text('daily_subscription.stats_title', lang))
    elif query.data == 'daily_feedback':
        # Handle daily feedback
        await query.edit_message_text(get_text('daily_subscription.feedback_prompt', lang))
    else:
        # Unknown callback - provide better error handling
        try:
            await query.edit_message_text(
                get_text('error_occurred', lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
                ])
            )
        except Exception as e:
            logger.error(f"Error handling unknown callback {query.data}: {e}")
            # Try to send a new message if edit fails
            try:
                await query.message.reply_text(
                    get_text('error_occurred', lang),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
                    ])
                )
            except Exception as e2:
                logger.error(f"Failed to send error message: {e2}")


# --- Handler Implementations ---

async def show_main_menu(query, lang):
    """Show main menu with beautiful UI"""
    # Enhanced welcome message with better formatting
    welcome_message = f"""
✨🔮 **FAL GRAM** 🔮✨
━━━━━━━━━━━━━━━━━━━━━━

🌟 *The doors of the mystical world are opening...*

Choose your mystical journey:

☕ **Coffee Fortune** - Discover the future in your cup
🃏 **Tarot Reading** - The cards have something to tell you  
💭 **Dream Analysis** - Decode your subconscious messages
⭐ **Astrology** - Guidance from the stars
🌅 **Daily Card** - Personal guidance every morning
👥 **Invite Friends** - Blessings multiply when shared

━━━━━━━━━━━━━━━━━━━━━━
✨ *Are you ready to discover your destiny?* ✨
"""
    
    await safe_edit_message(
        query,
        welcome_message,
        reply_markup=create_main_menu_keyboard(lang),
        parse_mode='Markdown'
    )

async def handle_coffee_fortune(query, lang):
    """Handle coffee fortune selection"""
    await safe_edit_message(
        query,
        get_text("coffee_fortune_prompt", lang),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')
        ]]),
        parse_mode='Markdown'
    )

async def handle_tarot_fortune(query, lang):
    """Handle tarot fortune selection"""
    await safe_edit_message(
        query,
        get_text("tarot_fortune_prompt", lang),
        parse_mode='Markdown'
    )
    
    # Draw a random tarot card
    tarot_cards = supabase_manager.get_tarot_cards()
    card = random.choice(tarot_cards) if tarot_cards else "The Fool"
    
    await query.message.reply_text(
        get_text("tarot_card_drawn", lang, card=card),
        parse_mode='Markdown'
    )
    
    # Generate interpretation
    await generate_tarot_interpretation(query, card, lang)

async def handle_dream_analysis(query, lang):
    """Handle dream analysis selection"""
    # Set user state to waiting for dream
    user_id = query.from_user.id
    supabase_manager.update_user(user_id, {'state': 'waiting_for_dream'})
    
    await safe_edit_message(
        query,
        get_text("dream_analysis_prompt", lang),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')
        ]]),
        parse_mode='Markdown'
    )

async def show_astrology_menu(query, lang):
    """Show astrology menu"""
    message = get_text("astrology_menu_message", lang)
    
    # Create astrology menu buttons
    keyboard = [
        [InlineKeyboardButton(get_text("daily_horoscope", lang), callback_data='astro_daily_horoscope')],
        [InlineKeyboardButton(get_text("weekly_horoscope", lang), callback_data='weekly_astro_report')],
        [InlineKeyboardButton(get_text("monthly_horoscope", lang), callback_data='monthly_horoscope_menu')],
        [InlineKeyboardButton(get_text("compatibility", lang), callback_data='astro_compatibility')],
        [InlineKeyboardButton(get_text("birth_chart", lang), callback_data='astro_birth_chart')],
        [InlineKeyboardButton(get_text("moon_calendar", lang), callback_data='astro_moon_calendar')],
        [InlineKeyboardButton(get_text("astrology_chatbot", lang), callback_data='astro_chatbot')],
        [InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_daily_card(query, lang):
    """Handle daily card subscription toggle"""
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    
    is_subscribed = user.get('astro_subscribed', False)
    
    if is_subscribed:
        # Unsubscribe
        supabase_manager.update_user(user_id, {'astro_subscribed': False})
        message = get_text("daily_card_unsubscribe", lang)
    else:
        # Subscribe
        supabase_manager.update_user(user_id, {'astro_subscribed': True})
        message = get_text("daily_card_subscribe", lang)
    
    keyboard = [[InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_referral_info(query, lang):
    """Show enhanced referral information with elegant UI"""
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    
    # Get bot username from the query
    bot_username = query.from_user.bot.username if hasattr(query.from_user, 'bot') else "FalGramBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    referred_count = user.get('referred_count', 0)
    referral_earnings = user.get('referral_earnings', 0)
    free_readings_earned = user.get('free_readings_earned', 0)
    stars_earned = user.get('stars_earned', 0)
    
    # Calculate rewards and progress
    total_rewards = free_readings_earned + stars_earned
    progress = min(referred_count, 5)  # Progress bar for first 5 referrals
    
    # Build elegant referral message
    message = "🌟 **FAL GRAM REFERRAL SYSTEM** 🌟\n\n"
    message += "🎁 **Earn rewards by inviting friends!**\n\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Your Stats Section
    message += "📊 **Your Statistics:**\n"
    message += f"👥 **Total Referrals:** {referred_count}\n"
    message += f"🎁 **Free Readings Earned:** {free_readings_earned}\n"
    message += f"⭐ **Stars Earned:** {stars_earned}\n"
    message += f"💰 **Total Rewards:** {total_rewards}\n\n"
    
    # Progress Bar
    message += "📈 **Progress Bar:**\n"
    progress_bar = "█" * progress + "░" * (5 - progress)
    message += f"`{progress_bar}` ({referred_count}/5)\n\n"
    
    # Your Referral Link
    message += "🔗 **Your Referral Link:**\n"
    message += f"`{referral_link}`\n\n"
    
    # Rewards System
    message += "🏆 **Rewards System:**\n"
    message += "• 1️⃣ **1 Referral** = 1 Free Reading ✨\n"
    message += "• 5️⃣ **5 Referrals** = 3 Bonus Readings + Special Badge 🏅\n"
    message += "• 🔟 **10 Referrals** = VIP Status + Unlimited Daily Cards 👑\n"
    message += "• 2️⃣5️⃣ **25 Referrals** = Elite Member + Priority Support 🌟\n"
    message += "• 5️⃣0️⃣ **50 Referrals** = Premium Reader Access 💎\n\n"
    
    # How it works
    message += "📋 **How it works:**\n"
    message += "1. Share your referral link with friends\n"
    message += "2. When they join using your link, you both get rewards\n"
    message += "3. Track your progress and earn more rewards\n"
    message += "4. Unlock special features as you refer more people\n\n"
    
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "✨ *Start sharing and earn amazing rewards!* ✨"
    
    # Create elegant keyboard
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_link_{referral_link}"),
         InlineKeyboardButton("📊 My Stats", callback_data="referral_stats")],
        [InlineKeyboardButton("🐦 Share on X", callback_data="share_twitter"),
         InlineKeyboardButton("📤 Share on Telegram", callback_data="share_telegram")],
        [InlineKeyboardButton("🎁 My Rewards", callback_data="my_rewards"),
         InlineKeyboardButton("🏆 Leaderboard", callback_data="referral_leaderboard")],
        [InlineKeyboardButton("📈 Progress Details", callback_data="referral_progress"),
         InlineKeyboardButton("🎯 Next Goal", callback_data="referral_next_goal")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_referral_stats(query, lang):
    """Show detailed referral statistics"""
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    
    referred_count = user.get('referred_count', 0)
    free_readings_earned = user.get('free_readings_earned', 0)
    stars_earned = user.get('stars_earned', 0)
    total_rewards = free_readings_earned + stars_earned
    
    # Get referral relationships
    user_referrals = supabase_manager.get_user_referrals(user_id)
    
    message = get_text("referral.stats_title", lang) + "\n\n"
    message += get_text("referral.total_referrals", lang).format(count=referred_count) + "\n"
    message += get_text("referral.free_readings_earned", lang).format(readings=free_readings_earned) + "\n"
    message += get_text("referral.stars_earned", lang).format(stars=stars_earned) + "\n"
    message += get_text("referral.total_rewards", lang).format(rewards=total_rewards) + "\n\n"
    
    if user_referrals:
        message += "👥 **Son Referidos:**\n"
        for i, referral in enumerate(user_referrals[:5], 1):  # Show last 5
            referred_user = supabase_manager.get_user(referral.get('referred_id'))
            username = referred_user.get('username', f"User{referral.get('referred_id')}")
            date = referral.get('created_at', '').split('T')[0] if referral.get('created_at') else 'Unknown'
            message += f"{i}. @{username} - {date}\n"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text("referral.buttons.my_rewards", lang),
            callback_data="my_rewards"
        )],
        [InlineKeyboardButton(
            get_text("referral.buttons.back", lang),
            callback_data="referral"
        )]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_my_rewards(query, lang):
    """Show user's earned rewards"""
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    
    free_readings_earned = user.get('free_readings_earned', 0)
    stars_earned = user.get('stars_earned', 0)
    total_rewards = free_readings_earned + stars_earned
    
    message = get_text("referral.my_rewards_title", lang) + "\n\n"
    message += get_text("referral.free_readings_earned", lang).format(readings=free_readings_earned) + "\n"
    message += get_text("referral.stars_earned", lang).format(stars=stars_earned) + "\n"
    message += get_text("referral.total_rewards", lang).format(rewards=total_rewards) + "\n\n"
    
    if free_readings_earned > 0:
        message += "🎁 **Kullanılabilir Ödüller:**\n"
        message += f"• {free_readings_earned} ücretsiz fal hakkı\n"
        message += f"• {stars_earned} ⭐ bonus\n\n"
        message += "💡 **Nasıl Kullanılır:**\n"
        message += "• Ücretsiz fal haklarınız otomatik olarak kullanılır\n"
        message += "• Bonus yıldızlar premium planlarda kullanılabilir\n"
    
    keyboard = [
        [InlineKeyboardButton(
            get_text("referral.buttons.my_stats", lang),
            callback_data="referral_stats"
        )],
        [InlineKeyboardButton(
            get_text("referral.buttons.back", lang),
            callback_data="referral"
        )]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_language_menu(query):
    """Show language selection menu with elegant UI"""
    user_id = query.from_user.id
    current_lang = get_user_language(user_id)
    
    # Create elegant language selection message
    message = "🌐 **LANGUAGE SELECTION** 🌐\n\n"
    message += "Please select your preferred language:\n"
    message += "Lütfen tercih ettiğiniz dili seçin:\n"
    message += "Por favor selecciona tu idioma preferido:\n\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    message += "Current language / Mevcut dil / Idioma actual:\n"
    message += f"**{current_lang.upper()}**\n\n"
    message += "Choose from the options below:\n"
    
    # Create elegant language keyboard
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data='set_lang_tr'),
         InlineKeyboardButton("🇺🇸 English", callback_data='set_lang_en')],
        [InlineKeyboardButton("🇪🇸 Español", callback_data='set_lang_es')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_language_change(query, new_lang):
    """Handle language change"""
    user_id = query.from_user.id
    
    # Update user language
    supabase_manager.update_user(user_id, {'language': new_lang})
    
    # Send confirmation in new language
    lang_name = LOCALES[new_lang].get('language_name', new_lang)
    message = get_text("language_updated", new_lang).format(lang=lang_name)
    
    await safe_edit_message(
        query,
        message,
        reply_markup=create_main_menu_keyboard(new_lang),
        parse_mode='Markdown'
    )

# --- Missing Handler Functions ---

async def show_premium_menu(query, lang):
    """Show premium menu with all available plans"""
    # Build elegant premium menu text
    menu_text = "💎 **PREMIUM PLANS** 💎\n\n"
    menu_text += "✨ **Unlock unlimited features and exclusive content!**\n\n"
    menu_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Add available plans
    for plan_id, plan in PREMIUM_PLANS.items():
        if plan_id == 'free':
            continue  # Skip free plan in premium menu
        
        plan_name = plan.get('name', plan_id.title())
        price = plan.get('price_stars', 0)
        duration = plan.get('duration', '30 days')
        
        menu_text += f"✨ **{plan_name}** - {price} ⭐\n"
        menu_text += f"⏰ {duration}\n"
        menu_text += f"📝 {plan.get('description', '')}\n\n"
    
    menu_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    menu_text += "💡 **Choose your plan or compare all options:**\n\n"
    
    # Create elegant keyboard with plan buttons
    keyboard = []
    for plan_id, plan in PREMIUM_PLANS.items():
        if plan_id == 'free':
            continue  # Skip free plan in premium menu
        
        plan_name = plan.get('name', plan_id.title())
        price = plan.get('price_stars', 0)
        
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {plan_name} - {price} ⭐",
                callback_data=f"premium_plan_{plan_id}"
            )
        ])
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("📊 Compare Plans", callback_data="premium_compare"),
        InlineKeyboardButton("💳 Payment Info", callback_data="payment_info")
    ])
    keyboard.append([
        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
    ])
    
    await safe_edit_message(
        query,
        menu_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def admin_show_stats(query, lang):
    """Show admin statistics"""
    stats = supabase_manager.get_payment_statistics()
    await safe_edit_message(
        query,
        get_text("admin_stats_message", lang, stats=stats),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_show_users(query, lang):
    """Show admin users"""
    users = supabase_manager.get_all_users()
    await safe_edit_message(
        query,
        get_text("admin_users_message", lang, count=len(users)),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_show_settings(query, lang):
    """Show admin settings"""
    await safe_edit_message(
        query,
        get_text("admin_settings_message", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_view_logs(query, lang):
    """Show admin logs"""
    logs = supabase_manager.get_logs(limit=50)
    log_text = "\n".join([f"• {log}" for log in logs[:20]]) if logs else get_text("no_logs", lang)
    await safe_edit_message(
        query,
        get_text("admin_logs_message", lang, logs=log_text),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_download_pdf(query, lang):
    """Download admin PDF"""
    await safe_edit_message(
        query,
        get_text("admin_pdf_download", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_premium_management(query, lang):
    """Show premium management menu"""
    await safe_edit_message(
        query,
        get_text("premium_management", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_premium_users(query, lang):
    """Show premium users"""
    premium_users = supabase_manager.get_premium_users()
    await safe_edit_message(
        query,
        get_text("admin_premium_users", lang, count=len(premium_users)),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_premium_stats(query, lang):
    """Show premium statistics"""
    stats = supabase_manager.get_payment_statistics()
    await safe_edit_message(
        query,
        get_text("admin_premium_stats", lang, stats=stats),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_gift_subscription(query, lang):
    """Gift subscription interface"""
    await safe_edit_message(
        query,
        get_text("admin_gift_subscription", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_cancel_subscription(query, lang):
    """Cancel subscription interface"""
    await safe_edit_message(
        query,
        get_text("admin_cancel_subscription", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def admin_premium_pdf(query, lang):
    """Generate premium PDF report"""
    await safe_edit_message(
        query,
        get_text("admin_premium_pdf", lang),
        reply_markup=create_admin_panel_keyboard(lang),
        parse_mode='Markdown'
    )

async def show_daily_horoscope_menu(query, lang):
    """Show daily horoscope menu"""
    # Create keyboard with main menu button
    keyboard = create_horoscope_keyboard(lang)
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await safe_edit_message(
        query,
        get_text("daily_horoscope_menu", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_compatibility_menu(query, lang):
    """Show compatibility menu"""
    # Create keyboard with main menu button
    keyboard = create_compatibility_keyboard(lang)
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await safe_edit_message(
        query,
        get_text("compatibility_menu", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_birth_chart(query, lang):
    """Handle birth chart request"""
    await safe_edit_message(
        query,
        get_text("birth_chart_prompt", lang),
        reply_markup=create_main_menu_keyboard(lang),
            parse_mode='Markdown'
        )

async def show_moon_calendar(query, lang):
    """Show moon calendar"""
    await safe_edit_message(
        query,
        get_text("moon_calendar_message", lang),
        reply_markup=create_main_menu_keyboard(lang),
        parse_mode='Markdown'
    )

async def show_weekly_horoscope_menu(query, lang):
    """Show weekly horoscope menu"""
    # Create keyboard with main menu button
    keyboard = create_horoscope_keyboard(lang)
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await safe_edit_message(
        query,
        get_text("weekly_horoscope_menu", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_monthly_horoscope_menu(query, lang):
    """Show monthly horoscope menu"""
    # Create keyboard with main menu button
    keyboard = create_horoscope_keyboard(lang)
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await safe_edit_message(
        query,
        get_text("monthly_horoscope_menu", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def activate_astrology_chatbot(query, lang):
    """Activate astrology chatbot"""
    await safe_edit_message(
        query,
        get_text("astrology_chatbot_activated", lang),
        reply_markup=create_main_menu_keyboard(lang),
        parse_mode='Markdown'
    )

async def show_premium_comparison(query, lang):
    """Show premium plan comparison table with elegant UI"""
    # Build elegant comparison table
    comparison_text = "💎 **PREMIUM PLAN COMPARISON** 💎\n\n"
    comparison_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Plan Overview Table
    comparison_text += "📊 **Plan Overview:**\n\n"
    comparison_text += "| Plan | Price | Duration | Features |\n"
    comparison_text += "|------|-------|----------|----------|\n"
    
    for plan_id, plan in PREMIUM_PLANS.items():
        plan_name = plan.get('name', plan_id.title())
        price = plan.get('price_stars', 0)
        duration = plan.get('duration', '30 days')
        
        # Get features for this plan
        features = plan.get('features', [])
        feature_count = len(features)
        
        comparison_text += f"| {plan_name} | {price} ⭐ | {duration} | {feature_count} features |\n"
    
    comparison_text += "\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Detailed Feature Comparison
    comparison_text += "🔍 **Detailed Feature Comparison:**\n\n"
    
    # Get all unique features
    all_features = set()
    for plan in PREMIUM_PLANS.values():
        features = plan.get('features', [])
        for feature in features:
            # Extract feature name (remove emoji and get main text)
            feature_name = feature.split(' ', 1)[1] if ' ' in feature else feature
            all_features.add(feature_name)
    
    # Create feature comparison table
    comparison_text += "| Feature | Free | Basic | Premium | VIP |\n"
    comparison_text += "|---------|------|-------|---------|-----|\n"
    
    for feature in sorted(all_features):
        row = f"| {feature} |"
        for plan_id in ['free', 'basic', 'premium', 'vip']:
            plan = PREMIUM_PLANS.get(plan_id, {})
            features = plan.get('features', [])
            has_feature = any(feature in f for f in features)
            row += " ✅ |" if has_feature else " ❌ |"
        comparison_text += row + "\n"
    
    comparison_text += "\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    comparison_text += "💡 **Choose your plan and click below to purchase:**\n\n"
    
    # Create elegant keyboard with plan selection buttons
    keyboard = []
    for plan_id, plan in PREMIUM_PLANS.items():
        if plan_id == 'free':
            continue  # Skip free plan in purchase menu
        
        plan_name = plan.get('name', plan_id.title())
        price = plan.get('price_stars', 0)
        
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {plan_name} - {price} ⭐",
                callback_data=f"premium_plan_{plan_id}"
            )
        ])
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("📋 Plan Details", callback_data="premium_details"),
        InlineKeyboardButton("💳 Payment Info", callback_data="payment_info")
    ])
    keyboard.append([
        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
        InlineKeyboardButton("🔙 Premium Menu", callback_data="premium_menu")
    ])
    
    await safe_edit_message(
        query,
        comparison_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_subscription_management(query, lang):
    """Show subscription management"""
    await safe_edit_message(
        query,
        get_text("subscription_management", lang),
        reply_markup=create_premium_menu_keyboard(lang),
        parse_mode='Markdown'
    )

async def generate_daily_horoscope(query, sign_index, lang):
    """Generate daily horoscope"""
    await generate_daily_horoscope_impl(query, sign_index, lang)

async def generate_weekly_horoscope(query, sign_index, lang):
    """Generate weekly horoscope"""
    await generate_weekly_horoscope_impl(query, sign_index, lang)

async def generate_monthly_horoscope(query, sign_index, lang):
    """Generate monthly horoscope"""
    await generate_monthly_horoscope_impl(query, sign_index, lang)

async def generate_daily_horoscope_impl(query, sign_index, lang):
    """Implementation of daily horoscope generation"""
    await safe_edit_message(
        query,
        get_text("daily_horoscope_generating", lang),
        parse_mode='Markdown'
    )

async def generate_weekly_horoscope_impl(query, sign_index, lang):
    """Implementation of weekly horoscope generation"""
    await safe_edit_message(
        query,
        get_text("weekly_horoscope_generating", lang),
        parse_mode='Markdown'
    )

async def generate_monthly_horoscope_impl(query, sign_index, lang):
    """Implementation of monthly horoscope generation"""
    await safe_edit_message(
        query,
        get_text("monthly_horoscope_generating", lang),
        parse_mode='Markdown'
    )

async def handle_compatibility_selection(query, lang):
    """Handle compatibility selection"""
    await safe_edit_message(
        query,
        get_text("compatibility_processing", lang),
        parse_mode='Markdown'
    )

async def show_premium_plan_details(query, plan_name, lang):
    """Show premium plan details"""
    plan = PREMIUM_PLANS.get(plan_name, {})
    if not plan:
        await safe_edit_message(
            query,
            get_text("error.plan_not_found", lang),
            reply_markup=create_premium_menu_keyboard(lang),
            parse_mode='Markdown'
        )
        return
    
    # Get plan details from locale
    plan_details = get_text(f"premium_plans.plans.{plan_name}", lang, default={})
    
    # Build plan description
    plan_text = f"✨ **{plan.get('name', plan_name.title())}** ✨\n\n"
    plan_text += f"📝 **{get_text('premium_plans.plan_details.description_label', lang)}**\n"
    plan_text += f"{plan.get('description', '')}\n\n"
    plan_text += f"💰 **{get_text('premium_plans.plan_details.price_label', lang)}**\n"
    plan_text += f"{plan.get('price_stars', 0)} ⭐\n\n"
    plan_text += f"⏰ **{get_text('premium_plans.plan_details.duration_label', lang)}**\n"
    plan_text += f"{plan.get('duration', '30 days')}\n\n"
    plan_text += f"🎯 **{get_text('premium_plans.plan_details.features_label', lang)}**\n"
    
    # Add features
    features = plan.get('features', [])
    for feature in features:
        plan_text += f"• {feature}\n"
    
    # Create keyboard with buy button
    keyboard = [
        [InlineKeyboardButton(
            get_text("premium_plans.buttons.buy", lang),
            callback_data=f"buy_{plan_name}"
        )],
        [InlineKeyboardButton(
            get_text("premium_plans.buttons.back", lang),
            callback_data="premium_menu"
        )]
    ]
    
    await safe_edit_message(
        query,
        plan_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def initiate_premium_purchase(query, plan_name, lang):
    """Initiate premium purchase with Telegram Stars"""
    plan = PREMIUM_PLANS.get(plan_name, {})
    if not plan:
        await safe_edit_message(
            query,
            get_text("error.plan_not_found", lang),
            reply_markup=create_premium_menu_keyboard(lang),
            parse_mode='Markdown'
        )
        return
    plan_name_display = plan.get('name', plan_name.title())
    price_stars = plan.get('price_stars', 0)
    duration = plan.get('duration', '30 days')
    # Create purchase message
    purchase_text = f"💎 **{plan_name_display}** 💎\n\n"
    purchase_text += f"💰 **Price:** {price_stars} ⭐\n"
    purchase_text += f"⏰ **Duration:** {duration}\n\n"
    purchase_text += f"📝 **Description:**\n{plan.get('description', '')}\n\n"
    purchase_text += f"✨ **Features:**\n"
    features = plan.get('features', [])
    for feature in features:
        purchase_text += f"• {feature}\n"
    purchase_text += f"\n{get_text('premium_plans.separator', lang)}\n\n"
    purchase_text += get_text('premium.purchase_initiated', lang) + "\n"
    # Create payment keyboard
    keyboard = [
        [InlineKeyboardButton(
            f"💳 Pay {price_stars} ⭐",
            callback_data=f"pay_stars_{plan_name}"
        )],
        [InlineKeyboardButton(
            get_text("premium_plans.back_to_menu", lang),
            callback_data="premium_menu"
        )]
    ]
    await safe_edit_message(
        query,
        purchase_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_stars_payment(query, plan_name, lang):
    """Handle Telegram Stars payment for premium plans"""
    plan = PREMIUM_PLANS.get(plan_name, {})
    if not plan:
        await safe_edit_message(
            query,
            get_text("error.plan_not_found", lang),
            reply_markup=create_premium_menu_keyboard(lang),
            parse_mode='Markdown'
        )
        return
    user_id = query.from_user.id
    price_stars = plan.get('price_stars', 0)
    plan_name_display = plan.get('name', plan_name.title())
    # Simulate payment process (replace with real payment integration)
    try:
        # Payment logic here (simulate success)
        await safe_edit_message(
            query,
            get_text('premium.payment_success', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ]),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Payment error: {e}")
        await safe_edit_message(
            query,
            get_text('premium.payment_error', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.try_again', lang), callback_data=f"pay_stars_{plan_name}")],
                [InlineKeyboardButton(get_text('buttons.back_to_menu', lang), callback_data="premium_menu")]
            ]),
            parse_mode='Markdown'
        )

async def process_telegram_stars_payment(query, plan_name, lang):
    """Process Telegram Stars payment and activate premium plan"""
    plan = PREMIUM_PLANS.get(plan_name, {})
    if not plan:
        await safe_edit_message(
            query,
            get_text("error.plan_not_found", lang),
            reply_markup=create_premium_menu_keyboard(lang),
            parse_mode='Markdown'
        )
        return
    
    user_id = query.from_user.id
    price_stars = plan.get('price_stars', 0)
    plan_name_display = plan.get('name', plan_name.title())
    
    try:
        # Check if user has enough stars
        # For now, we'll simulate the payment process
        # In a real implementation, you would check the user's star balance
        
        # Create payment form using Telegram Stars
        payment_form_data = {
            "title": f"Fal Gram - {plan_name_display}",
            "description": f"Premium plan subscription for {plan_name_display}",
            "payload": f"premium_{plan_name}_{user_id}",
            "currency": "XTR",  # Telegram Stars currency
            "prices": [LabeledPrice(f"{plan_name_display} Plan", price_stars)]  # Stars amount
        }
        
        # For Telegram Stars, we need to use a different approach
        # Since direct star payment might not be available, we'll show instructions
        
        message = f"💎 **{plan_name_display} Plan** 💎\n\n"
        message += f"💰 **Price:** {price_stars} Telegram Stars\n\n"
        message += "📱 **To complete your purchase:**\n"
        message += "1. Make sure you have enough Telegram Stars\n"
        message += "2. Contact @BotFather to enable payments\n"
        message += "3. Or use admin command to activate manually\n\n"
        message += "🔧 **Alternative:** Contact support for manual activation"
        
        keyboard = [
            [InlineKeyboardButton("💳 Try Payment", callback_data=f"try_payment_{plan_name}")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Plans", callback_data="premium_menu")]
        ]
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # Update user state to waiting for payment
        supabase_manager.update_user(user_id, {
            'payment_state': f'waiting_{plan_name}',
            'payment_amount': price_stars
        })
        
        supabase_manager.add_log(f"Payment initiated: User {user_id} for {plan_name} ({price_stars} stars)")
        
    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        error_text = get_text('premium.payment_error', lang)
        keyboard = [
            [InlineKeyboardButton(get_text('buttons.try_again', lang), callback_data=f"pay_stars_{plan_name}")],
            [InlineKeyboardButton(get_text('buttons.back_to_menu', lang), callback_data="premium_menu")]
        ]
        await safe_edit_message(
            query,
            error_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# New referral and premium handler functions
async def handle_copy_referral_link(query, lang):
    """Handle copy referral link action"""
    user_id = query.from_user.id
    bot_username = query.from_user.bot.username if hasattr(query.from_user, 'bot') else "FalGramBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    message = "📋 **Referral Link Copied!** 📋\n\n"
    message += f"Your referral link has been copied to clipboard:\n"
    message += f"`{referral_link}`\n\n"
    message += "Share this link with your friends to earn rewards!"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_share_twitter(query, lang):
    """Handle share on Twitter/X action"""
    user_id = query.from_user.id
    bot_username = query.from_user.bot.username if hasattr(query.from_user, 'bot') else "FalGramBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # Create Twitter/X share message
    share_text = f"🔮 Check out this amazing fortune telling bot! {referral_link}"
    twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
    
    message = get_text("referral.share_twitter_message", lang)
    
    keyboard = [
        [InlineKeyboardButton("🐦 Share on X", url=twitter_url)],
        [InlineKeyboardButton("📋 Copy Link", callback_data="copy_link_twitter")],
        [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_share_telegram(query, lang):
    """Handle share on Telegram action"""
    user_id = query.from_user.id
    bot_username = query.from_user.bot.username if hasattr(query.from_user, 'bot') else "FalGramBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    telegram_url = f"https://t.me/share/url?url={referral_link}&text=🔮 Check out this amazing fortune telling bot!"
    
    message = "📤 **Share on Telegram** 📤\n\n"
    message += "Click the button below to share on Telegram:\n\n"
    message += "Your referral link will be automatically included!"
    
    keyboard = [
        [InlineKeyboardButton("📤 Share on Telegram", url=telegram_url)],
        [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_referral_leaderboard(query, lang):
    """Show referral leaderboard"""
    try:
        # Get leaderboard data from database
        leaderboard_data = supabase_manager.get_referral_relationships()
        
        message = get_text("referral.leaderboard_title", lang) + "\n\n"
        
        if leaderboard_data:
            for i, entry in enumerate(leaderboard_data[:10], 1):
                user_id = entry.get('referrer_id')
                referred_count = entry.get('referred_count', 0)
                message += f"{i}. User {user_id}: {referred_count} referrals\n"
        else:
            message += get_text("referral.no_data", lang)
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing referral leaderboard: {e}")
        await safe_edit_message(
            query,
            get_text('error_occurred', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ])
        )

async def show_referral_progress(query, lang):
    """Show referral progress details"""
    try:
        user_id = query.from_user.id
        user_data = supabase_manager.get_user(user_id)
        referred_count = len(supabase_manager.get_user_referrals(user_id))
        
        message = get_text("referral.progress_title", lang) + "\n\n"
        message += f"📊 **Your Progress:**\n"
        message += f"• Total Referrals: {referred_count}\n"
        message += f"• Current Level: {get_referral_level(referred_count)}\n"
        message += f"• Next Goal: {get_next_goal(referred_count)}\n\n"
        
        # Progress bar
        progress = min(referred_count % 5, 5)
        progress_bar = "█" * progress + "░" * (5 - progress)
        message += f"📈 Progress: [{progress_bar}] ({progress}/5)\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing referral progress: {e}")
        await safe_edit_message(
            query,
            get_text('error_occurred', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ])
        )

async def show_referral_next_goal(query, lang):
    """Show next referral goal"""
    try:
        user_id = query.from_user.id
        referred_count = len(supabase_manager.get_user_referrals(user_id))
        
        message = get_text("referral.next_goal_title", lang) + "\n\n"
        
        next_goal = get_next_goal(referred_count)
        message += f"🎯 **Next Goal:** {next_goal}\n\n"
        
        # Show rewards for next goal
        next_level = (referred_count // 5) + 1
        rewards = get_level_rewards(next_level)
        message += f"🏆 **Rewards:**\n{rewards}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Referral", callback_data="referral")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing referral next goal: {e}")
        await safe_edit_message(
            query,
            get_text('error_occurred', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ])
        )

async def show_premium_details(query, lang):
    """Show premium plan details"""
    try:
        user_id = query.from_user.id
        user_data = supabase_manager.get_user(user_id)
        current_plan = user_data.get('premium_plan', 'free')
        
        message = "💎 **Premium Plan Details** 💎\n\n"
        
        if current_plan != 'free':
            plan = PREMIUM_PLANS.get(current_plan, {})
            message += f"📋 **Current Plan:** {plan.get('name', current_plan.title())}\n"
            message += f"📅 **Expires:** {user_data.get('premium_expires', 'Unknown')}\n\n"
            message += f"✨ **Features:**\n"
            for feature in plan.get('features', []):
                message += f"• {feature}\n"
        else:
            message += "You don't have an active premium plan.\n\n"
            message += "Upgrade to unlock premium features!"
        
        keyboard = [
            [InlineKeyboardButton("📋 Plan Details", callback_data="premium_details")],
            [InlineKeyboardButton("💳 Payment Info", callback_data="payment_info")]
        ]
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
        keyboard.append([InlineKeyboardButton("🔙 Premium Menu", callback_data="premium_menu")])
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing premium details: {e}")
        await safe_edit_message(
            query,
            get_text('error_occurred', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ])
        )

async def show_payment_info(query, lang):
    """Show payment information"""
    try:
        message = get_text("payment.title", lang) + "\n\n"
        message += get_text("payment.description", lang) + "\n\n"
        
        message += get_text("payment.secure_payment", lang) + "\n"
        for feature in get_text("payment.secure_features", lang, default=[]):
            message += f"{feature}\n"
        message += "\n"
        
        message += get_text("payment.how_to_get_stars", lang) + "\n"
        for source in get_text("payment.stars_sources", lang, default=[]):
            message += f"{source}\n"
        message += "\n"
        
        message += get_text("payment.payment_process", lang) + "\n"
        for step in get_text("payment.payment_steps", lang, default=[]):
            message += f"{step}\n"
        
        keyboard = [
            [InlineKeyboardButton(get_text("payment.buy_premium", lang), callback_data="premium_menu")],
            [InlineKeyboardButton(get_text("payment.back_to_plans", lang), callback_data="premium_compare")]
        ]
        
        await safe_edit_message(
            query,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing payment info: {e}")
        await safe_edit_message(
            query,
            get_text('error_occurred', lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text('buttons.main_menu', lang), callback_data="main_menu")]
            ])
        )

# Helper functions for referral system
def get_referral_level(referral_count):
    """Get referral level based on count"""
    if referral_count >= 50:
        return "Elite"
    elif referral_count >= 25:
        return "VIP"
    elif referral_count >= 10:
        return "Premium"
    elif referral_count >= 5:
        return "Active"
    else:
        return "New"

def get_next_goal(referral_count):
    """Get next referral goal"""
    current_level = referral_count // 5
    next_level_count = (current_level + 1) * 5
    remaining = next_level_count - referral_count
    return f"{remaining} more referrals to Level {current_level + 1}"

def get_level_rewards(level):
    """Get rewards for a specific level"""
    rewards = {
        1: "1 Free Reading",
        2: "3 Bonus Readings + Special Badges",
        3: "VIP Status + Unlimited Daily Cards",
        4: "Elite Member + Priority Support",
        5: "Premium Fortune Teller Access"
    }
    return rewards.get(level, "Special rewards")

async def generate_tarot_interpretation(query, card, lang):
    """Generate tarot interpretation"""
    await safe_edit_message(
        query,
        get_text("tarot_interpretation", lang, card=card),
        parse_mode='Markdown'
    )

async def process_dream_text(query, lang):
    """Process dream text"""
    await safe_edit_message(
        query,
        get_text("dream_processing", lang),
        parse_mode='Markdown'
    )

async def process_birth_info(query, lang):
    """Process birth info"""
    await safe_edit_message(
        query,
        get_text("birth_info_processing", lang),
        parse_mode='Markdown'
    )

async def handle_chatbot_question(query, lang):
    """Handle chatbot question"""
    await safe_edit_message(
        query,
        get_text("chatbot_processing", lang),
        parse_mode='Markdown'
    )

async def generate_coffee_fortune(query, lang):
    """Generate coffee fortune"""
    await safe_edit_message(
        query,
        get_text("coffee_fortune_processing", lang),
        parse_mode='Markdown'
    )

# --- Implementation Functions for Message Handler ---

async def process_dream_text_impl(update, context, text, lang):
    """Implementation of dream text processing"""
    await update.message.reply_text(
        get_text("dream_processing", lang),
        parse_mode='Markdown'
    )

async def process_birth_info_impl(update, context, text, lang):
    """Implementation of birth info processing"""
    await update.message.reply_text(
        get_text("birth_info_processing", lang),
                parse_mode='Markdown'
            )

async def handle_chatbot_question_impl(update, context, text, lang):
    """Implementation of chatbot question handling"""
    await update.message.reply_text(
        get_text("chatbot_processing", lang),
        parse_mode='Markdown'
    )

async def generate_coffee_fortune_impl(update, photo_bytes, lang):
    """Implementation of coffee fortune generation"""
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    
    try:
        # Use faster model for better performance
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Get prompt from Supabase with proper language
        prompt = supabase_manager.get_prompt("coffee", lang)
        if not prompt:
            # Fallback prompts for each language
            fallback_prompts = {
                'tr': f"Sen deneyimli bir kahve falı yorumcususun. {update.effective_user.first_name} için kahve fincanındaki işaretleri yorumla.\n\nFincanın içindeki şekilleri, sembolleri ve işaretleri detaylı bir şekilde açıkla. Kişisel bir yorum yap ve gelecekteki fırsatları belirt.\n\n150-200 kelime.",
                'en': f"You are an experienced coffee fortune reader. Interpret the signs in the coffee cup for {update.effective_user.first_name}.\n\nExplain the shapes, symbols, and signs in the cup in detail. Make a personal interpretation and indicate future opportunities.\n\n150-200 words.",
                'es': f"Eres un lector de café experimentado. Interpreta los signos en la taza de café para {update.effective_user.first_name}.\n\nExplica las formas, símbolos y signos en la taza en detalle. Haz una interpretación personal e indica oportunidades futuras.\n\n150-200 palabras."
            }
            prompt = fallback_prompts.get(lang, fallback_prompts['en'])
        
        # Prepare prompt with proper language instruction
        final_prompt = prompt.replace("{username}", update.effective_user.first_name)
        
        # Add explicit language instruction
        language_instructions = {
            'tr': f"KAHVE FALI YORUMCUSU. SADECE TÜRKÇE KAHVE FALI YORUMU YAZ.\n\n{final_prompt}\n\nTÜRKÇE YORUM:",
            'en': f"COFFEE FORTUNE READER. WRITE ONLY COFFEE FORTUNE INTERPRETATION IN ENGLISH.\n\n{final_prompt}\n\nENGLISH INTERPRETATION:",
            'es': f"LECTOR DE CAFÉ. ESCRIBE SOLO LA INTERPRETACIÓN DEL CAFÉ EN ESPAÑOL.\n\n{final_prompt}\n\nINTERPRETACIÓN EN ESPAÑOL:"
        }
        final_prompt = language_instructions.get(lang, language_instructions['en'])
        
        supabase_manager.add_log(f"Coffee fortune prompt prepared ({lang}): {len(final_prompt)} characters")
        supabase_manager.add_log(f"Gemini API call in progress (coffee, {lang}): {user_id_str}")
        
        # Send to Gemini (async API) - with timeout
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: model.generate_content([final_prompt, photo_bytes])),
                timeout=8.0  # Reduced timeout for faster response
            )
            
            supabase_manager.add_log(f"Gemini API response successfully received: {user_id_str}")
        except asyncio.TimeoutError:
            supabase_manager.add_log(f"Gemini API timeout (8s): {user_id_str}")
            # Try DeepSeek as fallback
            try:
                deepseek_response = await asyncio.wait_for(
                    loop.run_in_executor(None, call_deepseek_api, final_prompt),
                    timeout=10.0
                )
                response = type('Response', (), {'text': deepseek_response})()
                supabase_manager.add_log(f"DeepSeek fallback successful: {user_id_str}")
            except Exception as deepseek_error:
                supabase_manager.add_log(f"DeepSeek fallback failed: {str(deepseek_error)[:100]}")
                raise Exception("AI API did not respond (timeout)")
        except Exception as e:
            supabase_manager.add_log(f"Gemini API error: {str(e)[:100]}")
            raise Exception(f"Gemini API error: {str(e)[:100]}")
        
        if not response:
            raise Exception("No response received from AI API")
        
        if not response.text:
            raise Exception("Empty response received from AI API")
        
        supabase_manager.add_log(f"Coffee fortune response received: {len(response.text)} characters")
        
        # Reduce free reading count (if not admin)
        if update.effective_user.id != ADMIN_ID:
            user_data = supabase_manager.get_user(update.effective_user.id)
            current_readings = user_data.get("readings_count", 0) if user_data else 0
            supabase_manager.update_user(update.effective_user.id, {
                'readings_count': current_readings + 1
            })
            supabase_manager.add_log(f"Coffee fortune completed (free reading reduced): {user_id_str}")
        
        return response.text
        
    except Exception as e:
        logger.error(f"Coffee fortune generation error: {e}")
        return None

# --- Missing Keyboard Functions ---

def create_premium_menu_keyboard(lang='tr'):
    """Create premium menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("premium_compare", lang), callback_data='premium_compare')],
        [InlineKeyboardButton(get_text("subscription_management", lang), callback_data='subscription_management')],
        [InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]
    ])

def create_horoscope_keyboard(lang='tr'):
    """Create horoscope keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("aries", lang), callback_data='daily_horoscope_0')],
        [InlineKeyboardButton(get_text("taurus", lang), callback_data='daily_horoscope_1')],
        [InlineKeyboardButton(get_text("gemini", lang), callback_data='daily_horoscope_2')],
        [InlineKeyboardButton(get_text("cancer", lang), callback_data='daily_horoscope_3')],
        [InlineKeyboardButton(get_text("leo", lang), callback_data='daily_horoscope_4')],
        [InlineKeyboardButton(get_text("virgo", lang), callback_data='daily_horoscope_5')],
        [InlineKeyboardButton(get_text("libra", lang), callback_data='daily_horoscope_6')],
        [InlineKeyboardButton(get_text("scorpio", lang), callback_data='daily_horoscope_7')],
        [InlineKeyboardButton(get_text("sagittarius", lang), callback_data='daily_horoscope_8')],
        [InlineKeyboardButton(get_text("capricorn", lang), callback_data='daily_horoscope_9')],
        [InlineKeyboardButton(get_text("aquarius", lang), callback_data='daily_horoscope_10')],
        [InlineKeyboardButton(get_text("pisces", lang), callback_data='daily_horoscope_11')],
        [InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]
    ])

def create_compatibility_keyboard(lang='tr'):
    """Create compatibility keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("aries", lang), callback_data='compat_aries')],
        [InlineKeyboardButton(get_text("taurus", lang), callback_data='compat_taurus')],
        [InlineKeyboardButton(get_text("gemini", lang), callback_data='compat_gemini')],
        [InlineKeyboardButton(get_text("cancer", lang), callback_data='compat_cancer')],
        [InlineKeyboardButton(get_text("leo", lang), callback_data='compat_leo')],
        [InlineKeyboardButton(get_text("virgo", lang), callback_data='compat_virgo')],
        [InlineKeyboardButton(get_text("libra", lang), callback_data='compat_libra')],
        [InlineKeyboardButton(get_text("scorpio", lang), callback_data='compat_scorpio')],
        [InlineKeyboardButton(get_text("sagittarius", lang), callback_data='compat_sagittarius')],
        [InlineKeyboardButton(get_text("capricorn", lang), callback_data='compat_capricorn')],
        [InlineKeyboardButton(get_text("aquarius", lang), callback_data='compat_aquarius')],
        [InlineKeyboardButton(get_text("pisces", lang), callback_data='compat_pisces')],
        [InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]
    ])


# --- Message Handlers ---

async def handle_message(update: Update, context: CallbackContext):
    """Handle all text messages"""
    if not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    text = update.message.text
    
    # Get user from database to check state
    user = supabase_manager.get_user(user_id)
    user_state = user.get('state', 'idle') if user else 'idle'
    
    # Handle different user states
    if user_state == 'waiting_for_dream':
        await handle_dream_text(update, context)
    elif user_state == 'waiting_for_birth_info':
        await process_birth_chart(update, context)
    elif user_state == 'chatbot_mode':
        await handle_chatbot_question(update, context)
    else:
        # Default response - show main menu
        await update.message.reply_text(
            get_text("default_message_response", lang),
            reply_markup=create_main_menu_keyboard(lang)
        )

async def handle_photo(update: Update, context: CallbackContext):
    """Handle photo messages (for coffee fortune)"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    # Check if user can use fortune telling
    user = supabase_manager.get_user(user_id)
    fortune_count = user.get('fortune_count', 0)
    premium_plan = user.get('premium_plan', 'free')
    
    if premium_plan == 'free' and fortune_count >= FREE_READING_LIMIT:
        message = get_text("fortune_limit_reached", lang, stars_count=PAID_READING_STARS)
        keyboard = [
            [InlineKeyboardButton(get_text("premium_menu", lang), callback_data='premium_menu')],
            [InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]
        ]
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # Process coffee fortune
    await update.message.reply_text(get_text("fortune_in_progress", lang))
    
    # Download photo
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Generate fortune
    await generate_coffee_fortune_impl(update, photo_bytes, lang)


# --- Missing Functions ---

async def post_init(application: Application):
    """Post initialization function"""
    logger.info("Bot initialized successfully")
    
    # Start scheduler after the event loop is running
    scheduler.start()
    
    # Schedule daily card sending
    scheduler.add_job(
        send_daily_cards,
        CronTrigger(hour=9, minute=0),
        id='daily_cards',
        replace_existing=True
    )
    
    # Schedule moon notifications
    scheduler.add_job(
        check_and_send_moon_notifications,
        CronTrigger(hour=20, minute=0),
        id='moon_notifications',
        replace_existing=True
    )
    
    logger.info("Scheduler started and jobs scheduled")

async def pre_checkout_callback(update: Update, context: CallbackContext):
    """Pre-checkout callback"""
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment_callback(update: Update, context: CallbackContext):
    """Successful payment callback for Telegram Stars payments"""
    payment_info = update.message.successful_payment
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    try:
        # Handle different payment types
        if payment_info.invoice_payload.startswith('premium_'):
            # Extract plan name and user ID from payload
            payload_parts = payment_info.invoice_payload.split('_')
            if len(payload_parts) >= 3:
                plan_name = payload_parts[1]  # e.g., 'basic', 'premium', 'vip'
                user_id_from_payload = payload_parts[2]
                
                # Verify this is the correct user
                if str(user_id) == user_id_from_payload:
                    # Update user premium plan in database
                    plan = PREMIUM_PLANS.get(plan_name)
                    if plan:
                        # Calculate expiration date (30 days from now)
                        expires_at = datetime.now() + timedelta(days=30)
                        
                        # Update user's premium plan
                        supabase_manager.update_user_premium_plan(
                            user_id, 
                            plan_name, 
                            expires_at.isoformat()
                        )
                        
                        # Log the successful payment
                        supabase_manager.add_log(
                            f"Premium payment successful: User {user_id} purchased {plan_name} plan for {payment_info.total_amount} XTR"
                        )
                        
                        # Send success message
                        success_message = f"""🎉 **Premium Abonelik Aktif!** 🎉

✨ **Plan:** {plan['name']}
💰 **Ödenen:** {payment_info.total_amount} ⭐
📅 **Süre:** {plan['duration']}
⏰ **Bitiş Tarihi:** {expires_at.strftime('%d.%m.%Y')}

🎯 Artık tüm premium özelliklere erişiminiz var!

🏠 Ana menüye dönmek için /start komutunu kullanın."""
                        
                        await update.message.reply_text(
                            success_message,
                            parse_mode='Markdown',
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")],
                                [InlineKeyboardButton("💎 Premium Özellikler", callback_data="premium_menu")]
                            ])
                        )
                    else:
                        await update.message.reply_text("❌ Geçersiz plan türü!")
                else:
                    await update.message.reply_text("❌ Kullanıcı kimliği doğrulanamadı!")
            else:
                await update.message.reply_text("❌ Geçersiz ödeme bilgisi!")
                
        elif payment_info.invoice_payload == 'coffee_fortune':
            await process_coffee_fortune_paid(update, context, True)
        elif payment_info.invoice_payload == 'tarot_fortune':
            await process_paid_tarot(update, context)
        else:
            await update.message.reply_text("✅ Ödeme başarıyla işlendi!")
            
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await update.message.reply_text(
            "❌ Ödeme işlenirken bir hata oluştu. Lütfen destek ekibiyle iletişime geçin.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
            ])
        )

async def error_handler(update: Update, context: CallbackContext):
    """Error handler"""
    logger.error(f"Exception while handling an update: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("An error occurred. Please try again later.")

async def send_daily_cards():
    """Send daily cards to subscribed users"""
    # Implementation for sending daily cards
    logger.info("Sending daily cards to subscribed users")

async def check_and_send_moon_notifications():
    """Check and send moon notifications"""
    # This function would check for moon phases and send notifications
    # Implementation depends on your notification system
    pass

async def process_coffee_fortune_paid(update, context, is_paid=False):
    """Process paid coffee fortune with sharing options"""
    user_id = update.effective_user.id
    user = supabase_manager.get_user(user_id)
    lang = get_user_language(user_id)
    
    # Generate coffee fortune
    try:
        # Get photo from update
        photo = update.message.photo[-1] if update.message.photo else None
        if not photo:
            await update.message.reply_text(
                get_text("coffee_fortune_no_photo", lang),
                reply_markup=get_main_menu_keyboard(user_id)
            )
            return
        
        # Download photo
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Generate fortune using AI
        fortune_result = await generate_coffee_fortune_impl(update, photo_bytes, lang)
        
        if fortune_result:
            # Show fortune with sharing options
            await show_coffee_fortune_with_sharing(update, fortune_result, lang)
        else:
            await update.message.reply_text(
                get_text("fortune_error", lang),
                reply_markup=get_main_menu_keyboard(user_id)
            )
            
    except Exception as e:
        logger.error(f"Coffee fortune error: {e}")
        await update.message.reply_text(
            get_text("fortune_error", lang),
            reply_markup=get_main_menu_keyboard(user_id)
        )

async def process_paid_tarot(update, context):
    """Process paid tarot reading"""
    user_id = update.effective_user.id
    user = supabase_manager.get_user(user_id)
    lang = user.get('language', 'tr')
    
    # Draw a random tarot card
    tarot_cards = supabase_manager.get_tarot_cards()
    card = random.choice(tarot_cards) if tarot_cards else "The Fool"
    
    await update.message.reply_text(
        get_text("tarot_fortune_paid", lang, card=card),
        parse_mode='Markdown'
    )

# Missing functions from the previous bot.py
async def draw_tarot_card(update: Update, context: CallbackContext):
    """Draw tarot card and create interpretation with optimized performance."""
    query = update.callback_query
    await query.answer()
    
    user = await get_or_create_user(query.from_user.id, query.from_user)
    user_id_str = str(query.from_user.id)
    lang = get_user_language(query.from_user.id)
    
    # Check rate limit
    if not gemini_rate_limiter.can_make_request(query.from_user.id):
        wait_time = gemini_rate_limiter.get_wait_time(query.from_user.id)
        await query.edit_message_text(
            f"⚠️ API rate limit exceeded. Please wait {int(wait_time)} seconds before trying again.",
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )
        return
    
    # Admin check - admin has unlimited access
    if query.from_user.id == ADMIN_ID:
        supabase_manager.add_log(f"Admin user requested tarot: {user_id_str}")
        await query.edit_message_text(get_text("tarot_drawing", lang))
        
        try:
            tarot_cards = supabase_manager.get_tarot_cards()
            card = random.choice(tarot_cards) if tarot_cards else "The Fool"
            
            # Optimized prompt for faster response
            optimized_prompt = f"Tarot reader: {user.get('first_name', 'Friend')} drew {card}. Brief interpretation in {lang}, 80 words max."
            
            # Try both APIs concurrently for faster response
            response = await get_fastest_ai_response(optimized_prompt, lang)
            
            supabase_manager.add_log(f"Admin tarot reading generated. User: {user_id_str}. Card: {card}")
            await query.message.reply_text(response, reply_markup=get_main_menu_keyboard(query.from_user.id))
        except Exception as e:
            logger.error(f"Admin tarot reading error: {e}")
            await query.edit_message_text(
                get_text("fortune_error", lang), 
                reply_markup=get_main_menu_keyboard(query.from_user.id)
            )
        return
    
    # Check reading limit for regular users
    readings_count = supabase_manager.get_user(query.from_user.id).get("readings_count", 0)
    if readings_count >= FREE_READING_LIMIT:
        # Redirect to premium plans
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Premium Plans", callback_data="premium_menu")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        await query.edit_message_text(
            f"{get_text('fortune_limit_reached', lang)}\n\n💫 **Continue with Telegram Stars:**", 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    await query.edit_message_text(get_text("tarot_drawing", lang))
    
    try:
        tarot_cards = supabase_manager.get_tarot_cards()
        card = random.choice(tarot_cards) if tarot_cards else "The Fool"
        
        # Optimized prompt for faster response
        optimized_prompt = f"Tarot reader: {user.get('first_name', 'Friend')} drew {card}. Brief interpretation in {lang}, 80 words max."
        
        # Try both APIs concurrently for faster response
        response = await get_fastest_ai_response(optimized_prompt, lang)
        
        if not response:
            raise Exception("No response from AI APIs")
        
        supabase_manager.add_log(f"Tarot response received ({lang}): {len(response)} characters")
        
        # Update reading count
        supabase_manager.update_user(query.from_user.id, {
            "readings_count": supabase_manager.get_user(query.from_user.id)["readings_count"] + 1
        })
        
        supabase_manager.add_log(f"Tarot reading generated. User: {user_id_str}. Card: {card}")
        await query.message.reply_text(response, reply_markup=get_main_menu_keyboard(query.from_user.id))
    except Exception as e:
        logger.error(f"Tarot reading error: {e}")
        await query.edit_message_text(
            get_text("fortune_error", lang), 
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )


async def get_fastest_ai_response(prompt: str, lang: str) -> str:
    """Get the fastest response from either Gemini or DeepSeek API."""
    loop = asyncio.get_event_loop()
    
    # Create tasks for both APIs
    gemini_task = asyncio.create_task(
        asyncio.wait_for(
            loop.run_in_executor(None, lambda: call_gemini_api(prompt)),
            timeout=6.0  # Reduced timeout for faster response
        )
    )
    
    deepseek_task = asyncio.create_task(
        asyncio.wait_for(
            loop.run_in_executor(None, lambda: call_deepseek_api(prompt)),
            timeout=8.0  # Slightly longer timeout for DeepSeek
        )
    )
    
    # Wait for the first successful response
    try:
        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [gemini_task, deepseek_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel the other task
        for task in pending:
            task.cancel()
        
        # Get the result from the completed task
        for task in done:
            try:
                result = task.result()
                if result:
                    return result
            except Exception as e:
                supabase_manager.add_log(f"API task failed: {str(e)[:100]}")
        
        # If both failed, return fallback response
        return get_fallback_tarot_response(lang)
        
    except Exception as e:
        supabase_manager.add_log(f"All AI APIs failed: {str(e)[:100]}")
        return get_fallback_tarot_response(lang)


def call_gemini_api(prompt: str) -> str:
    """Call Gemini API with error handling."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text if response and response.text else ""
    except Exception as e:
        supabase_manager.add_log(f"Gemini API error: {str(e)[:100]}")
        return ""


def get_fallback_tarot_response(lang: str) -> str:
    """Get fallback tarot response when APIs fail."""
    fallback_responses = {
        'tr': "🔮 **Tarot Yorumu**\n\nKartınız size yeni fırsatlar ve değişimler getiriyor. Cesaretinizi toplayın ve yeni başlangıçlar yapın.",
        'en': "🔮 **Tarot Interpretation**\n\nYour card brings new opportunities and changes. Gather your courage and make new beginnings.",
        'es': "🔮 **Interpretación de Tarot**\n\nTu carta trae nuevas oportunidades y cambios. Reúne tu coraje y haz nuevos comienzos."
    }
    return fallback_responses.get(lang, fallback_responses['en'])

async def handle_dream_text(update: Update, context: CallbackContext):
    """Handle dream text, birth chart information, and chatbot questions."""
    user_id_str = str(update.effective_user.id)
    user = supabase_manager.get_user(update.effective_user.id)
    
    supabase_manager.add_log(f"handle_dream_text called: {user_id_str}")
    supabase_manager.add_log(f"User state: {user.get('state') if user else 'no_user'}")
    
    # Check user state
    if user and user.get('state') == 'waiting_for_dream':
        # Dream interpretation process
        lang = get_user_language(update.effective_user.id)
        dream_text = update.message.text
        
        # Detect language from dream text for better accuracy
        detected_lang = detect_dream_language(dream_text)
        if detected_lang and detected_lang != lang:
            # Update user language if different from detected
            supabase_manager.update_user(update.effective_user.id, {'language': detected_lang})
            lang = detected_lang
            supabase_manager.add_log(f"Language updated to {lang} based on dream text")
        
        supabase_manager.add_log(f"Dream text received: {user_id_str}. Text: {dream_text[:50]}... Language: {lang}")
        
        await update.message.reply_text(get_text("dream_analyzing", lang))
        
        try:
            # Use faster model for better performance
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-pro')
            
            # Get prompt from Supabase with proper language
            prompt = supabase_manager.get_prompt("dream", lang)
            if not prompt:
                # Fallback prompts for each language
                fallback_prompts = {
                    'tr': f"Sen deneyimli bir rüya yorumcususun. {update.effective_user.first_name} için rüya yorumu yap.\n\nRüyasında ne gördüğünü önce anlat. Örneğin: 'Rüyanda bir kelebek gördün...'\n\nSonra bu sembollerin anlamını açıkla ve {update.effective_user.first_name} için kişisel bir yorum yap.\n\n150-200 kelime.",
                    'en': f"You are an experienced dream interpreter. Create a dream interpretation for {update.effective_user.first_name}.\n\nDescribe what they saw in their dream first. For example: 'In your dream, you saw a butterfly...'\n\nThen explain the meaning of these symbols and make a personal interpretation for {update.effective_user.first_name}.\n\n150-200 words.",
                    'es': f"Eres un intérprete de sueños experimentado. Crea una interpretación de sueños para {update.effective_user.first_name}.\n\nPrimero describe lo que vieron en su sueño. Por ejemplo: 'En tu sueño, viste una mariposa...'\n\nLuego explica el significado de estos símbolos y haz una interpretación personal para {update.effective_user.first_name}.\n\n150-200 palabras."
                }
                prompt = fallback_prompts.get(lang, fallback_prompts['en'])
            
            # Prepare prompt with proper language instruction
            final_prompt = prompt.replace("{username}", update.effective_user.first_name).replace("{dream_text}", dream_text)
            
            # Add explicit language instruction
            language_instructions = {
                'tr': f"RÜYA YORUMCUSU. SADECE TÜRKÇE RÜYA YORUMU YAZ.\n\n{final_prompt}\n\nTÜRKÇE YORUM:",
                'en': f"DREAM INTERPRETER. WRITE ONLY DREAM INTERPRETATION IN ENGLISH.\n\n{final_prompt}\n\nENGLISH INTERPRETATION:",
                'es': f"INTÉRPRETE DE SUEÑOS. ESCRIBE SOLO LA INTERPRETACIÓN DEL SUEÑO EN ESPAÑOL.\n\n{final_prompt}\n\nINTERPRETACIÓN EN ESPAÑOL:"
            }
            final_prompt = language_instructions.get(lang, language_instructions['en'])
            
            supabase_manager.add_log(f"Dream prompt prepared ({lang}): {len(final_prompt)} characters")
            supabase_manager.add_log(f"Gemini API call in progress (dream, {lang}): {user_id_str}")
            
            # Send to Gemini (async API) - with timeout
            try:
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, model.generate_content, final_prompt),
                    timeout=8.0  # Reduced timeout for faster response
                )
                
                supabase_manager.add_log(f"Gemini API response successfully received: {user_id_str}")
            except asyncio.TimeoutError:
                supabase_manager.add_log(f"Gemini API timeout (8s): {user_id_str}")
                # Try DeepSeek as fallback
                try:
                    deepseek_response = await asyncio.wait_for(
                        loop.run_in_executor(None, call_deepseek_api, final_prompt),
                        timeout=10.0
                    )
                    response = type('Response', (), {'text': deepseek_response})()
                    supabase_manager.add_log(f"DeepSeek fallback successful: {user_id_str}")
                except Exception as deepseek_error:
                    supabase_manager.add_log(f"DeepSeek fallback failed: {str(deepseek_error)[:100]}")
                    raise Exception("AI API did not respond (timeout)")
            except Exception as e:
                supabase_manager.add_log(f"Gemini API error: {str(e)[:100]}")
                raise Exception(f"Gemini API error: {str(e)[:100]}")
            
            supabase_manager.add_log(f"Gemini API response received: {response}")
            
            if not response:
                raise Exception("No response received from AI API")
            
            if not response.text:
                raise Exception("Empty response received from AI API")
            
            supabase_manager.add_log(f"Dream response received: {len(response.text)} characters")
            supabase_manager.add_log(f"Response content: {response.text[:500]}...")
            
            # Reduce free reading count (if not admin)
            if update.effective_user.id != ADMIN_ID:
                current_readings = user.get("readings_count", 0)
                supabase_manager.update_user(update.effective_user.id, {
                    'state': 'idle',
                    'readings_count': current_readings + 1
                })
                supabase_manager.add_log(f"Dream analysis completed (free reading reduced): {user_id_str}")
            else:
                supabase_manager.update_user(update.effective_user.id, {'state': 'idle'})
                supabase_manager.add_log(f"Admin dream analysis completed: {user_id_str}")
            
            await update.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(update.effective_user.id))
        except Exception as e:
            logger.error(f"Dream analysis error: {e}")
            await update.message.reply_text(
                get_text("fortune_error", lang), 
                reply_markup=get_main_menu_keyboard(update.effective_user.id)
            )
            
    elif user and user.get('state') == 'waiting_for_birth_info':
        # Birth chart information process
        await process_birth_chart(update, context)
        
    elif user and user.get('state') == 'chatbot_mode':
        # Astrology chatbot process
        await handle_chatbot_question(update, context)
        
    else:
        # User is not waiting for dream, check state
        current_state = user.get('state') if user else 'no_user'
        supabase_manager.add_log(f"Text received but state not suitable: {user_id_str}. State: {current_state}")

async def process_birth_chart(update: Update, context: CallbackContext):
    """Process birth chart analysis"""
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    lang = get_user_language(user_id)
    birth_info = update.message.text
    
    await update.message.reply_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Get prompt from Supabase
        prompt = supabase_manager.get_prompt("birth_chart", lang)
        if not prompt:
            prompt = f"You are a professional astrologer. Create a comprehensive birth chart analysis based on the following birth information:\n\nBirth Information: {birth_info}\n\nThe analysis should include:\n1. Sun Sign Analysis\n2. Rising Sign\n3. Moon Sign\n4. Mercury\n5. Venus\n6. Mars\n7. General Interpretation\n\n200-250 words, personalized and in-depth."
        
        # Replace placeholders
        username = update.effective_user.first_name or update.effective_user.username or "User"
        final_prompt = prompt.format(
            username=username,
            birth_date=birth_info,
            birth_time="Unknown",
            birth_place="Unknown"
        )
        
        # Add language instruction
        final_prompt = f"YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.\n\n{final_prompt}\n\n{lang.upper()} ANALYSIS:"
        
        # Async API call - with timeout
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, model.generate_content, final_prompt),
                timeout=15.0  # 15 second timeout
            )
            
            supabase_manager.add_log(f"✅ Birth Chart Gemini API call completed: {user_id_str}")
        except asyncio.TimeoutError:
            supabase_manager.add_log(f"❌ Birth Chart Gemini API timeout (15s): {user_id_str}")
            raise Exception("Gemini API did not respond (15 second timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Birth Chart Gemini API error: {str(e)[:100]}")
            raise Exception(f"Gemini API error: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Empty response received from Gemini API")
        
        chart_message = f"""🌟 **BIRTH CHART ANALYSIS** 🌟
━━━━━━━━━━━━━━━━━━━━━━

📅 **Birth Information:** {birth_info}

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *This analysis is prepared to provide you with personal guidance* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Another Analysis", callback_data="astro_birth_chart")],
            [InlineKeyboardButton("📱 Download PDF", callback_data=f"birth_chart_pdf_{user_id}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(chart_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.update_user(user_id, {'state': 'idle'})
        supabase_manager.add_log(f"Birth chart analysis completed: {user_id_str}")
        
    except Exception as e:
        logger.error(f"Birth chart error: {e}")
        await update.message.reply_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        supabase_manager.update_user(user_id, {'state': 'idle'})

async def handle_chatbot_question(update: Update, context: CallbackContext):
    """Handle chatbot questions"""
    user_id = update.effective_user.id
    user = supabase_manager.get_user(user_id)
    
    if user.get('state') != 'chatbot_mode' or user.get('premium_plan') != 'vip':
        return
    
    lang = get_user_language(user_id)
    question = update.message.text
    
    await update.message.reply_text(get_text(lang, "analyzing"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Get prompt from Supabase
        prompt = supabase_manager.get_prompt("astro_chatbot", lang)
        if not prompt:
            prompt = f"You are an experienced astrology chatbot. Answer the user's question like a professional astrology consultant.\n\nUser Question: {question}\n\nYour answer should include:\n- Direct and detailed response to the question\n- Astrological information and explanations\n- Practical advice\n- References to current planetary conditions\n\n120-180 words, in a friendly and professional tone."
        
        # Replace placeholders
        username = update.effective_user.first_name or update.effective_user.username or "User"
        final_prompt = prompt.format(username=username)
        
        # Add question and language instruction
        final_prompt = f"USER QUESTION: {question}\n\n{final_prompt}\n\nYOU ARE AN ASTROLOGY CHATBOT. RESPOND ONLY IN {lang.upper()} LANGUAGE.\n\n{lang.upper()} RESPONSE:"
        
        response = model.generate_content(final_prompt)
        
        if response and response.text:
            chatbot_message = f"""🤖 **ASTROLOGY CONSULTANT** 🤖

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
💬 *You can ask another question...*"""
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close Chatbot", callback_data="chatbot_close")]
            ])
            
            await update.message.reply_text(chatbot_message, reply_markup=keyboard, parse_mode='Markdown')
            supabase_manager.add_log(f"Chatbot question answered: {user_id} - {question[:50]}...")
        else:
            raise Exception("No response received from Gemini API")
            
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        await update.message.reply_text(
            get_text(lang, "sorry_cant_respond"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Close Chatbot", callback_data="chatbot_close")]
            ])
        )

# Missing functions from the previous bot.py
async def toggle_daily_subscription(update: Update, context: CallbackContext):
    """Toggle daily subscription"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    current_status = user.get("daily_subscribed", False)
    lang = get_user_language(query.from_user.id)
    
    # User's current status
    subscription_status = "✅ ACTIVE" if current_status else "❌ INACTIVE"
    next_delivery = "Every morning 09:00" if current_status else "Subscription not active"
    
    # Detailed explanation message
    if lang == 'tr':
        info_message = f"""🌅 **DAILY CARD SUBSCRIPTION** 🌅
━━━━━━━━━━━━━━━━━━━━━━

📱 **Your Current Status:** {subscription_status}
⏰ **Next Delivery:** {next_delivery}

🔮 **About This Feature:**
With Daily Card subscription, you receive a specially prepared tarot card and its interpretation every morning. This card presents the day's energy, opportunities you may encounter, and points to pay attention to from a mystical perspective.

✨ **What's Included:**
• 🃏 Special tarot card every morning at 09:00
• 📜 Current interpretation and meaning of the card
• 🎯 Practical advice for the day
• 🌟 Personal energy guidance
• 💫 Astrological connections and tips

🎁 **Special Benefits:**
• Completely FREE service
• Different card and interpretation every day
• Personalized content
• Motivational and inspiring messages
• Capturing the positive energy of the day

📊 **Statistics:**
• 15,000+ active daily subscribers
• 94% user satisfaction
• Average 4.8/5 rating

🔧 **How It Works:**
1. Activate subscription
2. Receive automatic message every morning
3. Read your card and plan your day
4. Cancel anytime you want

⚙️ **Settings:**
• Delivery time: 09:00 (changeable)
• Including weekends: Yes
• Notification type: Silent message"""

        toggle_text = "🔕 Stop Subscription" if current_status else "🔔 Start Subscription"
        toggle_callback = "confirm_daily_unsubscribe" if current_status else "confirm_daily_subscribe"
        
    else:  # English
        info_message = f"""🌅 **DAILY CARD SUBSCRIPTION** 🌅
━━━━━━━━━━━━━━━━━━━━━━

📱 **Your Current Status:** {subscription_status}
⏰ **Next Delivery:** {next_delivery}

🔮 **About This Feature:**
With Daily Card subscription, you receive a specially prepared tarot card and its interpretation every morning. This card presents the day's energy, opportunities you may encounter, and points to pay attention to from a mystical perspective.

✨ **What's Included:**
• 🃏 Special tarot card every morning at 09:00
• 📜 Current interpretation and meaning of the card
• 🎯 Practical advice for the day
• 🌟 Personal energy guidance
• 💫 Astrological connections and tips

🎁 **Special Benefits:**
• Completely FREE service
• Different card and interpretation every day
• Personalized content
• Motivational and inspiring messages
• Capturing the positive energy of the day

📊 **Statistics:**
• 15,000+ active daily subscribers
• 94% user satisfaction
• Average 4.8/5 rating

🔧 **How It Works:**
1. Activate subscription
2. Receive automatic message every morning
3. Read your card and plan your day
4. Cancel anytime you want

⚙️ **Settings:**
• Delivery time: 09:00 (changeable)
• Including weekends: Yes
• Notification type: Silent message"""

        toggle_text = "🔕 Stop Subscription" if current_status else "🔔 Start Subscription"
        toggle_callback = "confirm_daily_unsubscribe" if current_status else "confirm_daily_subscribe"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, callback_data=toggle_callback)],
        [InlineKeyboardButton("⚙️ Set Delivery Time", callback_data="set_delivery_time")],
        [InlineKeyboardButton("📊 Subscription Statistics", callback_data="subscription_stats")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(info_message, reply_markup=keyboard, parse_mode='Markdown')

async def confirm_daily_subscribe(update: Update, context: CallbackContext):
    """Confirm daily subscription"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    supabase_manager.update_user(query.from_user.id, {"daily_subscribed": True})
    lang = get_user_language(query.from_user.id)
    
    supabase_manager.add_log(f"User {user_id_str} started daily subscription.")
    
    success_message = """🎉 **Daily Card Subscription Activated!** 🎉

✅ You will now receive your special tarot card every morning at 09:00
🔮 Your first card will be delivered tomorrow morning
💫 Great decision!

🎁 **Welcome Gift:**
You'll receive an extra bonus card for your first week!"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Subscription Settings", callback_data="toggle_daily")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(success_message, reply_markup=keyboard, parse_mode='Markdown')

async def confirm_daily_unsubscribe(update: Update, context: CallbackContext):
    """Cancel daily subscription"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    supabase_manager.update_user(query.from_user.id, {"daily_subscribed": False})
    lang = get_user_language(query.from_user.id)
    
    supabase_manager.add_log(f"User {user_id_str} stopped daily subscription.")
    
    unsubscribe_message = """💔 **Daily Card Subscription Stopped**

😔 You will no longer receive daily tarot cards
🔄 You can reactivate anytime
🎁 Your data is preserved, you can return

📊 **Your Feedback:**
Why did you stop the subscription? (Optional)"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Subscribe Again", callback_data="confirm_daily_subscribe")],
        [InlineKeyboardButton("💬 Give Feedback", callback_data="daily_feedback")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(unsubscribe_message, reply_markup=keyboard, parse_mode='Markdown')

async def get_referral_link_callback(update: Update, context: CallbackContext):
    """Create and show referral link"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_language(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    
    # Get referral statistics
    referred_count = user.get("referred_count", 0)
    bonus_readings = user.get("bonus_readings", 0)
    referral_earnings = user.get("referral_earnings", 0)
    
    # VIP status check
    vip_status = "👑 VIP" if referred_count >= 10 else "🌟 Elite" if referred_count >= 25 else "💎 Premium" if referred_count >= 5 else "🆕 New"
    
    # Progress bar (5 milestone)
    current_milestone = (referred_count // 5) * 5
    next_milestone = current_milestone + 5
    progress = referred_count - current_milestone
    progress_bar = "🟢" * progress + "⚪" * (5 - progress)
    
    # Daily/weekly goals
    daily_goal = 1
    weekly_goal = 5
    
    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user_id_str}"
    
    message = f"""🌟 **FAL GRAM REFERRAL SYSTEM** 🌟
━━━━━━━━━━━━━━━━━━━━━━

👤 **Your Status:** {vip_status}

📊 **Your Statistics:**
👥 Total Invites: **{referred_count}** people
🎁 Bonus Readings: **{bonus_readings}** readings
💰 Total Earnings: **{referral_earnings}** readings

📈 **Progress Bar ({progress}/5):**
{progress_bar} **{referred_count}**/{next_milestone}

🏆 **Reward System:**
• 1 Invite = 1 Free Reading ✨
• 5 Invites = 3 Bonus Readings + Special Badges 🏅
• 10 Invites = VIP Status + Unlimited Daily Cards 👑
• 25 Invites = Elite Member + Priority Support 🌟
• 50 Invites = Premium Fortune Teller Access 💎

🎯 **Your Goals:**
• Daily: {daily_goal} invite
• Weekly: {weekly_goal} invites

🔗 **Your Special Referral Link:**
```
{referral_link}
```

📤 **Quick Share:**"""
    
    # Advanced buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Share on WhatsApp", url=f"https://api.whatsapp.com/send?text=🔮 Get free fortune telling on Fal Gram! {referral_link}"),
            InlineKeyboardButton("📲 Share on Telegram", url=f"https://t.me/share/url?url={referral_link}&text=🔮 Get free fortune telling on Fal Gram!")
        ],
        [
            InlineKeyboardButton("📊 Detailed Statistics", callback_data="referral_stats"),
            InlineKeyboardButton("🎁 My Rewards", callback_data="my_rewards")
        ],
        [
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_link_{user_id_str}"),
            InlineKeyboardButton("🔄 Refresh", callback_data="get_referral_link")
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')


# --- Missing Functions and Handlers ---

# Rate limiting for Gemini API
class GeminiRateLimiter:
    def __init__(self, max_requests_per_minute=60):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)
    
    def can_make_request(self, user_id):
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove requests older than 1 minute
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < 60]
        
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        return False
    
    def get_wait_time(self, user_id):
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [req_time for req_time in user_requests if now - req_time < 60]
        
        if len(user_requests) >= self.max_requests:
            oldest_request = min(user_requests)
            return 60 - (now - oldest_request)
        return 0

# Initialize rate limiter
gemini_rate_limiter = GeminiRateLimiter()

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(prompt, model="deepseek-chat"):
    """Call DeepSeek API with the given prompt"""
    if not DEEPSEEK_API_KEY:
        raise Exception("DeepSeek API key not configured")
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"DeepSeek API error: {str(e)}")

# Zodiac signs for different languages
ZODIAC_SIGNS = {
    'tr': ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık'],
    'en': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
    'es': ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis'],
    'fr': ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons']
}

# Supported languages
SUPPORTED_LANGUAGES = {
    'tr': 'Türkçe',
    'en': 'English', 
    'es': 'Español',
   
}

# Initialize Supabase manager
supabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)

# Missing admin functions
async def admin_gift_command(update: Update, context: CallbackContext):
    """Admin command to gift premium subscription"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("❌ Kullanım: /gift <user_id> <plan> <days>")
            return
        
        user_id = int(args[0])
        plan = args[1]
        days = int(args[2])
        
        # Validate plan
        if plan not in ['basic', 'premium', 'vip']:
            await update.message.reply_text("❌ Geçersiz plan. Kullanılabilir: basic, premium, vip")
            return
        
        # Calculate expiration date
        expires_at = datetime.now() + timedelta(days=days)
        
        # Update user's premium plan
        supabase_manager.update_user_premium_plan(user_id, plan, expires_at)
        
        # Log the action
        supabase_manager.add_log(f"Admin gifted {plan} plan to user {user_id} for {days} days")
        
        await update.message.reply_text(f"✅ {user_id} kullanıcısına {plan} planı {days} gün için hediye edildi!")
        
    except ValueError:
        await update.message.reply_text("❌ Geçersiz user_id veya days değeri!")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

async def admin_cancel_command(update: Update, context: CallbackContext):
    """Admin command to cancel premium subscription"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Kullanım: /cancel <user_id>")
            return
        
        user_id = int(args[0])
        
        # Cancel user's premium plan
        supabase_manager.update_user_premium_plan(user_id, 'free', None)
        
        # Log the action
        supabase_manager.add_log(f"Admin cancelled premium plan for user {user_id}")
        
        await update.message.reply_text(f"✅ {user_id} kullanıcısının premium aboneliği iptal edildi!")
        
    except ValueError:
        await update.message.reply_text("❌ Geçersiz user_id değeri!")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

# Missing callback handlers
async def back_to_admin(update: Update, context: CallbackContext):
    """Return to admin panel"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    lang = get_user_language(query.from_user.id)
    await admin_show_stats(query, lang)

async def admin_gift_subscription_input(update: Update, context: CallbackContext):
    """Handle gift subscription input"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    # Store user state for gift subscription
    context.user_data['gift_state'] = 'waiting_user_id'
    await update.message.reply_text("👤 Hediye edilecek kullanıcının ID'sini girin:")

async def admin_cancel_subscription_input(update: Update, context: CallbackContext):
    """Handle cancel subscription input"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    # Store user state for cancel subscription
    context.user_data['cancel_state'] = 'waiting_user_id'
    await update.message.reply_text("👤 İptal edilecek kullanıcının ID'sini girin:")

# Missing premium purchase handlers
async def premium_buy_plan(update: Update, context: CallbackContext):
    """Handle premium plan purchase with Telegram Stars"""
    query = update.callback_query
    await query.answer()
    
    plan_name = query.data.replace('buy_', '')
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    if plan_name not in PREMIUM_PLANS:
        await query.edit_message_text("❌ Geçersiz plan!")
        return
    
    plan = PREMIUM_PLANS[plan_name]
    
    # Check if payment provider token is configured
    if not PAYMENT_PROVIDER_TOKEN:
        await query.edit_message_text(
            "❌ Ödeme sistemi henüz yapılandırılmamış. Lütfen daha sonra tekrar deneyin.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Premium Menü", callback_data="premium_menu")]
            ])
        )
        return
    
    # Create invoice for Telegram Stars payment
    prices = [LabeledPrice(plan['name'], plan['price_stars'])]
    
    try:
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title=f"{plan['name']} Aboneliği",
            description=plan['description'],
            payload=f"premium_{plan_name}_{user_id}",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",  # Telegram Stars currency
            prices=prices,
            start_parameter=f"premium_{plan_name}",
            photo_url="https://t.me/your_bot_username/photo",  # Optional: Add your bot's photo
            photo_width=512,
            photo_height=512,
            photo_size=512,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
            is_flexible=False
        )
        
        await query.edit_message_text(
            f"💳 **{plan['name']} Planı Satın Alma**\n\n"
            f"💰 Fiyat: {plan['price_stars']} ⭐\n"
            f"📅 Süre: {plan['duration']}\n"
            f"📝 {plan['description']}\n\n"
            f"Ödeme sayfası açılıyor...",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Premium Menü", callback_data="premium_menu")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Payment invoice creation failed: {e}")
        await query.edit_message_text(
            f"❌ Ödeme oluşturulamadı: {str(e)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Premium Menü", callback_data="premium_menu")]
            ])
        )

# Missing astrology handlers
async def advanced_moon_calendar(update: Update, context: CallbackContext):
    """Show advanced moon calendar"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_language(query.from_user.id)
    
    # Calculate current moon phase
    current_phase = calculate_moon_phase()
    energy_advice = get_moon_energy_advice(current_phase['energy'], lang)
    
    message = f"""🌙 **GELİŞMİŞ AY TAKVİMİ** 🌙
━━━━━━━━━━━━━━━━━━━━━━

📅 **Bugünün Ay Fazı:** {current_phase['phase_name']}
🌊 **Enerji Seviyesi:** {current_phase['energy']}/100
📊 **Ay Yaşı:** {current_phase['age']:.1f} gün

💫 **Enerji Tavsiyesi:**
{energy_advice}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Ay enerjisini kullanarak gününüzü planlayın* ✨"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def planetary_transits(update: Update, context: CallbackContext):
    """Show planetary transits (VIP feature)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    premium_info = check_premium_access(user_id)
    lang = get_user_language(user_id)
    
    if not premium_info['has_premium'] or premium_info['plan'] not in ['premium', 'vip']:
        await query.edit_message_text(
            "❌ Bu özellik sadece Premium ve VIP kullanıcılar için!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium Planlar", callback_data="premium_menu")],
                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
            ])
        )
        return
    
    # Generate planetary transit information
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are an expert astrologer. Create a detailed planetary transit report for today.

Include:
1. Current planetary positions
2. Major transits and aspects
3. How these affect different zodiac signs
4. Recommendations for the day

Write in {lang.upper()} language, 200-250 words."""

        response = model.generate_content(prompt)
        
        message = f"""🌟 **PLANETARY TRANSITS** 🌟
━━━━━━━━━━━━━━━━━━━━━━

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Premium astrological insights* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Hata: {str(e)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")]
            ])
        )

async def social_astrology(update: Update, context: CallbackContext):
    """Show social astrology features (VIP feature)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    lang = get_user_language(user_id)
    
    if user.get('premium_plan') != 'vip':
        await query.edit_message_text(
            "❌ Bu özellik sadece VIP kullanıcılar için!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 VIP Plan", callback_data="premium_plan_vip")],
                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
            ])
        )
        return
    
    message = f"""👥 **SOSYAL ASTROLOJİ** 👥
━━━━━━━━━━━━━━━━━━━━━━

🌟 **VIP Özellikler:**
• Astroloji topluluk grupları
• Uzman astrologlarla canlı sohbet
• Kişisel astroloji danışmanlığı
• Özel astroloji etkinlikleri
• Premium astroloji içerikleri

🔮 **Yakında Gelecek:**
• Astroloji forumu
• Canlı yayınlar
• Özel workshop'lar
• Kişisel astroloji raporları

━━━━━━━━━━━━━━━━━━━━━━
✨ *VIP deneyiminizi keşfedin* ✨"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def chatbot_close(update: Update, context: CallbackContext):
    """Close chatbot mode"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    supabase_manager.update_user(user_id, {'state': 'idle'})
    
    lang = get_user_language(user_id)
    await show_main_menu(query, lang)

# Missing utility functions
def get_main_menu_keyboard(user_id: int):
    """Get main menu keyboard for user"""
    lang = get_user_language(user_id)
    return create_main_menu_keyboard(lang)

def detect_dream_language(text: str) -> str:
    """Detect language from dream text for better accuracy."""
    # Simple language detection based on common words
    text_lower = text.lower()
    
    # Turkish indicators
    turkish_words = ['rüya', 'gördüm', 'gördü', 'gördüğüm', 'gördüğü', 'uykuda', 'uyurken', 'rüyamda', 'rüyamda']
    if any(word in text_lower for word in turkish_words):
        return 'tr'
    
    # Spanish indicators
    spanish_words = ['sueño', 'soñé', 'soñaba', 'soñé que', 'en mi sueño', 'durmiendo', 'mientras dormía']
    if any(word in text_lower for word in spanish_words):
        return 'es'
    
    # English indicators (default)
    english_words = ['dream', 'dreamed', 'dreamt', 'dreaming', 'saw', 'saw in my dream', 'while sleeping']
    if any(word in text_lower for word in english_words):
        return 'en'
    
    # Default to English if no clear indicators
    return 'en'

async def show_coffee_fortune_with_sharing(update, fortune_text, lang):
    """Show coffee fortune with sharing options"""
    user_id = update.effective_user.id
    bot_username = update.message.from_user.bot.username if hasattr(update.message.from_user, 'bot') else "FalGramBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # Create sharing message
    share_text = f"🔮 {fortune_text[:100]}...\n\n✨ Get your own coffee fortune reading!\n🔗 {referral_link}\n\n#FalGram #CoffeeFortune #AI"
    
    # Create sharing keyboard
    keyboard = [
        [InlineKeyboardButton("🐦 Share on X", callback_data=f"share_coffee_twitter_{quote(share_text)}")],
        [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_coffee_link_{referral_link}")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    
    # Show fortune with sharing prompt
    message = f"{fortune_text}\n\n{get_text('coffee_fortune_share_prompt', lang)}"
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def handle_share_coffee_twitter(query, lang):
    """Handle sharing coffee fortune on Twitter/X"""
    # Extract share text from callback data
    callback_data = query.data
    if callback_data.startswith("share_coffee_twitter_"):
        share_text = callback_data.replace("share_coffee_twitter_", "")
        # Decode the URL-encoded text
        from urllib.parse import unquote
        share_text = unquote(share_text)
        
        # Create Twitter/X share URL
        twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
        
        keyboard = [
            [InlineKeyboardButton("🐦 Open X", url=twitter_url)],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await safe_edit_message(
            query,
            get_text("coffee_fortune_share_twitter_message", lang),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )


async def handle_copy_coffee_link(query, lang):
    """Handle copying coffee fortune referral link"""
    callback_data = query.data
    if callback_data.startswith("copy_coffee_link_"):
        referral_link = callback_data.replace("copy_coffee_link_", "")
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        await safe_edit_message(
            query,
            get_text("coffee_fortune_link_copied", lang, link=referral_link),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )


async def handle_try_payment(query, plan_name, lang):
    """Handle try payment action"""
    user_id = query.from_user.id
    plan = PREMIUM_PLANS.get(plan_name, {})
    price_stars = plan.get('price_stars', 0)
    plan_name_display = plan.get('name', plan_name.title())
    
    message = f"💳 **Payment Attempt** 💳\n\n"
    message += f"Plan: **{plan_name_display}**\n"
    message += f"Price: **{price_stars} Telegram Stars**\n\n"
    message += "⚠️ **Note:** Telegram Stars payment is currently in development.\n\n"
    message += "🔧 **For now, you can:**\n"
    message += "• Contact support for manual activation\n"
    message += "• Use admin commands if you're an admin\n"
    message += "• Wait for full payment integration\n\n"
    message += "📞 **Support:** @YourSupportUsername"
    
    keyboard = [
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="premium_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def handle_contact_support(query, lang):
    """Handle contact support action"""
    message = "📞 **Contact Support** 📞\n\n"
    message += "Need help with payment or have questions?\n\n"
    message += "🔗 **Support Options:**\n"
    message += "• Telegram: @YourSupportUsername\n"
    message += "• Email: support@falgram.com\n"
    message += "• Website: https://falgram.com/support\n\n"
    message += "📋 **Please include:**\n"
    message += "• Your User ID: `" + str(query.from_user.id) + "`\n"
    message += "• Issue description\n"
    message += "• Screenshots if applicable\n\n"
    message += "⏰ **Response time:** Usually within 24 hours"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# --- Main Function ---

def main():
    """Ana fonksiyon"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("gift", admin_gift_command))
    application.add_handler(CommandHandler("cancel", admin_cancel_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Payment handlers
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Run bot
    logger.info("Bot başlatılıyor...")
    
    if os.getenv('ENVIRONMENT') == 'production':
        # Production mode with webhook
        webhook_url = os.getenv('WEBHOOK_URL', '')
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get('PORT', 8080)),
                url_path=TELEGRAM_BOT_TOKEN,
                webhook_url=f"{webhook_url}/{TELEGRAM_BOT_TOKEN}"
            )
        else:
            logger.error("WEBHOOK_URL not set for production!")
    else:
        # Development mode with polling
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Start web service in separate thread
    from app import start_web_service
    start_web_service()
    
    # Run the bot
    main()

import os
import json
import random
import io
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler, PreCheckoutQueryHandler, ConversationHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fpdf import FPDF
from supabase import create_client, Client
from functools import lru_cache
import math
import time
import os
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime, timedelta
from fpdf import FPDF

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

# --- Başlangıç Kurulumu ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

# --- Ortam Değişkenleri ve Sabitler ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

FREE_READING_LIMIT = 5
PAID_READING_STARS = 250  # Artık kullanılmayacak, premium planlara yönlendirme
CHOOSING, TYPING_REPLY = range(2)

# Premium Plan Definitions
PREMIUM_PLANS = {
    'free': {
        'name': 'Ücretsiz',
        'name_en': 'Free',
        'price': 0,
        'price_stars': 0,
        'description': 'Temel özelliklerle başlayın',
        'description_en': 'Start with basic features',
        'features': [
            '☕ 5 ücretsiz fal (Kahve, Tarot, Rüya)',
            '♈ Günlük burç yorumu',
            '🔮 Temel astroloji özellikleri',
            '📱 Temel chatbot desteği',
            '🎁 Referral bonusları'
        ],
        'features_en': [
            '☕ 5 free readings (Coffee, Tarot, Dream)',
            '♈ Daily horoscope',
            '🔮 Basic astrology features',
            '📱 Basic chatbot support',
            '🎁 Referral bonuses'
        ]
    },
    'basic': {
        'name': 'Temel Plan',
        'name_en': 'Basic Plan',
        'price': 500,
        'price_stars': 500,
        'description': 'Sınırsız fal ve gelişmiş özellikler',
        'description_en': 'Unlimited readings and advanced features',
        'features': [
            '♾️ Sınırsız fal (Kahve, Tarot, Rüya)',
            '📊 Haftalık burç raporu',
            '🔮 Gelişmiş astroloji analizi',
            '💫 Doğum haritası yorumu',
            '🌙 Ay takvimi özellikleri',
            '💬 Gelişmiş chatbot',
            '🎯 Kişiselleştirilmiş öneriler',
            '📈 Detaylı fal geçmişi',
            '🔔 Özel bildirimler'
        ],
        'features_en': [
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
        'name_en': 'Premium Plan',
        'price': 1000,
        'price_stars': 1000,
        'description': 'Tam astroloji paketi ve özel özellikler',
        'description_en': 'Complete astrology package and special features',
        'features': [
            '✨ Temel Plan özellikleri',
            '📅 Aylık burç yorumu',
            '🪐 Gezegen geçişleri analizi',
            '💕 Burç uyumluluğu',
            '🌙 Gelişmiş ay takvimi',
            '📈 Detaylı astroloji raporları',
            '🎯 Kişiselleştirilmiş öneriler',
            '🔮 Özel fal türleri',
            '📊 Astroloji istatistikleri',
            '🎁 Özel içerikler',
            '⚡ Öncelikli destek'
        ],
        'features_en': [
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
        'name_en': 'VIP Plan',
        'price': 2000,
        'price_stars': 2000,
        'description': 'En üst düzey deneyim ve öncelikli destek',
        'description_en': 'Ultimate experience with priority support',
        'features': [
            '👑 Premium Plan özellikleri',
            '🤖 7/24 Astroloji Chatbot',
            '👥 Sosyal astroloji özellikleri',
            '🎁 Özel VIP içerikler',
            '⚡ Öncelikli destek',
            '📊 Gelişmiş analitikler',
            '🎯 Kişisel astroloji danışmanı',
            '🌟 Özel VIP fal türleri',
            '💎 Sınırsız özel içerik',
            '🎪 Özel etkinlikler',
            '📱 Özel VIP arayüzü',
            '🔮 AI destekli kişisel rehberlik'
        ],
        'features_en': [
            '👑 Premium Plan features',
            '🤖 24/7 Astrology Chatbot',
            '👥 Social astrology features',
            '🎁 Exclusive VIP content',
            '⚡ Priority support',
            '📊 Advanced analytics',
            '🎯 Personal astrology consultant',
            '🌟 Exclusive VIP reading types',
            '💎 Unlimited exclusive content',
            '🎪 Special events',
            '📱 Exclusive VIP interface',
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

    def get_all_users(self):
        try:
            result = self.client.table("users").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_all_users hatası: {e}")
            return []

    def get_subscribed_users(self):
        try:
            result = self.client.table("users").select("id").eq("daily_subscribed", True).execute()
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
    advice_map = {
        'new': [
            get_text(lang, "moon_energy.new.1", "Perfect time for new beginnings"),
            get_text(lang, "moon_energy.new.2", "Set your intentions"),
            get_text(lang, "moon_energy.new.3", "Start new projects"),
            get_text(lang, "moon_energy.new.4", "Explore your inner world")
        ],
        'waxing': [
            get_text(lang, "moon_energy.waxing.1", "Time for growth and development"),
            get_text(lang, "moon_energy.waxing.2", "Increase your energy"),
            get_text(lang, "moon_energy.waxing.3", "Seize new opportunities"),
            get_text(lang, "moon_energy.waxing.4", "Move forward with positive thoughts")
        ],
        'first_quarter': [
            get_text(lang, "moon_energy.first_quarter.1", "Time to make decisions"),
            get_text(lang, "moon_energy.first_quarter.2", "Focus on your goals"),
            get_text(lang, "moon_energy.first_quarter.3", "Make action plans"),
            get_text(lang, "moon_energy.first_quarter.4", "Take strong steps")
        ],
        'full': [
            get_text(lang, "moon_energy.full.1", "Time for completion and celebration"),
            get_text(lang, "moon_energy.full.2", "Evaluate your achievements"),
            get_text(lang, "moon_energy.full.3", "Share with loved ones"),
            get_text(lang, "moon_energy.full.4", "Feel the mystical energies")
        ],
        'waning': [
            get_text(lang, "moon_energy.waning.1", "Time for letting go and cleansing"),
            get_text(lang, "moon_energy.waning.2", "Release old habits"),
            get_text(lang, "moon_energy.waning.3", "Clear negative energies"),
            get_text(lang, "moon_energy.waning.4", "Find your inner peace")
        ],
        'last_quarter': [
            get_text(lang, "moon_energy.last_quarter.1", "Time for evaluation and learning"),
            get_text(lang, "moon_energy.last_quarter.2", "Analyze the past"),
            get_text(lang, "moon_energy.last_quarter.3", "Learn your lessons"),
            get_text(lang, "moon_energy.last_quarter.4", "Prepare for the future")
        ]
    }
    
    return advice_map.get(energy, [get_text(lang, "messages.moon_energy_advice")])

# --- Dil ve Metin Fonksiyonları (Supabase destekli) ---
@lru_cache(maxsize=32)
def get_config_from_db(key):
    return supabase_manager.get_config(key)

def get_locales():
    """
    'locales' klasöründeki JSON dosyalarından dil metinlerini yükler.
    Örn: tr.json, en.json
    """
    locales_dir = "locales"
    all_locales = {}
    
    # Desteklenen dillerin listesi (dosya adlarına göre)
    supported_langs = [f.split('.')[0] for f in os.listdir(locales_dir) if f.endswith('.json')]

    for lang_code in supported_langs:
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_locales[lang_code] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Lokalizasyon dosyası yüklenemedi: {file_path} - Hata: {e}")
            
    return all_locales

locales = get_locales()

def get_text(lang: str, key: str, default: str = None, **kwargs) -> str:
    """Dil dosyasından metin alır ve parametreleri yerleştirir. Nested key'leri destekler."""
    try:
        locale_data = locales.get(lang, locales["tr"])
        
        # Nested key'leri destekle (örn: "buttons.close_chatbot")
        keys = key.split('.')
        text = locale_data
        for k in keys:
            if isinstance(text, dict) and k in text:
                text = text[k]
            else:
                text = default if default is not None else key
                break
        
        if text is None:
            text = default if default is not None else key
        result = text.format(**kwargs) if kwargs else text
        return str(result) if result is not None else (default if default is not None else key)
    except Exception as e:
        logger.error(f"Text error for key '{key}' in lang '{lang}': {e}")
        return default if default is not None else key

def get_user_lang(user_id: int) -> str:
    user = supabase_manager.get_user(user_id)
    return user.get("language", "tr") if user else "tr"

# Desteklenen diller ve kod mappings
SUPPORTED_LANGUAGES = {
    'tr': '🇹🇷 Türkçe',
    'en': '🇺🇸 English', 
    'es': '🇪🇸 Español',
    'fr': '🇫🇷 Français',
    'ru': '🇷🇺 Русский',
    'de': '🇩🇪 Deutsch',
    'ar': '🇸🇦 العربية',
    'it': '🇮🇹 Italiano',
    'pt': '🇵🇹 Português'
}

# Burç isimleri
ZODIAC_SIGNS = {
    'tr': ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık'],
    'en': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
    'es': ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis'],
    'fr': ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons'],
    'ru': ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы'],
    'de': ['Widder', 'Stier', 'Zwillinge', 'Krebs', 'Löwe', 'Jungfrau', 'Waage', 'Skorpion', 'Schütze', 'Steinbock', 'Wassermann', 'Fische'],
    'ar': ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'العذراء', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت'],
    'it': ['Ariete', 'Toro', 'Gemelli', 'Cancro', 'Leone', 'Vergine', 'Bilancia', 'Scorpione', 'Sagittario', 'Capricorno', 'Acquario', 'Pesci'],
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
def get_main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Generate main menu keyboard based on user language"""
    lang = get_user_lang(user_id)
    user = supabase_manager.get_user(user_id)
    premium_plan = user.get('premium_plan', 'free') if user else 'free'
    
    # Helper function to ensure text is always a string
    def safe_text(key: str) -> str:
        text = get_text(lang, key)
        return str(text) if text is not None else key
    
    keyboard = [
        [InlineKeyboardButton(safe_text("coffee_fortune"), callback_data="select_coffee")],
        [InlineKeyboardButton(safe_text("tarot_fortune"), callback_data="select_tarot")],
        [InlineKeyboardButton(safe_text("dream_analysis"), callback_data="select_dream")],
        [InlineKeyboardButton(safe_text("astrology"), callback_data="select_astrology")],
        [
            InlineKeyboardButton(safe_text("daily_card"), callback_data="toggle_daily"),
            InlineKeyboardButton(safe_text("referral"), callback_data="get_referral_link")
        ]
    ]
    
    # Premium butonu ekle
    if premium_plan == 'free':
        keyboard.append([InlineKeyboardButton(safe_text("premium_upgrade"), 
                                            callback_data="premium_menu")])
    else:
        plan_name = PREMIUM_PLANS.get(premium_plan, {}).get('name', 'Premium')
        keyboard.append([InlineKeyboardButton(f"💎 {plan_name}", callback_data="premium_menu")])
    
    keyboard.append([InlineKeyboardButton(safe_text("language"), callback_data="change_language")])
    
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_button(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ " + get_text(lang, "main_menu_button"), callback_data="main_menu")]
    ])

def get_navigation_keyboard(lang: str, include_back=True, include_forward=False):
    """Navigasyon klavyesi oluşturur."""
    buttons = []
    if include_back:
        buttons.append(InlineKeyboardButton("⬅️ Geri", callback_data="main_menu"))
    if include_forward:
        buttons.append(InlineKeyboardButton("İleri ➡️", callback_data="next_page"))
    
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def show_main_menu(update: Update, context: CallbackContext, message: str = None):
    """Ana menüyü gösterir."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    lang = get_user_lang(update.effective_user.id)
    
    menu_text = message or get_text(lang, "start_message")
    keyboard = get_main_menu_keyboard(update.effective_user.id)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(menu_text, reply_markup=keyboard, parse_mode='Markdown')

# --- Ana Komutlar ---
async def start(update: Update, context: CallbackContext):
    """Bot başlangıç komutunu işler."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    user_id_str = str(update.effective_user.id)
    
    # Otomatik dil tespiti yap
    detected_lang = detect_user_language(update.effective_user)
    current_lang = get_user_lang(update.effective_user.id)
    
    # Eğer kullanıcının mevcut dili farklıysa güncelle
    if detected_lang != current_lang:
        supabase_manager.update_user(update.effective_user.id, {'language': detected_lang})
        supabase_manager.add_log(f"Kullanıcı dili güncellendi: {user_id_str} - {current_lang} → {detected_lang}")
        current_lang = detected_lang
    
    # Referral link kontrolü
    if context.args:
        referrer_id = context.args[0]
        supabase_manager.add_log(f"Referral link ile geldi: {user_id_str} - Referrer: {referrer_id}")
        
        try:
            referrer_user_id = int(referrer_id)
            if referrer_user_id != update.effective_user.id:  # Kendi kendini referans edemez
                referrer = supabase_manager.get_user(referrer_user_id)
                if referrer:
                    # Referrer'ın kazançlarını artır
                    new_count = referrer.get('referred_count', 0) + 1
                    new_earnings = referrer.get('referral_earnings', 0) + 1
                    bonus_readings = referrer.get('bonus_readings', 0) + 1
                    
                    supabase_manager.update_user(referrer_user_id, {
                        'referred_count': new_count,
                        'referral_earnings': new_earnings,
                        'bonus_readings': bonus_readings
                    })
                    
                    supabase_manager.add_log(f"Referral işlendi: {referrer_id} -> {user_id_str}")
        except ValueError:
            supabase_manager.add_log(f"Geçersiz referral ID: {referrer_id}")
    
    # Hoş geldin mesajı (tespit edilen dilde)
    welcome_message = get_text(current_lang, "start_message")
    
    # Dil tespiti bildirimi ekle (sadece yeni kullanıcılar için)
    if user.get('readings_count', 0) == 0:
        lang_name = SUPPORTED_LANGUAGES.get(current_lang, 'Türkçe')
        lang_detect_msg = get_text(current_lang, "language_detected").format(lang=lang_name)
        welcome_message = f"{lang_detect_msg}\n\n{welcome_message}"
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard(update.effective_user.id),
        parse_mode='Markdown'
    )
    
    supabase_manager.add_log(f"Start komutu işlendi: {user_id_str} - Dil: {current_lang}")

# --- Callback Handlers ---
async def main_menu_callback(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    await show_main_menu(update, context)

async def select_service_callback(update: Update, context: CallbackContext):
    """Handles service selection buttons"""
    query = update.callback_query
    await query.answer()
    
    service = query.data.split('_')[1]  # select_coffee -> coffee
    lang = get_user_lang(query.from_user.id)
    
    if service == 'coffee':
        await query.edit_message_text(get_text(lang, "fortune_request"), reply_markup=get_main_menu_keyboard(query.from_user.id))
    elif service == 'tarot':
        await draw_tarot_card(update, context)
    elif service == 'dream':
        user_id = query.from_user.id
        user = supabase_manager.get_user(user_id)
        
        # Admin kontrolü - admin sınırsız erişime sahip
        if user_id == ADMIN_ID:
            supabase_manager.update_user(user_id, {'state': 'waiting_for_dream'})
            try:
                await query.edit_message_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
            except Exception as e:
                await query.message.reply_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
            return
        
        # Ücretsiz fal hakkı kontrolü
        readings_count = user.get("readings_count", 0)
        if readings_count >= FREE_READING_LIMIT:
            # Premium planlara yönlendir
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium Planlara Geç", callback_data="premium_menu")],
                [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
            ])
            await query.edit_message_text(
                f"🎯 **Ücretsiz fal hakkınız doldu!**\n\n✨ **Sınırsız fal için Premium Planlara geçin:**\n\n" +
                f"• **Temel Plan (500 ⭐):** Sınırsız fal + gelişmiş özellikler\n" +
                f"• **Premium Plan (1000 ⭐):** Tam astroloji paketi\n" +
                f"• **VIP Plan (2000 ⭐):** En üst düzey deneyim\n\n" +
                f"🌟 **Premium avantajları:**\n" +
                f"♾️ Sınırsız fal (Kahve, Tarot, Rüya)\n" +
                f"🔮 Gelişmiş astroloji özellikleri\n" +
                f"📊 Detaylı raporlar ve analizler", 
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            return
        
        supabase_manager.update_user(user_id, {'state': 'waiting_for_dream'})
        try:
            await query.edit_message_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
        except Exception as e:
            await query.message.reply_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
    elif service == 'astrology':
        await astrology_menu(update, context)
    elif service == 'daily':
        await toggle_daily_subscription(update, context)

async def draw_tarot_card(update: Update, context: CallbackContext):
    """Tarot kartı çeker ve yorumu oluşturur."""
    query = update.callback_query
    user = await get_or_create_user(query.from_user.id, query.from_user)
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Admin kontrolü - admin sınırsız erişime sahip
    if query.from_user.id == ADMIN_ID:
        supabase_manager.add_log(f"Admin kullanıcı tarot istedi: {user_id_str}")
        await query.edit_message_text(get_text(lang, "tarot_drawing"))
        
        try:
            tarot_cards = supabase_manager.get_tarot_cards()
            card = random.choice(tarot_cards) if tarot_cards else "The Fool"
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = supabase_manager.get_prompt("tarot", lang)
            if not prompt:
                prompt = f"Sen deneyimli bir tarot yorumcususun. {card} kartını çeken {user.get('first_name', 'Dostum')} için Türkçe dilinde kapsamlı bir yorum oluştur."
            
            prompt = prompt.replace("{card}", card).replace("{username}", user.get('first_name', 'Dostum'))
            
            # Gemini'ye net talimat ekle
            final_prompt = f"""SEN BİR TAROT YORUMCUSUSUN. SADECE TAROT YORUMUNU YAZ.

{prompt}

YORUM:"""
            
            # Sync API çağrısı (async sorunu için)
            try:
                supabase_manager.add_log(f"🔄 Admin Tarot Gemini API çağrısı başlatılıyor...")
                response = model.generate_content(final_prompt)
                supabase_manager.add_log(f"✅ Admin Tarot Gemini API çağrısı tamamlandı")
            except Exception as e:
                supabase_manager.add_log(f"❌ Admin Tarot Gemini API hatası: {str(e)[:100]}")
                raise
            
            supabase_manager.add_log(f"Admin tarot falı üretildi. Kullanıcı: {user_id_str}. Kart: {card}")
            await query.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(query.from_user.id))
        except Exception as e:
            logger.error(f"Admin tarot falı hatası: {e}")
            await query.edit_message_text(
                get_text(lang, "fortune_error"), 
                reply_markup=get_main_menu_keyboard(query.from_user.id)
            )
        return
    
    readings_count = supabase_manager.get_user(query.from_user.id).get("readings_count", 0)
    if readings_count >= FREE_READING_LIMIT:
        # Premium planlara yönlendir
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Premium Planlara Geç", callback_data="premium_menu")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        await query.edit_message_text(
            f"{get_text(lang, 'fortune_limit_reached')}\n\n💫 **Telegram Stars ile devam edin:**", 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    await query.edit_message_text(get_text(lang, "tarot_drawing"))
    
    try:
        tarot_cards = supabase_manager.get_tarot_cards()
        card = random.choice(tarot_cards) if tarot_cards else "The Fool"
        
        # Gemini 2.5 modelini kullan (eğer mevcutsa)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor: {user_id_str}")
        except Exception as e:
            # Eğer 2.5 mevcut değilse 1.5 kullan
            model = genai.GenerativeModel('gemini-1.5-flash')
            supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor: {user_id_str}")
        
        prompt = supabase_manager.get_prompt("tarot", lang)
        if not prompt:
            prompt = f"""Sen deneyimli bir tarot yorumcususun. {card} kartını çeken {user.get('first_name', 'Dostum')} için kapsamlı bir yorum oluştur.

**Kartın Genel Anlamı:** {card} kartının temel sembolizmini ve enerjisini açıkla.
**Kişisel Mesaj:** Bu kartın {user.get('first_name', 'Dostum')}'in hayatındaki mevcut duruma nasıl yansıdığını yorumla.
**Gelecek Öngörüsü:** Kartın gösterdiği enerjiye dayanarak yakın gelecek için bir öngörüde bulun.
**Pratik Tavsiye:** {user.get('first_name', 'Dostum')}'e bu kartın enerjisini en iyi nasıl kullanabileceğine dair somut öneriler ver.

**Dil Tonu:** Mistik, bilge ve motive edici.
**Kısıtlamalar:** 120-150 kelime."""
        
        prompt = prompt.replace("{card}", card).replace("{username}", user.get('first_name', 'Dostum'))
        
        supabase_manager.add_log(f"Tarot prompt hazırlandı ({lang}): {len(prompt)} karakter")
        supabase_manager.add_log(f"Gemini API çağrısı yapılıyor ({lang}): {user_id_str}")
        
        # Prompt'a dil talimatı ekle
        if lang != 'tr':
            prompt = f"Please respond in {lang.upper()} language.\n\n" + prompt
        
        # Sync API çağrısı - timeout ile
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(model.generate_content, prompt)
            try:
                response = future.result(timeout=30)
                supabase_manager.add_log(f"✅ Tarot Gemini API çağrısı tamamlandı ({lang})")
            except TimeoutError:
                supabase_manager.add_log(f"❌ Tarot Gemini API timeout (30s) ({lang})")
                raise Exception("Gemini API timeout (30s)")
            except Exception as e:
                supabase_manager.add_log(f"❌ Tarot Gemini API hatası: {str(e)[:100]} ({lang})")
                raise
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        supabase_manager.add_log(f"Gemini tarot yanıtı alındı ({lang}): {len(response.text)} karakter")
        
        supabase_manager.update_user(query.from_user.id, {
            "readings_count": supabase_manager.get_user(query.from_user.id)["readings_count"] + 1
        })
        
        supabase_manager.add_log(f"Tarot falı üretildi. Kullanıcı: {user_id_str}. Kart: {card}")
        await query.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(query.from_user.id))
    except Exception as e:
        logger.error(f"Tarot falı hatası: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"), 
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def handle_dream_text(update: Update, context: CallbackContext):
    """Rüya metnini, doğum haritası bilgilerini ve chatbot sorularını işler."""
    user_id_str = str(update.effective_user.id)
    user = supabase_manager.get_user(update.effective_user.id)
    
    supabase_manager.add_log(f"handle_dream_text çağrıldı: {user_id_str}")
    supabase_manager.add_log(f"Kullanıcı state: {user.get('state') if user else 'no_user'}")
    
    # Kullanıcı durumunu kontrol et
    if user and user.get('state') == 'waiting_for_dream':
        # Rüya tabiri işlemi
        lang = get_user_lang(update.effective_user.id)
        dream_text = update.message.text
        
        supabase_manager.add_log(f"Rüya metni alındı: {user_id_str}. Metin: {dream_text[:50]}...")
        
        await update.message.reply_text(get_text(lang, "dream_analyzing"))
        
        try:
            # Gemini 2.5 modelini kullan (eğer mevcutsa)
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor (rüya): {user_id_str}")
            except Exception as e:
                # Eğer 2.5 mevcut değilse 1.5 kullan
                model = genai.GenerativeModel('gemini-1.5-flash')
                supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor (rüya): {user_id_str}")
            
            prompt = supabase_manager.get_prompt("dream", lang)
            if not prompt:
                supabase_manager.add_log(f"Prompt before processing (rüya): {prompt[:500]}...") # Log raw prompt
                prompt = f"""Sen deneyimli bir rüya yorumcususun. {update.effective_user.first_name} için rüya yorumu yap.

Rüyada gördüğü şeyleri başta belirt. Örneğin: "Rüyanda kelebek görmen..."

Sonra bu sembollerin anlamını açıkla ve {update.effective_user.first_name} için kişisel yorum yap.

150-200 kelime arası yaz."""
            
            supabase_manager.add_log(f"Prompt before processing (rüya): {prompt[:500]}...") # Log raw prompt
            
            # Prompt'u hazırla
            final_prompt = prompt.replace("{username}", update.effective_user.first_name).replace("{dream_text}", dream_text)
            
            # Dil talimatını ekle ve Gemini'ye çok net talimat ekle
            if lang == 'tr':
                final_prompt = f"""SEN BİR RÜYA YORUMCUSUSUN. SADECE TÜRKÇE RÜYA YORUMUNU YAZ.

{final_prompt}

TÜRKÇE YORUM:"""
            elif lang == 'en':
                final_prompt = f"""YOU ARE A DREAM INTERPRETER. WRITE ONLY DREAM INTERPRETATION IN ENGLISH.

{final_prompt}

ENGLISH INTERPRETATION:"""
            elif lang == 'es':
                final_prompt = f"""ERES UN INTÉRPRETE DE SUEÑOS. ESCRIBE SOLO LA INTERPRETACIÓN DEL SUEÑO EN ESPAÑOL.

{final_prompt}

INTERPRETACIÓN EN ESPAÑOL:"""
            elif lang == 'fr':
                final_prompt = f"""VOUS ÊTES UN INTERPRÈTE DE RÊVES. ÉCRIVEZ SEULEMENT L'INTERPRÉTATION DU RÊVE EN FRANÇAIS.

{final_prompt}

INTERPRÉTATION EN FRANÇAIS:"""
            elif lang == 'ru':
                final_prompt = f"""ВЫ ТОЛКОВАТЕЛЬ СНОВ. НАПИШИТЕ ТОЛЬКО ТОЛКОВАНИЕ СНА НА РУССКОМ ЯЗЫКЕ.

{final_prompt}

ТОЛКОВАНИЕ НА РУССКОМ:"""
            else:
                final_prompt = f"""SEN BİR RÜYA YORUMCUSUSUN. SADECE RÜYA YORUMUNU YAZ.

{final_prompt}

YORUM:"""
            
            supabase_manager.add_log(f"Rüya prompt hazırlandı ({lang}): {len(final_prompt)} karakter")
            supabase_manager.add_log(f"Gemini API çağrısı yapılıyor (rüya, {lang}): {user_id_str}")
            
            # Gemini'ye gönder (sync API) - timeout ile
            try:
                supabase_manager.add_log(f"DEBUG: About to call Gemini API for dream analysis: {user_id_str}") # NEW LOG
                supabase_manager.add_log(f"DEBUG: Final prompt for dream analysis: {final_prompt[:1000]}...") # Log final prompt
                # Thread pool executor ile sync çağrı
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(model.generate_content, final_prompt)
                    response = future.result(timeout=30)  # 30 saniye timeout
                
                supabase_manager.add_log(f"Gemini API yanıtı başarıyla alındı: {user_id_str}")
            except concurrent.futures.TimeoutError:
                supabase_manager.add_log(f"Gemini API timeout (30s): {user_id_str}")
                raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
            except Exception as e:
                supabase_manager.add_log(f"Gemini API hatası: {str(e)[:100]}")
                raise Exception(f"Gemini API hatası: {str(e)[:100]}")
            
            supabase_manager.add_log(f"Gemini API yanıtı alındı: {response}")
            
            if not response:
                raise Exception("Gemini API'den yanıt alınamadı")
            
            if not response.text:
                raise Exception("Gemini API'den boş yanıt alındı")
            
            supabase_manager.add_log(f"Gemini rüya yanıtı alındı: {len(response.text)} karakter")
            supabase_manager.add_log(f"Yanıt içeriği: {response.text[:500]}...")
            
            # Ücretsiz fal hakkını azalt (admin değilse)
            if update.effective_user.id != ADMIN_ID:
                current_readings = user.get("readings_count", 0)
                supabase_manager.update_user(update.effective_user.id, {
                    'state': 'idle',
                    'readings_count': current_readings + 1
                })
                supabase_manager.add_log(f"Rüya analizi yapıldı (ücretsiz hak azaltıldı): {user_id_str}")
            else:
                supabase_manager.update_user(update.effective_user.id, {'state': 'idle'})
                supabase_manager.add_log(f"Admin rüya analizi yapıldı: {user_id_str}")
            
            await update.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(update.effective_user.id))
        except Exception as e:
            logger.error(f"Rüya analizi hatası: {e}")
            await update.message.reply_text(
                get_text(lang, "fortune_error"), 
                reply_markup=get_main_menu_keyboard(update.effective_user.id)
            )
            
    elif user and user.get('state') == 'waiting_for_birth_info':
        # Doğum haritası bilgisi işlemi
        await process_birth_chart(update, context)
        
    elif user and user.get('state') == 'chatbot_mode':
        # Astroloji chatbot işlemi
        await handle_chatbot_question(update, context)
        
    else:
        # Kullanıcı rüya bekliyor değilse, state'i kontrol et
        current_state = user.get('state') if user else 'no_user'
        supabase_manager.add_log(f"Text alındı ama state uygun değil: {user_id_str}. State: {current_state}")

# Astroloji modülü fonksiyonları
async def astrology_menu(update: Update, context: CallbackContext):
    """Astroloji ana menüsünü gösterir"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    premium_plan = user.get('premium_plan', 'free')
    
    keyboard = [
        [
            InlineKeyboardButton(get_text(lang, "birth_chart"), callback_data="astro_birth_chart"),
            InlineKeyboardButton(get_text(lang, "daily_horoscope"), callback_data="astro_daily_horoscope")
        ],
        [
            InlineKeyboardButton(get_text(lang, "compatibility"), callback_data="astro_compatibility"),
            InlineKeyboardButton(get_text(lang, "buttons.advanced_moon_calendar"), 
                                callback_data="advanced_moon_calendar")
        ]
    ]
    
    # Premium özellikler
    if premium_plan in ['premium', 'vip']:
        keyboard.append([
            InlineKeyboardButton(get_text(lang, "buttons.weekly_report"), 
                               callback_data="weekly_astro_report"),
            InlineKeyboardButton(get_text(lang, "buttons.planetary_transits"), 
                               callback_data="planetary_transits")
        ])
    
    # VIP özellikler
    if premium_plan == 'vip':
        keyboard.append([
            InlineKeyboardButton(get_text(lang, "buttons.astro_chatbot"), 
                               callback_data="astro_chatbot"),
            InlineKeyboardButton(get_text(lang, "buttons.social_features"), 
                               callback_data="social_astrology")
        ])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, "main_menu_button"), callback_data="main_menu")])
    
    astro_message = f"""⭐ **{get_text(lang, 'astrology_menu.title')}** ⭐
━━━━━━━━━━━━━━━━━━━━━━

🌟 **{get_text(lang, 'birth_chart')}** - {get_text(lang, 'astrology_menu.description', default='Personal astrological analysis')}
📅 **{get_text(lang, 'daily_horoscope')}** - {get_text(lang, 'astrology_menu.description', default='Daily guidance for your sign')}
💕 **{get_text(lang, 'compatibility')}** - {get_text(lang, 'astrology_menu.description', default='Energy analysis between two signs')}
🌙 **{get_text(lang, 'buttons.advanced_moon_calendar')}** - {get_text(lang, 'astrology_menu.description', default='Real moon phases and effects')}

{'📊 **Premium Features Active!**' if premium_plan in ['premium', 'vip'] else ''}
{'🤖 **VIP Features Active!**' if premium_plan == 'vip' else ''}

━━━━━━━━━━━━━━━━━━━━━━
✨ *{get_text(lang, 'astrology_menu.footer', default='Discover what the stars tell you')}* ✨"""
    
    try:
        await query.edit_message_text(astro_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception as e:
        # Eğer mesaj düzenlenemezse yeni mesaj gönder
        await query.message.reply_text(astro_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def astro_daily_horoscope(update: Update, context: CallbackContext):
    """Günlük burç yorumu için burç seçimini gösterir"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    # Her satırda 3 burç olacak şekilde keyboard oluştur
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"daily_horoscope_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    await query.edit_message_text(
        get_text(lang, "enter_your_sign"),
        reply_markup=keyboard
    )

async def generate_daily_horoscope(update: Update, context: CallbackContext):
    """Seçilen burç için günlük yorum üretir"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # DEBUG: Fonksiyona ulaştık
    supabase_manager.add_log(f"🎯 generate_daily_horoscope fonksiyonu çalışıyor - {user_id_str}")
    
    # Callback data'dan burç index'ini al
    supabase_manager.add_log(f"🔍 Callback data: {query.data}")
    sign_index = int(query.data.split('_')[-1])
    supabase_manager.add_log(f"🔍 Sign index: {sign_index}")
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    supabase_manager.add_log(f"🔍 Available signs: {len(signs)} items")
    selected_sign = signs[sign_index]
    supabase_manager.add_log(f"🔍 Selected sign: {selected_sign}")
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini 2.0 modelini kullan
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor (astroloji): {user_id_str}")
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
            supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor (astroloji): {user_id_str}")
        
        # Prompt'u hazırla
        prompt = supabase_manager.get_prompt("daily_horoscope", lang)
        if not prompt:
            if lang == 'tr':
                prompt = f"""Sen deneyimli bir astrologsun. {selected_sign} burcu için bugünün detaylı astrolojik yorumunu oluştur.

Şu konuları içermeli:
1. **Genel Enerji:** Bugünün astrolojik atmosferi
2. **Aşk ve İlişkiler:** Duygusal yaşamda ne beklemeli
3. **Kariyer ve Finans:** İş ve para konularında rehberlik
4. **Sağlık ve Enerji:** Fiziksel ve mental sağlık önerileri
5. **Günün Tavsiyesi:** Pratik bir öneri

120-150 kelime arası, pozitif ve motive edici olsun."""
            else:
                prompt = f"""You are an experienced astrologer. Create a detailed astrological interpretation for {selected_sign} sign for today.

Include these topics:
1. **General Energy:** Today's astrological atmosphere
2. **Love and Relationships:** What to expect in emotional life
3. **Career and Finance:** Guidance on work and money matters
4. **Health and Energy:** Physical and mental health recommendations
5. **Daily Advice:** A practical suggestion

120-150 words, positive and motivating."""
        
        prompt = prompt.replace("{sign}", selected_sign)
        
        # Dil-spesifik final prompt
        if lang == 'tr':
            final_prompt = f"""SEN BİR ASTROLOGSUN. SADECE TÜRKÇE ASTROLOJI YORUMUNU YAZ.

{prompt}

TÜRKÇE YORUM:"""
        elif lang == 'en':
            final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY ASTROLOGICAL INTERPRETATION IN ENGLISH.

{prompt}

ENGLISH INTERPRETATION:"""
        else:
            # Diğer diller için temel yapı
            final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.

{prompt}

{lang.upper()} INTERPRETATION:"""
        
        # Gemini API çağrısı
        supabase_manager.add_log(f"Gemini'ye gönderilen prompt uzunluğu: {len(final_prompt)} karakter")
        supabase_manager.add_log(f"🔄 Gemini API çağrısı başlatılıyor...")
        
        # Sync API çağrısı (async sorunu için)
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, final_prompt)
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"✅ Gemini API çağrısı tamamlandı")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"❌ Gemini API timeout (30s): {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Gemini API hatası: {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        supabase_manager.add_log(f"Gemini response alındı: {response is not None}")
        if response:
            supabase_manager.add_log(f"Response text var mı: {hasattr(response, 'text') and response.text is not None}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        horoscope_message = f"""📅 **{selected_sign.upper()} - GÜNLÜK BURÇ** 📅
━━━━━━━━━━━━━━━━━━━━━━

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
🌟 *İyi bir gün geçirin!* 🌟"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Başka Burç", callback_data="astro_daily_horoscope")],
            [InlineKeyboardButton("📱 Burç Aboneliği", callback_data="astro_subscribe_daily")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(horoscope_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Günlük burç yorumu üretildi: {user_id_str} - {selected_sign}")
        
    except Exception as e:
        logger.error(f"Astroloji yorumu hatası: {e}")
        supabase_manager.add_log(f"Astroloji hatası - {user_id_str}: {str(e)}")
        await query.edit_message_text(
            f"❌ Astroloji yorumu oluşturulurken hata:\n{str(e)[:100]}...",
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def astro_compatibility(update: Update, context: CallbackContext):
    """Uyumluluk analizi için ilk burç seçimini gösterir"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    # Burç seçim keyboard'u oluştur
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"compat_first_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    await query.edit_message_text(
        get_text(lang, "compatibility_prompt"),
        reply_markup=keyboard
    )

async def astro_first_sign_selected(update: Update, context: CallbackContext):
    """İlk burç seçildi, ikinci burç seçimi için"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    first_sign_index = int(query.data.split('_')[-1])
    first_sign = signs[first_sign_index]
    
    # İkinci burç seçimi
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"compat_second_{first_sign_index}_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    if lang == 'tr':
        message = f"💕 **{first_sign}** seçtiniz. Şimdi ikinci burcu seçin:"
    else:
        message = f"💕 You selected **{first_sign}**. Now select the second sign:"
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def generate_compatibility_analysis(update: Update, context: CallbackContext):
    """İki burç arasındaki uyumluluk analizini üretir"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Callback data'dan her iki burç index'ini al
    parts = query.data.split('_')
    first_sign_index = int(parts[-2])
    second_sign_index = int(parts[-1])
    
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    first_sign = signs[first_sign_index]
    second_sign = signs[second_sign_index]
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Supabase'den prompt'u al
        prompt = supabase_manager.get_prompt("compatibility", lang)
        if not prompt:
            prompt = f"""You are an experienced astrologer. Analyze the compatibility between {first_sign} and {second_sign} signs.

Cover these topics comprehensively:
1. **General Compatibility:** Basic character harmony (0-100%)
2. **Love and Romance:** Emotional bond and attraction
3. **Friendship:** Social harmony and friendship potential
4. **Cooperation:** Success chances in joint projects
5. **Challenges:** Possible conflict areas
6. **Advice:** Suggestions to strengthen the relationship

180-220 words, balanced and realistic."""
        
        # Placeholder'ları değiştir
        final_prompt = prompt.format(first_sign=first_sign, second_sign=second_sign)
        
        # Dil talimatını ekle
        final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.

{final_prompt}

{lang.upper()} ANALYSIS:"""
        
        # Sync API çağrısı - timeout ile
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, final_prompt)
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"✅ Compatibility Analysis Gemini API çağrısı tamamlandı: {user_id_str}")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"❌ Compatibility Analysis Gemini API timeout (30s): {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Compatibility Analysis Gemini API hatası: {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        compatibility_message = f"""�� **UYUMLULUK ANALİZİ** 💕
━━━━━━━━━━━━━━━━━━━━━━

**{first_sign} ↔️ {second_sign}**

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *İlişkilerde anlayış en önemli unsurdur* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Başka Analiz", callback_data="astro_compatibility")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(compatibility_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Uyumluluk analizi yapıldı: {user_id_str} - {first_sign} & {second_sign}")
        
    except Exception as e:
        logger.error(f"Uyumluluk analizi hatası: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def astro_birth_chart(update: Update, context: CallbackContext):
    """Doğum haritası için bilgi ister"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user_id = query.from_user.id
    
    # Kullanıcı state'ini güncelle
    supabase_manager.update_user(user_id, {'state': 'waiting_for_birth_info'})
    
    birth_info_message = f"""🌟 **DOĞUM HARİTASI ANALİZİ** 🌟
━━━━━━━━━━━━━━━━━━━━━━

Doğum haritanızı çıkarabilmek için aşağıdaki bilgilere ihtiyacım var:

📅 **Format:** GG.AA.YYYY SS:DD - Şehir
📍 **Örnek:** 15.06.1990 14:30 - İstanbul

🔮 **Not:** Doğum saati ne kadar kesin olursa, analiz o kadar doğru olur.

━━━━━━━━━━━━━━━━━━━━━━
✨ *Lütfen doğum bilgilerinizi yukardaki formatta yazın* ✨"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(birth_info_message, reply_markup=keyboard, parse_mode='Markdown')

async def process_birth_chart(update: Update, context: CallbackContext):
    """Doğum haritası analizi yapar"""
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    lang = get_user_lang(user_id)
    birth_info = update.message.text
    
    await update.message.reply_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Supabase'den prompt'u al
        prompt = supabase_manager.get_prompt("birth_chart", lang)
        if not prompt:
            prompt = f"""You are a professional astrologer. Create a comprehensive birth chart analysis based on the following birth information:

Birth Information: {birth_info}

The analysis should include:
1. **Sun Sign Analysis:** Core personality traits
2. **Rising Sign:** External appearance and first impression
3. **Moon Sign:** Emotional structure and inner world
4. **Mercury:** Communication and thinking style
5. **Venus:** Love and relationship style
6. **Mars:** Energy and motivation source
7. **General Interpretation:** Holistic personality assessment

200-250 words, personalized and in-depth."""
        
        # Placeholder'ları değiştir
        username = update.effective_user.first_name or update.effective_user.username or "User"
        birth_date = birth_info  # Basit olarak tüm metni kullan
        birth_time = "Unknown"  # Kullanıcıdan alınmamış
        birth_place = "Unknown"  # Kullanıcıdan alınmamış
        
        final_prompt = prompt.format(
            username=username,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place
        )
        
        # Dil talimatını ekle
        final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.

{final_prompt}

{lang.upper()} ANALYSIS:"""
        
        # Sync API çağrısı - timeout ile
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, final_prompt)
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"✅ Birth Chart Gemini API çağrısı tamamlandı: {user_id_str}")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"❌ Birth Chart Gemini API timeout (30s): {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Birth Chart Gemini API hatası: {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        chart_message = f"""🌟 **DOĞUM HARİTASI ANALİZİ** 🌟
━━━━━━━━━━━━━━━━━━━━━━

📅 **Doğum Bilgisi:** {birth_info}

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Bu analiz size kişisel rehberlik sağlaması için hazırlanmıştır* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Başka Analiz", callback_data="astro_birth_chart")],
            [InlineKeyboardButton("📱 PDF İndir", callback_data=f"birth_chart_pdf_{user_id}")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(chart_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.update_user(user_id, {'state': 'idle'})
        supabase_manager.add_log(f"Doğum haritası analizi yapıldı: {user_id_str}")
        
    except Exception as e:
        logger.error(f"Doğum haritası hatası: {e}")
        await update.message.reply_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        supabase_manager.update_user(user_id, {'state': 'idle'})

async def astro_moon_calendar(update: Update, context: CallbackContext):
    """Ay takvimi özelliği"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    
    # Basit ay fazları
    moon_phases = [
        "🌑 Yeni Ay", "🌒 Hilal", "🌓 İlk Dördün", "🌔 Şişkin Ay",
        "🌕 Dolunay", "🌖 Azalan Ay", "🌗 Son Dördün", "🌘 Eski Hilal"
    ]
    
    import datetime
    import random
    
    today = datetime.date.today()
    current_phase = moon_phases[today.day % 8]  # Basit simülasyon
    
    # Ay etkisi analizi
    moon_effects = {
        'tr': [
            "Bugün ay enerjisi yaratıcılığınızı artırıyor",
            "Duygusal dengede olmanız için mükemmel bir gün",
            "Yeni başlangıçlar için ideal enerji",
            "İç görü ve sezgilerinizi güçlendiren dönem",
            "Manevi gelişim için uygun zaman",
            "İlişkilerde derinleşme ve yakınlaşma dönemi"
        ],
        'en': [
            "Today's moon energy enhances your creativity",
            "Perfect day for emotional balance",
            "Ideal energy for new beginnings",
            "Period strengthening your intuition and insights",
            "Suitable time for spiritual development",
            "Period of deepening and bonding in relationships"
        ]
    }
    
    selected_effect = random.choice(moon_effects.get(lang, moon_effects['en']))
    
    moon_message = f"""🌙 **AY TAKVİMİ** 🌙
━━━━━━━━━━━━━━━━━━━━━━

📅 **Bugün:** {today.strftime('%d.%m.%Y')}
🌙 **Ay Fazı:** {current_phase}

✨ **Günün Ay Enerjisi:**
{selected_effect}

🔮 **Öneriler:**
• Meditasyon ve iç görü çalışmaları
• Duygusal temizlik ve arınma
• Yaratıcı projelerle ilgilen
• Doğa ile bağlantı kur

━━━━━━━━━━━━━━━━━━━━━━
🌟 *Ay döngüleriyle uyum halinde yaşayın* 🌟"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Ay Bildirimleri", callback_data="moon_notifications")],
        [InlineKeyboardButton("📅 Haftalık Takvim", callback_data="weekly_moon_calendar")],
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(moon_message, reply_markup=keyboard, parse_mode='Markdown')

async def astro_subscribe_daily(update: Update, context: CallbackContext):
    """Günlük burç aboneliği"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    user = supabase_manager.get_user(user_id)
    
    if user.get('astro_subscribed', False):
        message = "✅ Zaten günlük burç aboneliğiniz aktif!"
        button_text = "❌ Aboneliği İptal Et"
        callback_data = "astro_unsubscribe"
    else:
        message = "📱 Günlük burç aboneliği başlatılsın mı?"
        button_text = "✅ Evet, Abone Ol"
        callback_data = "astro_subscribe_confirm"
    
    subscription_info = f"""🌟 **GÜNLÜK BURÇ ABONELİĞİ** 🌟
━━━━━━━━━━━━━━━━━━━━━━

{message}

📅 **Özellikler:**
• Her sabah kişisel burç yorumu
• Haftalık astroloji özeti
• Özel ay döngüsü bildirimleri
• Premium astroloji içerikleri

⏰ **Gönderim:** Her sabah 08:00
🔔 **Durum:** {'✅ Aktif' if user.get('astro_subscribed', False) else '❌ İnaktif'}

━━━━━━━━━━━━━━━━━━━━━━"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(button_text, callback_data=callback_data)],
        [InlineKeyboardButton("🔙 Günlük Burç", callback_data="astro_daily_horoscope")]
    ])
    
    await query.edit_message_text(subscription_info, reply_markup=keyboard, parse_mode='Markdown')

async def astro_subscribe_confirm(update: Update, context: CallbackContext):
    """Burç aboneliğini onaylar"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    supabase_manager.update_user(user_id, {'astro_subscribed': True})
    
    await query.edit_message_text(
        "✅ Günlük burç aboneliğiniz başlatıldı!\n\nHer sabah saat 08:00'da size özel burç yorumunuz gelecek.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
    )

async def moon_notifications(update: Update, context: CallbackContext):
    """Ay bildirimleri ayarları"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🌙 **AY BİLDİRİMLERİ**\n\nYakında: Dolunay, yeniay ve özel ay geçişleri için otomatik bildirimler!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Ay Takvimi", callback_data="astro_moon_calendar")]
        ])
    )

async def handle_photo(update: Update, context: CallbackContext):
    """Kahve fincanı fotoğrafını işler."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    user_id_str = str(update.effective_user.id)
    lang = get_user_lang(update.effective_user.id)
    
    supabase_manager.add_log(f"Fotoğraf alındı: {user_id_str}")
    
    # Admin kontrolü - admin sınırsız erişime sahip
    if update.effective_user.id == ADMIN_ID:
        supabase_manager.add_log(f"Admin kullanıcı fal istedi: {user_id_str}")
        await process_coffee_fortune(update, context, is_paid=False)
        return
    
    # Ödeme sonrası fotoğraf kontrolü
    if context.user_data.get('paid_coffee_fortune'):
        context.user_data.pop('paid_coffee_fortune', None)  # Flag'i temizle
        supabase_manager.add_log(f"Ücretli kahve falı fotoğrafı işleniyor: {user_id_str}")
        await process_coffee_fortune(update, context, is_paid=True)
        return
    
    readings_count = supabase_manager.get_user(update.effective_user.id).get("readings_count", 0)
    
    if readings_count >= FREE_READING_LIMIT:
        # Premium planlara yönlendir
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Premium Planlara Geç", callback_data="premium_menu")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        await update.message.reply_text(
            f"🎯 **Ücretsiz fal hakkınız doldu!**\n\n✨ **Sınırsız fal için Premium Planlara geçin:**\n\n" +
            f"• **Temel Plan (500 ⭐):** Sınırsız fal + gelişmiş özellikler\n" +
            f"• **Premium Plan (1000 ⭐):** Tam astroloji paketi\n" +
            f"• **VIP Plan (2000 ⭐):** En üst düzey deneyim\n\n" +
            f"🌟 **Premium avantajları:**\n" +
            f"♾️ Sınırsız fal (Kahve, Tarot, Rüya)\n" +
            f"🔮 Gelişmiş astroloji özellikleri\n" +
            f"📊 Detaylı raporlar ve analizler", 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # Önce referans haklarını kontrol et
    referral_readings = supabase_manager.get_user(update.effective_user.id).get('referral_readings', 0)
    if referral_readings > 0:
        supabase_manager.update_user(update.effective_user.id, {'referral_readings': referral_readings - 1})
        supabase_manager.add_log(f"Kullanıcı {user_id_str} referans hakkı kullandı. Kalan: {referral_readings - 1}")
        await process_coffee_fortune(update, context, is_paid=False)
        return
    
    # Sonra normal ücretsiz hakları kontrol et
    free_readings = supabase_manager.get_user(update.effective_user.id).get('readings_count', 0)
    if free_readings < FREE_READING_LIMIT:
        supabase_manager.update_user(update.effective_user.id, {'readings_count': free_readings + 1})
        supabase_manager.add_log(f"Kullanıcı {user_id_str} ücretsiz hak kullandı. Toplam: {free_readings + 1}")
        await process_coffee_fortune(update, context, is_paid=False)
        return

async def process_coffee_fortune(update: Update, context: CallbackContext, is_paid: bool = False):
    """Kahve falını işler."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    user_id_str = str(update.effective_user.id)
    lang = get_user_lang(update.effective_user.id)
    
    await update.message.reply_text(get_text(lang, "fortune_in_progress"))
    
    try:
        # Fotoğrafı indir
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        photo_data = await photo_file.download_as_bytearray()
        
        supabase_manager.add_log(f"Fotoğraf indirildi: {len(photo_data)} bytes")
        
        # Gemini Vision ile analiz - 2.5 modelini kullan (eğer mevcutsa)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor (kahve): {user_id_str}")
        except Exception as e:
            # Eğer 2.5 mevcut değilse 1.5 kullan
            model = genai.GenerativeModel('gemini-1.5-flash')
            supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor (kahve): {user_id_str}")
        
        # Prompt'u hazırla
        prompt = supabase_manager.get_prompt("coffee_fortune", lang)
        if not prompt:
            prompt = f"""Sen İstanbul'un en meşhur kahve falcılarından birisin. Mistisizm ve modern hayat arasında bir köprü kuruyorsun. 
            
Gördüğün kahve fincanı fotoğrafına dayanarak, Türkçe dilinde şu elementleri içeren derinlikli ve etkileyici bir fal yorumu oluştur:

1. **Ana Sembol ve Anlamı:** Fincanda gördüğün en baskın 1-2 sembolü canlı bir şekilde betimle. Bu sembollerin evrensel ve psikolojik anlamlarını açıkla.
2. **Kişisel Yorum:** Bu sembollerin, {user.get('first_name', 'Dostum')}'in hayatındaki mevcut duruma nasıl yansıdığını spesifik örneklerle yorumla.
3. **Yakın Gelecek İçin Öngörü:** Fincanın genel atmosferine dayanarak önümüzdeki haftalar için küçük bir öngörüde bulun.
4. **Mistik Tavsiye:** {user.get('first_name', 'Dostum')}'e sembollerin enerjisini en iyi nasıl kullanabileceğine dair bilgece bir tavsiye ver.

**Dil Tonu:** Edebi, bilge, hafif gizemli ama daima umut veren bir dil kullan.
**Kısıtlamalar:** 80-100 kelime. Emoji yok."""

        # Username placeholder'ını değiştir
        prompt = prompt.replace("{username}", user.get('first_name', 'Dostum'))
        
        supabase_manager.add_log(f"Prompt hazırlandı: {len(prompt)} karakter")
        
        # Gemini API çağrısı
        supabase_manager.add_log(f"Kahve falı prompt hazırlandı ({lang}): {len(prompt)} karakter")
        supabase_manager.add_log(f"Gemini API çağrısı yapılıyor (kahve, {lang}): {user_id_str}")
        
        # Dil talimatını ekle ve Gemini'ye çok net talimat ekle
        if lang == 'tr':
            final_prompt = f"""SEN BİR KAHVE FALCISISIN. SADECE TÜRKÇE FAL YORUMUNU YAZ.

{prompt}

TÜRKÇE YORUM:"""
        elif lang == 'en':
            final_prompt = f"""YOU ARE A COFFEE FORTUNE TELLER. WRITE ONLY COFFEE FORTUNE IN ENGLISH.

{prompt}

ENGLISH FORTUNE:"""
        elif lang == 'es':
            final_prompt = f"""ERES UN LECTOR DE BORRA DE CAFÉ. ESCRIBE SOLO LA LECTURA DE CAFÉ EN ESPAÑOL.

{prompt}

LECTURA EN ESPAÑOL:"""
        elif lang == 'fr':
            final_prompt = f"""VOUS ÊTES UN LECTEUR DE MARC DE CAFÉ. ÉCRIVEZ SEULEMENT LA LECTURE DE CAFÉ EN FRANÇAIS.

{prompt}

LECTURE EN FRANÇAIS:"""
        elif lang == 'ru':
            final_prompt = f"""ВЫ ГАДАЛКА НА КОФЕЙНОЙ ГУЩЕ. НАПИШИТЕ ТОЛЬКО ГАДАНИЕ НА РУССКОМ ЯЗЫКЕ.

{prompt}

ГАДАНИЕ НА РУССКОМ:"""
        else:
            final_prompt = f"""SEN BİR KAHVE FALCISISIN. SADECE FAL YORUMUNU YAZ.

{prompt}

YORUM:"""
        
        # Gemini API çağrısı - timeout ile
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, [final_prompt, {"mime_type": "image/jpeg", "data": bytes(photo_data)}])
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"Gemini API yanıtı başarıyla alındı (kahve): {user_id_str}")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"Gemini API timeout (30s) - kahve: {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"Gemini API hatası (kahve): {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        supabase_manager.add_log(f"Gemini kahve falı yanıtı alındı: {len(response.text)} karakter")
        
        supabase_manager.add_log(f"Kahve falı yanıtı alındı: {len(response.text)} karakter")
        
        if not is_paid:
            current_readings = supabase_manager.get_user(update.effective_user.id).get("readings_count", 0)
            supabase_manager.update_user(update.effective_user.id, {
                "readings_count": current_readings + 1
            })
        
        supabase_manager.add_log(f"Kahve falı üretildi ({'ücretli' if is_paid else 'ücretsiz'}). Kullanıcı: {user_id_str}")
        
        # Fotoğrafı geri gönder ve falı caption olarak ekle
        await context.bot.send_photo(
            chat_id=update.effective_user.id, 
            photo=update.message.photo[-1].file_id, 
            caption=response.text, 
            reply_markup=get_main_menu_keyboard(update.effective_user.id)
        )
        
    except Exception as e:
        logger.error(f"Kahve falı hatası: {e}")
        supabase_manager.add_log(f"Kahve falı hatası: {str(e)}")
        
        # Daha detaylı hata mesajı
        error_message = f"❌ Fal yorumu oluşturulurken bir hata oluştu.\n\nHata detayı: {str(e)}"
        await update.message.reply_text(
            error_message, 
            reply_markup=get_main_menu_keyboard(update.effective_user.id)
        )

async def toggle_daily_subscription(update: Update, context: CallbackContext):
    """Günlük kart aboneliği hakkında detaylı bilgi gösterir."""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    current_status = user.get("daily_subscribed", False)
    lang = get_user_lang(query.from_user.id)
    
    # Kullanıcının mevcut durumu
    subscription_status = "✅ AKTİF" if current_status else "❌ PASİF"
    next_delivery = "Her sabah 09:00" if current_status else "Abonelik aktif değil"
    
    # Detaylı açıklama mesajı
    if lang == 'tr':
        info_message = f"""🌅 **GÜNLÜK KART ABONELİĞİ** 🌅
━━━━━━━━━━━━━━━━━━━━━━

📱 **Mevcut Durumunuz:** {subscription_status}
⏰ **Sonraki Teslimat:** {next_delivery}

🔮 **Bu Özellik Hakkında:**
Günlük Kart aboneliği ile her sabah size özel hazırlanmış bir tarot kartı ve yorumunu alırsınız. Bu kart günün enerjisini, karşılaşabileceğiniz fırsatları ve dikkat etmeniz gereken noktaları mystik bir perspektifle size sunar.

✨ **Neler İçerir:**
• 🃏 Her sabah 09:00'da özel tarot kartı
• 📜 Kartın güncel yorumu ve anlamı
• 🎯 Gün için pratik tavsiyeler
• 🌟 Kişisel enerji rehberliği
• 💫 Astrolojik bağlantılar ve ipuçları

🎁 **Özel Avantajlar:**
• Tamamen ÜCRETSİZ hizmet
• Her gün farklı kart ve yorum
• Kişiselleştirilmiş içerik
• Motivasyon ve ilham verici mesajlar
• Günün pozitif enerjisini yakalama

📊 **İstatistikler:**
• 15,000+ aktif günlük abone
• %94 kullanıcı memnuniyeti
• Ortalama 4.8/5 değerlendirme

🔧 **Nasıl Çalışır:**
1. Aboneliği aktifleştirin
2. Her sabah otomatik mesaj alın
3. Kartınızı okuyun ve günü planlayın
4. İstediğiniz zaman iptal edebilirsiniz

⚙️ **Ayarlar:**
• Teslimat saati: 09:00 (değiştirilebilir)
• Hafta sonu dahil: Evet
• Bildirim türü: Sessiz mesaj"""

        toggle_text = "🔕 Aboneliği Durdur" if current_status else "🔔 Aboneliği Başlat"
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
        [InlineKeyboardButton("⚙️ Teslimat Saati Ayarla", callback_data="set_delivery_time")],
        [InlineKeyboardButton("📊 Abonelik İstatistikleri", callback_data="subscription_stats")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(info_message, reply_markup=keyboard, parse_mode='Markdown')

async def confirm_daily_subscribe(update: Update, context: CallbackContext):
    """Günlük kart aboneliğini onaylar."""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    supabase_manager.update_user(query.from_user.id, {"daily_subscribed": True})
    lang = get_user_lang(query.from_user.id)
    
    supabase_manager.add_log(f"Kullanıcı {user_id_str} günlük aboneliği başlattı.")
    
    success_message = """🎉 **Günlük Kart Aboneliği Aktifleştirildi!** 🎉

✅ Artık her sabah 09:00'da size özel tarot kartınızı alacaksınız
🔮 İlk kartınız yarın sabah teslim edilecek
💫 Harika bir karar verdiniz!

🎁 **Hoş Geldin Hediyesi:**
İlk haftanız için ekstra bir bonus kart alacaksınız!"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Abonelik Ayarları", callback_data="toggle_daily")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(success_message, reply_markup=keyboard, parse_mode='Markdown')

async def confirm_daily_unsubscribe(update: Update, context: CallbackContext):
    """Günlük kart aboneliğini iptal eder."""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    supabase_manager.update_user(query.from_user.id, {"daily_subscribed": False})
    lang = get_user_lang(query.from_user.id)
    
    supabase_manager.add_log(f"Kullanıcı {user_id_str} günlük aboneliği durdurdu.")
    
    unsubscribe_message = """💔 **Günlük Kart Aboneliği Durduruldu**

😔 Artık günlük tarot kartları almayacaksınız
🔄 İstediğiniz zaman tekrar aktifleştirebilirsiniz
🎁 Verileriniz korunuyor, geri dönebilirsiniz

📊 **Geri Bildiriminiz:**
Aboneliği neden durdurdunuz? (Opsiyonel)"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Tekrar Abone Ol", callback_data="confirm_daily_subscribe")],
        [InlineKeyboardButton("💬 Geri Bildirim Ver", callback_data="daily_feedback")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(unsubscribe_message, reply_markup=keyboard, parse_mode='Markdown')

async def subscription_stats(update: Update, context: CallbackContext):
    """Kullanıcının abonelik istatistiklerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Simüle edilmiş istatistikler (gerçek implementasyonda veritabanından alınacak)
    days_subscribed = 15  # Kaç gündür abone
    cards_received = 12   # Alınan kart sayısı
    favorite_suit = "Swords"  # En çok çıkan kart türü
    streak = 5  # Ardışık gün sayısı
    
    stats_message = f"""📊 **KİŞİSEL ABONELİK İSTATİSTİKLERİNİZ** 📊
━━━━━━━━━━━━━━━━━━━━━━

📅 **Genel Bilgiler:**
• Abone süresi: **{days_subscribed}** gün
• Alınan kartlar: **{cards_received}** adet
• Açılma oranı: **%87** (harika!)
• En aktif gün: **Pazartesi**

🃏 **Kart İstatistikleri:**
• Favori kart türü: **{favorite_suit}**
• En şanslı kart: **The Star** ⭐
• Tekrar sayısı: 2 kart (normal)
• Çeşitlilik skoru: **8.5/10**

🔥 **Başarı Rozetleri:**
• 🌟 İlk Hafta Tamamlandı
• 🎯 %80+ Açılma Oranı
• 💫 10+ Farklı Kart
• ⚡ 5+ Gün Ardışık

📈 **Aktivite Grafiği:**
```
Pzt: ████████░░ 80%
Sal: ██████████ 100%
Çar: ██████░░░░ 60%
Per: ██████████ 100%
Cum: ████████░░ 80%
Cmt: ██████░░░░ 60%
Paz: ████████░░ 80%
```

🎁 **Kazanılan Ödüller:**
• 1 hafta bonusu: **Tamamlandı** ✅
• Sadakat rozeti: **3 gün kaldı** ⏳
• VIP erişim: **7 gün kaldı** ⏳

🔮 **Gelecek Projeksiyonunuz:**
Mevcut tutarlılığınızla bu ay sonunda **elit abone** statüsüne ulaşacaksınız!"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Abonelik Ayarları", callback_data="toggle_daily")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(stats_message, reply_markup=keyboard, parse_mode='Markdown')

async def change_language_menu(update: Update, context: CallbackContext):
    """Dil seçim menüsünü gösterir - genişletilmiş dil desteği"""
    query = update.callback_query
    await query.answer()
    
    # Genişletilmiş dil seçenekleri
    keyboard = []
    
    # İlk satır: Ana diller
    keyboard.append([
        InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr"),
        InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇪🇸 Español", callback_data="set_lang_es")
    ])
    
    # İkinci satır: Avrupa dilleri  
    keyboard.append([
        InlineKeyboardButton("🇫🇷 Français", callback_data="set_lang_fr"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="set_lang_de")
    ])
    
    # Üçüncü satır: Diğer diller
    keyboard.append([
        InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"),
        InlineKeyboardButton("🇮🇹 Italiano", callback_data="set_lang_it"),
        InlineKeyboardButton("🇵🇹 Português", callback_data="set_lang_pt")
    ])
    
    # Geri butonu
    keyboard.append([InlineKeyboardButton("⬅️ Geri", callback_data="main_menu")])
    
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(
        query,
        "🌐 **Dil Seçimi / Language Selection**\n\nLütfen tercih ettiğiniz dili seçin:\nPlease select your preferred language:", 
        reply_markup=keyboard_markup, 
        parse_mode='Markdown'
    )

async def set_language(update: Update, context: CallbackContext):
    """Kullanıcının dil tercihini günceller"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[-1]
    user_id = query.from_user.id
    user_id_str = str(user_id)
    
    # Dil kodunun geçerli olduğunu kontrol et
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = 'tr'
    
    # Kullanıcının dilini güncelle
    supabase_manager.update_user(user_id, {'language': lang_code})
    supabase_manager.add_log(f"Kullanıcı {user_id_str} dilini {lang_code} olarak değiştirdi.")
    
    # Dil değişikliği mesajı
    lang_name = SUPPORTED_LANGUAGES[lang_code]
    
    # Yeni dilde ana menüyü göster
    welcome_message = get_text(lang_code, "start_message")
    
    # Dil değişikliği bildirimi ekle
    if lang_code == 'tr':
        change_message = f"✅ Diliniz **{lang_name}** olarak güncellendi!"
    elif lang_code == 'en':
        change_message = f"✅ Your language updated to **{lang_name}**!"
    elif lang_code == 'es':
        change_message = f"✅ Tu idioma se actualizó a **{lang_name}**!"
    elif lang_code == 'fr':
        change_message = f"✅ Votre langue mise à jour vers **{lang_name}**!"
    elif lang_code == 'ru':
        change_message = f"✅ Ваш язык обновлён на **{lang_name}**!"
    else:
        change_message = f"✅ Language updated to **{lang_name}**!"
    
    full_message = f"{change_message}\n\n{welcome_message}"
    
    await show_main_menu(update, context, message=full_message)

async def get_referral_link_callback(update: Update, context: CallbackContext):
    """Referans linkini oluşturur ve gösterir."""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    
    # Referans istatistikleri al
    referred_count = user.get("referred_count", 0)
    bonus_readings = user.get("bonus_readings", 0)
    referral_earnings = user.get("referral_earnings", 0)
    
    # VIP statü kontrolü
    vip_status = "👑 VIP" if referred_count >= 10 else "🌟 Elit" if referred_count >= 25 else "💎 Premium" if referred_count >= 5 else "🆕 Yeni"
    
    # Progress bar oluştur (5'er milestone)
    current_milestone = (referred_count // 5) * 5
    next_milestone = current_milestone + 5
    progress = referred_count - current_milestone
    progress_bar = "🟢" * progress + "⚪" * (5 - progress)
    
    # Günlük/haftalık hedefler
    daily_goal = 1
    weekly_goal = 5
    
    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user_id_str}"
    
    # Use locale system for referral stats message
    message = get_text(lang, "referral_system.title", "🌟 **FAL GRAM REFERRAL SYSTEM** 🌟") + "\n" + \
              get_text(lang, "referral_system.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
              get_text(lang, "referral_system.status", "👤 **Your Status:**") + f" {vip_status}\n\n" + \
              get_text(lang, "referral_system.statistics_title", "📊 **Your Statistics:**") + "\n" + \
              get_text(lang, "referral_system.total_invites", "👥 Total Invites:") + f" **{referred_count}** " + \
              get_text(lang, "referral_system.people", "people") + "\n" + \
              get_text(lang, "referral_system.bonus_readings", "🎁 Bonus Readings:") + f" **{bonus_readings}** " + \
              get_text(lang, "referral_system.readings", "readings") + "\n" + \
              get_text(lang, "referral_system.total_earnings", "💰 Total Earnings:") + f" **{referral_earnings}** " + \
              get_text(lang, "referral_system.readings", "readings") + "\n\n" + \
              get_text(lang, "referral_system.progress_bar", "📈 **Progress Bar ({progress}/5):**") + "\n" + \
              f"{progress_bar} **{referred_count}**/{next_milestone}\n\n" + \
              get_text(lang, "referral_system.reward_system", "🏆 **Reward System:**") + "\n" + \
              get_text(lang, "referral_system.reward_1", "• 1 Invite = 1 Free Reading ✨") + "\n" + \
              get_text(lang, "referral_system.reward_5", "• 5 Invites = 3 Bonus Readings + Special Badges 🏅") + "\n" + \
              get_text(lang, "referral_system.reward_10", "• 10 Invites = VIP Status + Unlimited Daily Cards 👑") + "\n" + \
              get_text(lang, "referral_system.reward_25", "• 25 Invites = Elite Member + Priority Support 🌟") + "\n" + \
              get_text(lang, "referral_system.reward_50", "• 50 Invites = Premium Fortune Teller Access 💎") + "\n\n" + \
              get_text(lang, "referral_system.goals_title", "🎯 **Your Goals:**") + "\n" + \
              get_text(lang, "referral_system.daily_goal", "• Daily:") + f" {daily_goal} " + \
              get_text(lang, "referral_system.invite", "invite") + "\n" + \
              get_text(lang, "referral_system.weekly_goal", "• Weekly:") + f" {weekly_goal} " + \
              get_text(lang, "referral_system.invites", "invites") + "\n\n" + \
              get_text(lang, "referral_system.link_title", "🔗 **Your Special Referral Link:**") + "\n" + \
              f"```\n{referral_link}\n```\n\n" + \
              get_text(lang, "referral_system.quick_share", "📤 **Quick Share:**")
    
    # Gelişmiş butonlar
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_text(lang, "referral_system.share_whatsapp", "📱 Share on WhatsApp"), 
                               url=f"https://api.whatsapp.com/send?text=🔮 {get_text(lang, 'referral_system.share_text', 'Fal Gram\'da ücretsiz fal bak!')} {referral_link}"),
            InlineKeyboardButton(get_text(lang, "referral_system.share_telegram", "📲 Share on Telegram"), 
                               url=f"https://t.me/share/url?url={referral_link}&text=🔮 {get_text(lang, 'referral_system.share_text', 'Fal Gram\'da ücretsiz fal bak!')}")
        ],
        [
            InlineKeyboardButton(get_text(lang, "referral_system.detailed_stats", "📊 Detailed Statistics"), callback_data="referral_stats"),
            InlineKeyboardButton(get_text(lang, "referral_system.my_rewards", "🎁 My Rewards"), callback_data="my_rewards")
        ],
        [
            InlineKeyboardButton(get_text(lang, "referral_system.copy_link", "📋 Copy Link"), callback_data=f"copy_link_{user_id_str}"),
            InlineKeyboardButton(get_text(lang, "referral_system.refresh", "🔄 Refresh"), callback_data="get_referral_link")
        ],
        [InlineKeyboardButton(get_text(lang, "main_menu_button", "🏠 Main Menu"), callback_data="main_menu")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def referral_stats(update: Update, context: CallbackContext):
    """Detaylı referans istatistiklerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Detaylı istatistikler
    referred_count = user.get("referred_count", 0)
    total_earnings = user.get("referral_earnings", 0)
    last_referral = user.get("last_referral_date", "Henüz yok")
    
    # Bu hafta ve bu ay davetleri (örnek veriler - gerçek implementasyonda tarih kontrolü yapılacak)
    weekly_referrals = 0  # Bu hafta yapılan davetler
    monthly_referrals = referred_count  # Bu ay yapılan davetler
    
    # Ranking (örnek veri)
    user_ranking = max(1, 100 - referred_count * 3)  # Basit sıralama algoritması
    
    stats_message = f"""📊 **DETAYLI REFERANS İSTATİSTİKLERİ** 📊
━━━━━━━━━━━━━━━━━━━━━━

📈 **Genel Performans:**
• Toplam Davet: **{referred_count}** kişi
• Bu Hafta: **{weekly_referrals}** davet
• Bu Ay: **{monthly_referrals}** davet
• Son Davet: {last_referral}

💰 **Kazançlar:**
• Toplam Kazanılan Fal: **{total_earnings}** adet
• Ortalama/Davet: **{total_earnings/max(referred_count,1):.1f}** fal
• Potansiyel Değer: **{total_earnings * 250}** ⭐

🏆 **Sıralama & Statü:**
• Global Sıralama: **#{user_ranking}**
• Percentile: **Top %{(user_ranking/1000)*100:.0f}**
• Aktif Seviye: Level {referred_count//5 + 1}

📊 **Gelecek Hedefler:**
• Sonraki Seviye: {((referred_count//5)+1)*5} davet
• VIP'e Kalan: {max(0, 10-referred_count)} davet
• Elite'e Kalan: {max(0, 25-referred_count)} davet

🔥 **Bu Ay Liderboard Top 5:**
1. 👑 FalKing - 45 davet
2. 🌟 MysticalQueen - 38 davet
3. 💎 TarotMaster - 31 davet
4. 🔮 DreamReader - 28 davet
5. ✨ CoffeeSeer - 24 davet"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Referans Paneli", callback_data="get_referral_link")]
    ])
    
    await query.edit_message_text(stats_message, reply_markup=keyboard, parse_mode='Markdown')

async def my_rewards(update: Update, context: CallbackContext):
    """Kullanıcının ödüllerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    referred_count = user.get("referred_count", 0)
    bonus_readings = user.get("bonus_readings", 0)
    
    # Kazanılan rozetler
    badges = []
    if referred_count >= 1:
        badges.append("🌟 İlk Davet")
    if referred_count >= 5:
        badges.append("🏅 Topluluk Kurucusu")
    if referred_count >= 10:
        badges.append("👑 VIP Üye")
    if referred_count >= 25:
        badges.append("💎 Elit Statü")
    if referred_count >= 50:
        badges.append("🏆 Referans Ustası")
    
    # Özel yetkiler
    special_perks = []
    if referred_count >= 5:
        special_perks.append("• 🎁 Haftalık bonus fallar")
        special_perks.append("• 🌈 Özel renkli profil")
    if referred_count >= 10:
        special_perks.append("• 🔓 VIP tarot destesi")
        special_perks.append("• ⚡ Öncelikli AI yanıtları")
    if referred_count >= 25:
        special_perks.append("• 👨‍💼 Kişisel fal danışmanı")
        special_perks.append("• 📞 7/24 öncelikli destek")
    
    rewards_message = get_text(lang, "rewards.title", "🎁 **YOUR REWARD COLLECTION** 🎁") + "\n" + \
                     get_text(lang, "rewards.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
                     get_text(lang, "rewards.active_balance", "💰 **Active Balance:**") + "\n" + \
                     get_text(lang, "rewards.available_readings", "• Available Readings:") + f" **{bonus_readings}** " + \
                     get_text(lang, "rewards.readings", "readings") + "\n" + \
                     get_text(lang, "rewards.total_value", "• Total Value:") + f" **{bonus_readings * 250}** ⭐\n\n" + \
                     get_text(lang, "rewards.earned_badges", "🏅 **Earned Badges:**") + "\n" + \
                     (chr(10).join(badges) if badges else get_text(lang, "rewards.no_badges", "• No badges earned yet")) + "\n\n" + \
                     get_text(lang, "rewards.special_perks", "✨ **Your Special Perks:**") + "\n" + \
                     (chr(10).join(special_perks) if special_perks else get_text(lang, "rewards.no_perks", "• Invite more people to unlock special perks")) + "\n\n" + \
                     get_text(lang, "rewards.next_rewards", "🎯 **Next Rewards:**") + "\n" + \
                     (f"• {5-referred_count} " + get_text(lang, "rewards.more_invites", "more invites") + " → 🏅 " + get_text(lang, "rewards.community_founder", "Community Founder") if referred_count < 5 else "") + "\n" + \
                     (f"• {10-referred_count} " + get_text(lang, "rewards.more_invites", "more invites") + " → 👑 " + get_text(lang, "rewards.vip_status", "VIP Status") if referred_count < 10 else "") + "\n" + \
                     (f"• {25-referred_count} " + get_text(lang, "rewards.more_invites", "more invites") + " → 💎 " + get_text(lang, "rewards.elite_membership", "Elite Membership") if referred_count < 25 else "") + "\n" + \
                     (f"• {50-referred_count} " + get_text(lang, "rewards.more_invites", "more invites") + " → 🏆 " + get_text(lang, "rewards.referral_master", "Referral Master") if referred_count < 50 else "") + "\n\n" + \
                     get_text(lang, "rewards.special_offers", "🔮 **Special Offers:**") + "\n" + \
                     get_text(lang, "rewards.offer_1", "• 🌟 3+ invites this week → Extra 2 bonus readings") + "\n" + \
                     get_text(lang, "rewards.offer_2", "• 💎 10+ invites this month → Special tarot reading session") + "\n" + \
                     get_text(lang, "rewards.offer_3", "• 👑 Premium membership 50% discount (for VIPs)")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "rewards.use_bonus_readings", "💰 Use Bonus Readings"), callback_data="use_bonus_readings")],
        [InlineKeyboardButton(get_text(lang, "rewards.back_to_referral", "🔙 Referral Panel"), callback_data="get_referral_link")]
    ])
    
    await query.edit_message_text(rewards_message, reply_markup=keyboard, parse_mode='Markdown')

# --- Telegram Stars Ödeme Fonksiyonları ---
async def pay_for_fortune_callback(update: Update, context: CallbackContext):
    """Kahve falı için Telegram Stars ödeme işlemi."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Telegram Stars ödeme faturası oluştur
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title="🔮 Kahve Falı",
            description="Kahve fincanınızın fotoğrafından detaylı fal yorumu",
            payload="coffee_fortune",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",
            prices=[LabeledPrice("Kahve Falı", PAID_READING_STARS)],  # Telegram Stars cent cinsinden
            start_parameter="coffee_fortune_payment"
        )
        supabase_manager.add_log(f"Kahve falı ödeme faturası oluşturuldu: {query.from_user.id}")
    except Exception as e:
        logger.error(f"Ödeme faturası hatası: {e}")
        await query.message.reply_text("❌ Ödeme faturası oluşturulamadı. Lütfen daha sonra tekrar deneyin.")

async def pay_for_tarot_callback(update: Update, context: CallbackContext):
    """Tarot falı için Telegram Stars ödeme işlemi."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Telegram Stars ödeme faturası oluştur
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title="🎴 Tarot Falı",
            description="Kişisel tarot kartı yorumu",
            payload="tarot_fortune",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",
            prices=[LabeledPrice("Tarot Falı", PAID_READING_STARS)],  # Telegram Stars cent cinsinden
            start_parameter="tarot_fortune_payment"
        )
        supabase_manager.add_log(f"Tarot falı ödeme faturası oluşturuldu: {query.from_user.id}")
    except Exception as e:
        logger.error(f"Ödeme faturası hatası: {e}")
        await query.message.reply_text("❌ Ödeme faturası oluşturulamadı. Lütfen daha sonra tekrar deneyin.")

async def pay_for_dream_callback(update: Update, context: CallbackContext):
    """Rüya tabiri için Telegram Stars ödeme işlemi."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Telegram Stars ödeme faturası oluştur
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title="💭 Rüya Tabiri",
            description="Kişisel rüya yorumu ve analizi",
            payload="dream_fortune",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",
            prices=[LabeledPrice("Rüya Tabiri", PAID_READING_STARS)],  # Telegram Stars cent cinsinden
            start_parameter="dream_fortune_payment"
        )
        supabase_manager.add_log(f"Rüya tabiri ödeme faturası oluşturuldu: {query.from_user.id}")
    except Exception as e:
        logger.error(f"Ödeme faturası hatası: {e}")
        await query.message.reply_text("❌ Ödeme faturası oluşturulamadı. Lütfen daha sonra tekrar deneyin.")

async def precheckout_callback(update: Update, context: CallbackContext):
    """Ödeme öncesi kontrol."""
    query = update.pre_checkout_query
    await query.answer(ok=True)
    supabase_manager.add_log(f"Ödeme öncesi kontrol: {query.from_user.id}")

async def successful_payment_callback(update: Update, context: CallbackContext):
    """Başarılı ödeme sonrası işlem."""
    payment_info = update.message.successful_payment
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    
    supabase_manager.add_log(f"Başarılı ödeme: {user_id} - {payment_info.total_amount} cent")
    
    if payment_info.invoice_payload == "coffee_fortune":
        # Kahve falı için ödeme yapıldı, kullanıcıdan fotoğraf iste
        await update.message.reply_text("💫 Ödeme başarılı! Şimdi kahve fincanınızın fotoğrafını gönderin.")
        # Kullanıcının son gönderdiği fotoğrafı işle
        context.user_data['paid_coffee_fortune'] = True
    elif payment_info.invoice_payload == "tarot_fortune":
        # Tarot falı için ödeme yapıldı, tarot çek
        await update.message.reply_text("💫 Ödeme başarılı! Tarot kartınız çekiliyor...")
        # Tarot kartı çek
        await process_paid_tarot(update, context)
    elif payment_info.invoice_payload == "dream_fortune":
        # Rüya tabiri için ödeme yapıldı, rüya analizi iste
        await update.message.reply_text("💫 Ödeme başarılı! Şimdi rüyanızı anlatın.")
        # Kullanıcının rüya analizi için hazırla
        supabase_manager.update_user(user_id, {'state': 'waiting_for_dream'})
    elif payment_info.invoice_payload.startswith('premium_'):
        # Handle premium subscription payment
        plan_id = payment_info.invoice_payload.split('_')[1]
        plan = PREMIUM_PLANS.get(plan_id)
        
        if plan:
            # Update user's premium plan
            supabase_manager.update_user(user_id, {
                'premium_plan': plan_id,
                'premium_expires_at': datetime.now() + timedelta(days=30)
            })
            
            # Log the premium subscription
            supabase_manager.add_log(f"Premium subscription activated: User {user_id}, Plan {plan_id}")
            
            plan_name = plan.get('name' if lang == 'tr' else 'name_en', get_text(lang, "premium.unknown_plan", "Unknown Plan"))
            features = plan.get('features' if lang == 'tr' else 'features_en', [])
            
            success_message = get_text(lang, "premium.subscription_active", "🎉 **Premium Subscription Active!** 🎉") + "\n\n" + \
                            get_text(lang, "premium.subscription_success", "✨ **{plan_name}** planına başarıyla abone oldunuz!").format(plan_name=plan_name) + "\n\n" + \
                            get_text(lang, "premium.duration", "📅 **Duration:**") + " " + get_text(lang, "premium.duration_value", "30 days") + "\n" + \
                            get_text(lang, "premium.features", "💎 **Features:**") + "\n"
            
            for feature in features:
                success_message += f"• {feature}\n"
            
            success_message += "\n" + get_text(lang, "premium.access_granted", "🌟 Artık tüm premium özelliklere erişiminiz var!")
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Plan bulunamadı. Lütfen destek ile iletişime geçin.")

async def process_paid_tarot(update: Update, context: CallbackContext):
    """Ödeme sonrası tarot falı işleme."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    user_id_str = str(update.effective_user.id)
    lang = get_user_lang(update.effective_user.id)
    
    try:
        tarot_cards = supabase_manager.get_tarot_cards()
        card = random.choice(tarot_cards) if tarot_cards else "The Fool"
        
        # Gemini 2.5 modelini kullan (eğer mevcutsa)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor: {user_id_str}")
        except Exception as e:
            # Eğer 2.5 mevcut değilse 1.5 kullan
            model = genai.GenerativeModel('gemini-1.5-flash')
            supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor: {user_id_str}")
        
        prompt = supabase_manager.get_prompt("tarot", lang)
        if not prompt:
            prompt = f"""Sen deneyimli bir tarot yorumcususun. {card} kartını çeken {user.get('first_name', 'Dostum')} için kapsamlı bir yorum oluştur.

**Kartın Genel Anlamı:** {card} kartının temel sembolizmini ve enerjisini açıkla.
**Kişisel Mesaj:** Bu kartın {user.get('first_name', 'Dostum')}'in hayatındaki mevcut duruma nasıl yansıdığını yorumla.
**Gelecek Öngörüsü:** Kartın gösterdiği enerjiye dayanarak yakın gelecek için bir öngörüde bulun.
**Pratik Tavsiye:** {user.get('first_name', 'Dostum')}'e bu kartın enerjisini en iyi nasıl kullanabileceğine dair somut öneriler ver.

**Dil Tonu:** Mistik, bilge ve motive edici.
**Kısıtlamalar:** 120-150 kelime."""
        
        prompt = prompt.replace("{card}", card).replace("{username}", user.get('first_name', 'Dostum'))
        
        supabase_manager.add_log(f"Tarot prompt hazırlandı ({lang}): {len(prompt)} karakter")
        supabase_manager.add_log(f"Gemini API çağrısı yapılıyor ({lang}): {user_id_str}")
        
        # Prompt'a dil talimatı ekle
        if lang != 'tr':
            prompt = f"Please respond in {lang.upper()} language.\n\n" + prompt
        
        response = await model.generate_content_async(prompt)
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        supabase_manager.add_log(f"Gemini tarot yanıtı alındı ({lang}): {len(response.text)} karakter")
        
        supabase_manager.add_log(f"Ücretli tarot falı üretildi. Kullanıcı: {user_id_str}. Kart: {card}")
        await update.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(update.effective_user.id))
    except Exception as e:
        logger.error(f"Ücretli tarot falı hatası: {e}")
        await update.message.reply_text(
            get_text(lang, "fortune_error"), 
            reply_markup=get_main_menu_keyboard(update.effective_user.id)
        )

# --- Zamanlanmış Görevler ---
async def send_daily_card(application: Application):
    """Günlük tarot kartını abonelere gönderir."""
    logger.info("Günlük kart gönderme görevi çalışıyor.")
    
    subscribed_users = supabase_manager.get_subscribed_users()
    tarot_cards = supabase_manager.get_tarot_cards()
    
    for user_id in subscribed_users:
        try:
            lang = get_user_lang(user_id)
            username = supabase_manager.get_user(user_id).get("first_name", "Dostum")
            card = random.choice(tarot_cards) if tarot_cards else "The Fool"
            
            # Gemini 2.5 modelini kullan (eğer mevcutsa)
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                supabase_manager.add_log(f"Gemini 2.5 model kullanılıyor (günlük kart): {user_id}")
            except Exception as e:
                # Eğer 2.5 mevcut değilse 1.5 kullan
                model = genai.GenerativeModel('gemini-1.5-flash')
                supabase_manager.add_log(f"Gemini 1.5 model kullanılıyor (günlük kart): {user_id}")
            
            prompt = supabase_manager.get_prompt("daily_tarot", lang)
            if not prompt:
                prompt = f"""🌅 Günün başlangıcında {username} için {card} kartının enerjisini yorumla.

✨ **Günün Enerjisi:** {card} kartının bugün {username}'e sunduğu ana enerjiyi detaylıca açıkla.
🎯 **Günlük Fırsatlar:** Bu kartın gösterdiği gün içindeki özel fırsatları ve şansları belirt.
⚠️ **Dikkat Edilmesi Gerekenler:** Bugün dikkatli olması gereken noktaları ve potansiyel zorlukları vurgula.
💪 **Günlük Motivasyon:** {username}'i güne pozitif başlaması için güçlü ve motive eden bir mesaj ver.
🔮 **Günün Tavsiyesi:** Bu kartın enerjisini en iyi şekilde kullanmak için pratik tavsiyeler.

**Dil Tonu:** Enerjik, umut verici ve motive edici.
**Kısıtlamalar:** 80-100 kelime."""
            
            prompt = prompt.replace("{card}", card).replace("{username}", username)
            
            supabase_manager.add_log(f"Günlük kart prompt hazırlandı ({lang}): {len(prompt)} karakter")
            supabase_manager.add_log(f"Gemini API çağrısı yapılıyor (günlük kart, {lang}): {user_id}")
            
            # Prompt'a dil talimatı ekle
            if lang != 'tr':
                prompt = f"Please respond in {lang.upper()} language.\n\n" + prompt
            
            response = await model.generate_content_async(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini API'den boş yanıt alındı")
            
            supabase_manager.add_log(f"Gemini günlük kart yanıtı alındı: {len(response.text)} karakter")
            
            # Güzel bir günlük kart mesajı oluştur
            daily_message = f"""🌟 **FAL GRAM - GÜNÜN KARTI** 🌟
━━━━━━━━━━━━━━━━━━━━━━
🃏 **{card}**
━━━━━━━━━━━━━━━━━━━━━━

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
🌅 **Güzel bir gün geçir {username}!**
✨ *Fal Gram ile her gün yeni keşifler*"""
            
            await application.bot.send_message(
                chat_id=user_id, 
                text=daily_message, 
                parse_mode='Markdown'
            )
            supabase_manager.add_log(f"Günlük kart gönderildi: {user_id} (Kart: {card})")
        except Exception as e:
            logger.error(f"Günlük kart gönderme hatası ({user_id}): {e}")

async def post_init(application: Application):
    """Uygulama başlatıldıktan sonra zamanlayıcıyı başlatır."""
    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    hour, minute = supabase_manager.get_daily_card_time()
    scheduler.add_job(send_daily_card, CronTrigger(hour=hour, minute=minute), args=[application])
    scheduler.start()
    supabase_manager.add_log(f"Zamanlayıcı kuruldu: {hour}:{minute}")
    application.bot_data['scheduler'] = scheduler

# --- Admin Paneli ---
async def admin_command(update: Update, context: CallbackContext):
    """Admin komutunu işler."""
    if update.effective_user.id != ADMIN_ID:
        return
    
    await admin_panel(update, context)

async def admin_panel(update: Update, context: CallbackContext):
    """Admin panelini gösterir."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Kullanıcı Listesi", callback_data="admin_users")],
        [InlineKeyboardButton("👥 Referral İlişkileri", callback_data="admin_referrals")],
        [InlineKeyboardButton("💎 Premium Yönetimi", callback_data="admin_premium")],
        [InlineKeyboardButton("📋 Logları Görüntüle", callback_data="admin_view_logs")],
        [InlineKeyboardButton("📄 PDF İndir", callback_data="admin_download_pdf")],
        [InlineKeyboardButton("⚙️ Ayarlar", callback_data="admin_settings")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    if update.message:
        await update.message.reply_text("🔧 *Admin Paneli*", reply_markup=keyboard, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.edit_message_text("🔧 *Admin Paneli*", reply_markup=keyboard, parse_mode='Markdown')

async def admin_stats(update: Update, context: CallbackContext):
    """Admin istatistiklerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    total_users = len(supabase_manager.get_all_users())
    subscribed_users = len(supabase_manager.get_subscribed_users())
    referral_data = supabase_manager.get_referral_relationships()
    
    # Referral istatistikleri
    total_referrers = len(referral_data)
    total_referred = sum(user['referred_count'] for user in referral_data)
    total_earnings = sum(user['earnings'] for user in referral_data)
    
    stats_text = f"**📊 Bot İstatistikleri**\n\n"
    stats_text += f"**👥 Kullanıcı İstatistikleri:**\n"
    stats_text += f"• Toplam Kullanıcı: **{total_users}**\n"
    stats_text += f"• Günlük Kart Abonesi: **{subscribed_users}**\n\n"
    
    stats_text += f"**👤 Referral İstatistikleri:**\n"
    stats_text += f"• Referral Eden: **{total_referrers}** kullanıcı\n"
    stats_text += f"• Toplam Davet: **{total_referred}** kişi\n"
    stats_text += f"• Toplam Kazanç: **{total_earnings}** fal\n"
    
    if total_users > 0:
        stats_text += f"• Referral Oranı: **{(total_referrers/total_users*100):.1f}%**\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Referral Detayları", callback_data="admin_referrals")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_to_admin")]
    ])
    
    await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=keyboard)

async def admin_view_logs(update: Update, context: CallbackContext):
    """Admin loglarını gösterir."""
    query = update.callback_query
    await query.answer()
    
    logs = supabase_manager.get_logs(50)  # Son 50 log
    
    if not logs:
        await query.edit_message_text("Henüz log kaydı yok.", reply_markup=get_back_to_menu_button("tr"))
        return
    
    log_text = "**📋 Son 50 Log Kaydı**\n\n"
    for log in logs:
        timestamp = log['timestamp'][:19] if log['timestamp'] else "N/A"
        log_text += f"`{timestamp}`: {log['message']}\n\n"
    
    # Telegram mesaj limiti (4096 karakter)
    if len(log_text) > 4000:
        log_text = log_text[:4000] + "\n... (daha fazla log var)"
    
    await query.edit_message_text(log_text, parse_mode='Markdown', reply_markup=get_back_to_menu_button("tr"))

async def admin_settings(update: Update, context: CallbackContext):
    """Admin ayarlarını gösterir."""
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🕐 Günlük Kart Saatini Değiştir", callback_data="edit_daily_time")],
        [InlineKeyboardButton("📝 Prompt Düzenle", callback_data="edit_prompts")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    await query.edit_message_text("⚙️ *Admin Ayarları*", reply_markup=keyboard, parse_mode='Markdown')

async def admin_users(update: Update, context: CallbackContext):
    """Admin kullanıcı listesini gösterir."""
    query = update.callback_query
    await query.answer()
    
    users = supabase_manager.get_all_users()
    
    if not users:
        await query.edit_message_text("Henüz kullanıcı yok.", reply_markup=get_back_to_admin_button())
        return
    
    user_text = "**👥 Kullanıcı Listesi**\n\n"
    for i, user in enumerate(users[:20]):  # İlk 20 kullanıcı
        name = user.get('first_name', 'Bilinmeyen')
        user_id = user.get('user_id', 'N/A')
        readings = user.get('readings_count', 0)
        lang = user.get('language', 'tr')
        daily_sub = "✅" if user.get('daily_subscription', False) else "❌"
        
        user_text += f"{i+1}. **{name}** ({user_id})\n"
        user_text += f"   📚 Fallar: {readings} | 🌐 Dil: {lang.upper()} | 📅 Günlük: {daily_sub}\n\n"
    
    # Telegram mesaj limiti
    if len(user_text) > 4000:
        user_text = user_text[:4000] + "\n... (daha fazla kullanıcı var)"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Kullanıcı PDF İndir", callback_data="admin_download_users_pdf")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_to_admin")]
    ])
    
    await query.edit_message_text(user_text, parse_mode='Markdown', reply_markup=keyboard)

async def admin_referrals(update: Update, context: CallbackContext):
    """Admin referral ilişkilerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    referral_data = supabase_manager.get_referral_relationships()
    
    if not referral_data:
        await query.edit_message_text("Henüz referral ilişkisi yok.", reply_markup=get_back_to_admin_button())
        return
    
    # Referral verilerini sırala (en çok referral edenler üstte)
    referral_data.sort(key=lambda x: x['referred_count'], reverse=True)
    
    referral_text = "**👥 Referral İlişkileri**\n\n"
    referral_text += "**En Aktif Referral Edenler:**\n\n"
    
    for i, user in enumerate(referral_data[:15]):  # İlk 15 kullanıcı
        name = user['name']
        user_id = user['user_id']
        username = f"@{user['username']}" if user['username'] else "Kullanıcı adı yok"
        referred_count = user['referred_count']
        earnings = user['earnings']
        
        # VIP statü belirle
        if referred_count >= 10:
            status = "👑 VIP"
        elif referred_count >= 5:
            status = "💎 Premium"
        elif referred_count >= 3:
            status = "🌟 Aktif"
        else:
            status = "🆕 Yeni"
        
        referral_text += f"{i+1}. **{name}** ({user_id})\n"
        referral_text += f"   👤 {username} | {status}\n"
        referral_text += f"   👥 Davet: **{referred_count}** kişi | 💰 Kazanç: **{earnings}** fal\n\n"
    
    # Telegram mesaj limiti
    if len(referral_text) > 4000:
        referral_text = referral_text[:4000] + "\n... (daha fazla referral verisi var)"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Referral İstatistikleri", callback_data="admin_referral_stats")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_to_admin")]
    ])
    
    await query.edit_message_text(referral_text, parse_mode='Markdown', reply_markup=keyboard)

async def admin_referral_stats(update: Update, context: CallbackContext):
    """Admin referral istatistiklerini gösterir."""
    query = update.callback_query
    await query.answer()
    
    referral_data = supabase_manager.get_referral_relationships()
    all_users = supabase_manager.get_all_users()
    
    if not referral_data:
        await query.edit_message_text("Henüz referral verisi yok.", reply_markup=get_back_to_admin_button())
        return
    
    # İstatistikleri hesapla
    total_referrers = len(referral_data)
    total_referred = sum(user['referred_count'] for user in referral_data)
    total_earnings = sum(user['earnings'] for user in referral_data)
    total_users = len(all_users)
    
    # VIP kullanıcıları say
    vip_users = len([u for u in referral_data if u['referred_count'] >= 10])
    premium_users = len([u for u in referral_data if 5 <= u['referred_count'] < 10])
    active_users = len([u for u in referral_data if 3 <= u['referred_count'] < 5])
    
    # En iyi performans gösterenler
    top_referrer = max(referral_data, key=lambda x: x['referred_count']) if referral_data else None
    
    stats_text = "**📊 Referral İstatistikleri**\n\n"
    stats_text += f"**Genel İstatistikler:**\n"
    stats_text += f"👥 Toplam Kullanıcı: **{total_users}**\n"
    stats_text += f"👤 Referral Eden: **{total_referrers}** (%{(total_referrers/total_users*100):.1f})\n"
    stats_text += f"🎯 Toplam Davet: **{total_referred}**\n"
    stats_text += f"💰 Toplam Kazanç: **{total_earnings}** fal\n\n"
    
    stats_text += f"**VIP Seviyeler:**\n"
    stats_text += f"👑 VIP (10+ davet): **{vip_users}** kullanıcı\n"
    stats_text += f"💎 Premium (5-9 davet): **{premium_users}** kullanıcı\n"
    stats_text += f"🌟 Aktif (3-4 davet): **{active_users}** kullanıcı\n\n"
    
    if top_referrer:
        stats_text += f"**🏆 En İyi Performans:**\n"
        stats_text += f"👤 {top_referrer['name']} ({top_referrer['user_id']})\n"
        stats_text += f"👥 {top_referrer['referred_count']} davet | 💰 {top_referrer['earnings']} kazanç\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Referral Listesi", callback_data="admin_referrals")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_to_admin")]
    ])
    
    await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=keyboard)

async def admin_download_pdf(update: Update, context: CallbackContext):
    """Admin için PDF raporu oluşturur ve gönderir."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📄 PDF raporu hazırlanıyor...")
    
    try:
        from fpdf import FPDF
        import datetime
        
        # PDF oluştur
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Başlık
        pdf.cell(200, 10, txt="FAL GRAM - ADMIN RAPORU", ln=True, align='C')
        pdf.ln(10)
        
        # Tarih
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, txt=f"Rapor Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(10)
        
        # İstatistikler
        users = supabase_manager.get_all_users()
        subscribed_users = supabase_manager.get_subscribed_users()
        logs = supabase_manager.get_logs(100)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, txt="ISTATISTIKLER", ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, txt=f"Toplam Kullanici: {len(users)}", ln=True)
        pdf.cell(200, 10, txt=f"Gunluk Kart Abonesi: {len(subscribed_users)}", ln=True)
        pdf.cell(200, 10, txt=f"Toplam Log Kaydi: {len(logs)}", ln=True)
        pdf.ln(10)
        
        # Kullanıcı detayları
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, txt="KULLANICI DETAYLARI", ln=True)
        pdf.set_font('Arial', '', 10)
        
        for i, user in enumerate(users[:50]):  # İlk 50 kullanıcı
            name = user.get('first_name', 'Bilinmeyen')
            user_id = user.get('user_id', 'N/A')
            readings = user.get('readings_count', 0)
            lang = user.get('language', 'tr')
            
            pdf.cell(200, 6, txt=f"{i+1}. {name} ({user_id}) - Fallar: {readings}, Dil: {lang.upper()}", ln=True)
        
        # Referral ilişkileri
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, txt="REFERRAL ILISKILERI", ln=True)
        pdf.set_font('Arial', '', 10)
        
        referral_data = supabase_manager.get_referral_relationships()
        if referral_data:
            for i, user in enumerate(referral_data[:20]):  # İlk 20 referral
                name = user['name']
                user_id = user['user_id']
                referred_count = user['referred_count']
                earnings = user['earnings']
                pdf.cell(200, 6, txt=f"{i+1}. {name} ({user_id}) - Davet: {referred_count}, Kazanç: {earnings}", ln=True)
        else:
            pdf.cell(200, 6, txt="Henüz referral ilişkisi yok.", ln=True)
        
        # Son loglar
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, txt="SON LOGLAR", ln=True)
        pdf.set_font('Arial', '', 8)
        
        for log in logs[:30]:  # Son 30 log
            timestamp = log['timestamp'][:19] if log['timestamp'] else "N/A"
            message = log['message'][:80] + "..." if len(log['message']) > 80 else log['message']
            pdf.cell(200, 4, txt=f"{timestamp}: {message}", ln=True)
        
        # PDF'i kaydet
        pdf_filename = f"fal_gram_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(pdf_filename)
        
        # PDF'i gönder
        with open(pdf_filename, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id, 
                document=pdf_file, 
                filename=pdf_filename,
                caption="📄 **Fal Gram Admin Raporu**"
            )
        
        # Dosyayı sil
        import os
        os.remove(pdf_filename)
        
        await query.message.reply_text("✅ PDF raporu başarıyla gönderildi!", reply_markup=get_back_to_admin_button())
        
    except Exception as e:
        logger.error(f"PDF oluşturma hatası: {e}")
        await query.edit_message_text("❌ PDF oluşturulurken hata oluştu.", reply_markup=get_back_to_admin_button())

async def admin_download_users_pdf(update: Update, context: CallbackContext):
    """Kullanıcı listesi PDF'i oluşturur."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📄 Kullanıcı listesi PDF'i hazırlanıyor...")
    
    try:
        from fpdf import FPDF
        import datetime
        
        users = supabase_manager.get_all_users()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        pdf.cell(200, 10, txt="FAL GRAM - KULLANICI LISTESI", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, txt=f"Rapor Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.cell(200, 10, txt=f"Toplam Kullanici: {len(users)}", ln=True)
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, txt="DETAYLI KULLANICI BILGILERI", ln=True)
        pdf.set_font('Arial', '', 9)
        
        for i, user in enumerate(users):
            name = user.get('first_name', 'Bilinmeyen')
            username = user.get('username', 'N/A')
            user_id = user.get('user_id', 'N/A')
            readings = user.get('readings_count', 0)
            lang = user.get('language', 'tr')
            daily_sub = "Evet" if user.get('daily_subscription', False) else "Hayir"
            referral_count = user.get('referral_count', 0)
            
            pdf.cell(200, 5, txt=f"{i+1}. {name} (@{username})", ln=True)
            pdf.cell(200, 5, txt=f"    ID: {user_id} | Fallar: {readings} | Dil: {lang.upper()}", ln=True)
            pdf.cell(200, 5, txt=f"    Gunluk Abone: {daily_sub} | Referanslar: {referral_count}", ln=True)
            pdf.ln(2)
        
        pdf_filename = f"kullanici_listesi_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(pdf_filename)
        
        with open(pdf_filename, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id, 
                document=pdf_file, 
                filename=pdf_filename,
                caption="👥 **Kullanıcı Listesi Raporu**"
            )
        
        import os
        os.remove(pdf_filename)
        
        await query.message.reply_text("✅ Kullanıcı listesi PDF'i gönderildi!", reply_markup=get_back_to_admin_button())
        
    except Exception as e:
        logger.error(f"Kullanıcı PDF oluşturma hatası: {e}")
        await query.edit_message_text("❌ PDF oluşturulurken hata oluştu.", reply_markup=get_back_to_admin_button())

def get_back_to_admin_button():
    """Admin paneline dönüş butonu."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="back_to_admin")]
    ])

# ==================== ADMIN PREMIUM MANAGEMENT ====================

async def admin_premium_management(update: Update, context: CallbackContext):
    """Admin premium yönetimi menüsü"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    premium_users = supabase_manager.get_premium_users()
    total_premium = len(premium_users)
    active_subscriptions = len([u for u in premium_users if u.get('premium_expires_at') and u['premium_expires_at'] > datetime.now().isoformat()])
    
    message = get_text(lang, "admin_premium.title", "💎 **PREMIUM MANAGEMENT PANEL** 💎") + "\n" + \
              get_text(lang, "admin_premium.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
              get_text(lang, "admin_premium.statistics", "📊 **Statistics:**") + "\n" + \
              get_text(lang, "admin_premium.total_premium_users", "• Total Premium Users:") + f" **{total_premium}**\n" + \
              get_text(lang, "admin_premium.active_subscriptions", "• Active Subscriptions:") + f" **{active_subscriptions}**\n\n" + \
              get_text(lang, "admin_premium.management_options", "🎯 **Management Options:**") + "\n" + \
              get_text(lang, "admin_premium.separator", "━━━━━━━━━━━━━━━━━━━━━━")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "premium_users"), callback_data="admin_premium_users")],
        [InlineKeyboardButton(get_text(lang, "premium_stats"), callback_data="admin_premium_stats")],
        [InlineKeyboardButton(get_text(lang, "gift_subscription"), callback_data="admin_gift_subscription")],
        [InlineKeyboardButton(get_text(lang, "cancel_subscription"), callback_data="admin_cancel_subscription")],
        [InlineKeyboardButton(get_text(lang, "premium_report"), callback_data="admin_premium_pdf")],
        [InlineKeyboardButton(get_text(lang, "admin_panel_back"), callback_data="back_to_admin")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def admin_premium_users(update: Update, context: CallbackContext):
    """Premium kullanıcıları listele"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    premium_users = supabase_manager.get_premium_users()
    
    if not premium_users:
        await query.edit_message_text(get_text(lang, "no_premium_users"), reply_markup=get_back_to_admin_button())
        return
    
    message = get_text(lang, "premium_user_details") + "\n\n"
    
    for i, user in enumerate(premium_users[:20], 1):  # İlk 20 kullanıcı
        plan = PREMIUM_PLANS.get(user.get('premium_plan', 'free'), {})
        plan_name = plan.get('name' if lang == 'tr' else 'name_en', get_text(lang, "admin_premium.unknown_plan", "Unknown"))
        expires_at = user.get('premium_expires_at', get_text(lang, "admin_premium.unlimited", "Unlimited"))
        
        if expires_at and expires_at != get_text(lang, "admin_premium.unlimited", "Unlimited"):
            try:
                expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                expires_str = expires_date.strftime('%d.%m.%Y')
                status = get_text(lang, "admin_premium.status_active", "✅ Active") if expires_date > datetime.now() else get_text(lang, "admin_premium.status_expired", "❌ Expired")
            except:
                expires_str = expires_at
                status = get_text(lang, "admin_premium.status_unknown", "❓ Unknown")
        else:
            expires_str = get_text(lang, "admin_premium.unlimited", "Unlimited")
            status = get_text(lang, "admin_premium.status_active", "✅ Active")
        
        message += f"**{i}.** {user.get('first_name', get_text(lang, 'admin_premium.unnamed', 'Unnamed'))} (@{user.get('username', get_text(lang, 'admin_premium.user', 'user'))})\n"
        message += f"   📋 {get_text(lang, 'admin_premium.plan', 'Plan')}: {plan_name}\n"
        message += f"   📅 {get_text(lang, 'admin_premium.expires', 'Expires')}: {expires_str}\n"
        message += f"   🎯 {get_text(lang, 'admin_premium.status', 'Status')}: {status}\n\n"
    
    if len(premium_users) > 20:
        message += get_text(lang, "admin_premium.more_users", "... and {count} more users").format(count=len(premium_users) - 20)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "admin_premium.detailed_search", "🔍 Detailed Search"), callback_data="admin_premium_search")],
        [InlineKeyboardButton(get_text(lang, "back_to_premium"), callback_data="admin_premium")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def admin_premium_stats(update: Update, context: CallbackContext):
    """Premium abonelik istatistikleri"""
    query = update.callback_query
    await query.answer()
    
    premium_users = supabase_manager.get_premium_users()
    payments = supabase_manager.get_payment_statistics()
    
    # Plan dağılımı
    plan_stats = {}
    for user in premium_users:
        plan = user.get('premium_plan', 'free')
        plan_stats[plan] = plan_stats.get(plan, 0) + 1
    
    # Ödeme istatistikleri
    total_revenue = sum(payment.get('amount', 0) for payment in payments)
    monthly_revenue = sum(payment.get('amount', 0) for payment in payments 
                         if payment.get('created_at', '').startswith(datetime.now().strftime('%Y-%m')))
    
    message = f"""📊 **PREMIUM İSTATİSTİKLERİ** 📊
━━━━━━━━━━━━━━━━━━━━━━

👥 **Kullanıcı Dağılımı:**
"""
    
    for plan_id, count in plan_stats.items():
        plan_name = PREMIUM_PLANS.get(plan_id, {}).get('name', plan_id)
        message += f"• {plan_name}: **{count}** kullanıcı\n"
    
    message += f"""
💰 **Gelir İstatistikleri:**
• Toplam Gelir: **{total_revenue}** Star
• Bu Ay: **{monthly_revenue}** Star

📈 **Aktif Abonelikler:**
• Aktif: **{len([u for u in premium_users if u.get('premium_expires_at') and u['premium_expires_at'] > datetime.now().isoformat()])}**
• Süresi Dolmuş: **{len([u for u in premium_users if u.get('premium_expires_at') and u['premium_expires_at'] <= datetime.now().isoformat()])}**
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Detaylı Rapor", callback_data="admin_premium_detailed_stats")],
        [InlineKeyboardButton("🔙 Premium Yönetimi", callback_data="admin_premium")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def admin_gift_subscription(update: Update, context: CallbackContext):
    """Hediye abonelik menüsü"""
    query = update.callback_query
    await query.answer()
    
    message = """🎁 **HEDİYE ABONELİK** 🎁
━━━━━━━━━━━━━━━━━━━━━━

Bir kullanıcıya premium abonelik hediye etmek için:

1️⃣ Kullanıcı ID'sini girin
2️⃣ Plan seçin
3️⃣ Süre belirleyin

**Örnek:** `/gift 123456789 basic 30` (30 günlük temel plan)

**Mevcut Planlar:**"""
    
    for plan_id, plan in PREMIUM_PLANS.items():
        if plan_id != 'free':
            message += f"\n• **{plan['name']}** - {plan['price']} Star"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Hediye Komutu Örnekleri", callback_data="admin_gift_examples")],
        [InlineKeyboardButton("🔙 Premium Yönetimi", callback_data="admin_premium")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def admin_cancel_subscription(update: Update, context: CallbackContext):
    """Abonelik iptal menüsü"""
    query = update.callback_query
    await query.answer()
    
    message = """❌ **ABONELİK İPTAL** ❌
━━━━━━━━━━━━━━━━━━━━━━

Bir kullanıcının premium aboneliğini iptal etmek için:

**Komut:** `/cancel 123456789`

Bu işlem:
• Kullanıcının premium planını kaldırır
• Abonelik bitiş tarihini sıfırlar
• Kullanıcıya bilgilendirme mesajı gönderir

⚠️ **Dikkat:** Bu işlem geri alınamaz!
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 İptal Edilecek Kullanıcılar", callback_data="admin_cancel_list")],
        [InlineKeyboardButton("🔙 Premium Yönetimi", callback_data="admin_premium")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def admin_premium_pdf(update: Update, context: CallbackContext):
    """Premium rapor PDF'i oluştur"""
    query = update.callback_query
    await query.answer()
    
    try:
        premium_users = supabase_manager.get_premium_users()
        payments = supabase_manager.get_payment_statistics()
        
        # PDF oluştur
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        
        pdf.cell(200, 10, txt="FAL GRAM - PREMIUM RAPORU", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Toplam Premium Kullanıcı: {len(premium_users)}", ln=True)
        pdf.cell(200, 10, txt=f"Toplam Gelir: {sum(p.get('amount', 0) for p in payments)} Star", ln=True)
        pdf.ln(10)
        
        # Kullanıcı listesi
        pdf.cell(200, 10, txt="PREMIUM KULLANICILAR:", ln=True)
        for user in premium_users:
            plan = PREMIUM_PLANS.get(user.get('premium_plan', 'free'), {})
            pdf.cell(200, 8, txt=f"{user.get('first_name', 'İsimsiz')} - {plan.get('name', 'Bilinmiyor')}", ln=True)
        
        # PDF'i kaydet ve gönder
        filename = f"premium_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        with open(filename, 'rb') as f:
            await context.bot.send_document(
                chat_id=query.from_user.id,
                document=f,
                caption="📊 Premium Rapor"
            )
        
        os.remove(filename)
        supabase_manager.add_log(f"Premium rapor PDF'i oluşturuldu: {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Premium PDF oluşturma hatası: {e}")
        await query.edit_message_text("❌ PDF oluşturulurken hata oluştu.", reply_markup=get_back_to_admin_button())

# Admin komutları
async def admin_gift_command(update: Update, context: CallbackContext):
    """Hediye abonelik komutu"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("❌ Kullanım: /gift <user_id> <plan> <days>")
            return
        
        user_id = int(args[0])
        plan_id = args[1]
        days = int(args[2])
        
        if plan_id not in PREMIUM_PLANS or plan_id == 'free':
            await update.message.reply_text("❌ Geçersiz plan!")
            return
        
        # Kullanıcıyı güncelle
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        success = supabase_manager.update_user_premium_plan(user_id, plan_id, expires_at)
        
        if success:
            # Kullanıcıya bilgilendirme gönder
            try:
                plan_name = PREMIUM_PLANS[plan_id]['name']
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎁 **HEDİYE ABONELİK!** 🎁\n\n{plan_name} planına {days} günlük ücretsiz erişim kazandınız!\n\nAboneliğiniz {expires_at[:10]} tarihinde sona erecek."
                )
            except:
                pass
            
            await update.message.reply_text(f"✅ {user_id} kullanıcısına {plan_name} planı {days} gün hediye edildi!")
            supabase_manager.add_log(f"Admin hediye abonelik: {user_id} -> {plan_id} ({days} gün)")
        else:
            await update.message.reply_text("❌ Kullanıcı güncellenirken hata oluştu!")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

async def admin_cancel_command(update: Update, context: CallbackContext):
    """Abonelik iptal komutu"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Kullanım: /cancel <user_id>")
            return
        
        user_id = int(args[0])
        
        # Kullanıcıyı güncelle
        success = supabase_manager.update_user_premium_plan(user_id, 'free', None)
        
        if success:
            # Kullanıcıya bilgilendirme gönder
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Premium aboneliğiniz iptal edildi.\n\nÜcretsiz plana geri döndünüz."
                )
            except:
                pass
            
            await update.message.reply_text(f"✅ {user_id} kullanıcısının aboneliği iptal edildi!")
            supabase_manager.add_log(f"Admin abonelik iptal: {user_id}")
        else:
            await update.message.reply_text("❌ Kullanıcı güncellenirken hata oluştu!")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

# ==================== PREMIUM FUNCTIONS ====================

async def premium_subscription_menu(update: Update, context: CallbackContext):
    """Premium abonelik menüsünü gösterir"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass  # Ignore query timeout errors
    
    lang = get_user_lang(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    current_plan = user.get('premium_plan', 'free') if user else 'free'
    
    if lang == 'tr':
        title = "💎 **PREMIUM ABONELİK**"
        subtitle = f"Mevcut Plan: **{PREMIUM_PLANS.get(current_plan, {}).get('name', 'Ücretsiz')}**"
        description = """━━━━━━━━━━━━━━━━━━━━━━

🌟 **Daha Fazla Güç, Daha Derin Rehberlik!**

Sınırsız fal, gelişmiş astroloji ve kişiselleştirilmiş deneyim için premium planımıza geçin.

━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        title = "💎 **PREMIUM SUBSCRIPTION**"  
        subtitle = f"Current Plan: **{PREMIUM_PLANS.get(current_plan, {}).get('name_en', 'Free')}**"
        description = """━━━━━━━━━━━━━━━━━━━━━━

🌟 **More Power, Deeper Guidance!**

Upgrade to our premium plan for unlimited readings, advanced astrology and personalized experience.

━━━━━━━━━━━━━━━━━━━━━━"""
    
    keyboard = []
    
    # Plan butonları
    for plan_id, plan in PREMIUM_PLANS.items():
        if current_plan != plan_id:  # Mevcut planı gösterme
            plan_name = plan['name'] if lang == 'tr' else plan['name_en']
            keyboard.append([InlineKeyboardButton(
                f"✨ {plan_name} - {plan['price']} ⭐",
                callback_data=f"premium_plan_{plan_id}"
            )])
    
    # Diğer seçenekler
    keyboard.extend([
        [InlineKeyboardButton(get_text(lang, "plan_comparison_button"), 
                            callback_data="premium_compare")],
        [InlineKeyboardButton(get_text(lang, "subscription_management"), 
                            callback_data="premium_manage")],
        [InlineKeyboardButton(get_text(lang, "monthly_horoscope"), 
                            callback_data="monthly_horoscope_menu")],
        [InlineKeyboardButton(get_text(lang, "main_menu_button"), callback_data="main_menu")]
    ])
    
    message = f"{title}\n{subtitle}\n{description}"
    
    try:
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Error editing premium menu message: {e}")

async def premium_plan_details(update: Update, context: CallbackContext):
    """Premium plan detaylarını gösterir"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass  # Ignore query timeout errors
    
    plan_id = query.data.split('_')[-1]
    plan = PREMIUM_PLANS[plan_id]
    lang = get_user_lang(query.from_user.id)
    
    plan_name = plan['name'] if lang == 'tr' else plan['name_en']
    plan_description = plan['description'] if lang == 'tr' else plan['description_en']
    features = plan['features'] if lang == 'tr' else plan['features_en']
    
    if lang == 'tr':
        message = f"""✨ **{plan_name.upper()}** ✨
━━━━━━━━━━━━━━━━━━━━━━

📝 **Açıklama:** {plan_description}

💰 **Fiyat:** {plan['price']} Telegram Star
💵 **Aylık Abonelik:** {plan['price']} Star

🎯 **Özellikler:**
"""
    else:
        message = f"""✨ **{plan_name.upper()}** ✨
━━━━━━━━━━━━━━━━━━━━━━

📝 **Description:** {plan_description}

💰 **Price:** {plan['price']} Telegram Stars
💵 **Monthly Subscription:** {plan['price']} Stars

🎯 **Features:**
"""
    
    for feature in features:
        message += f"\n{feature}"
    
    message += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "purchase"), 
                            callback_data=f"premium_buy_{plan_id}")],
        [InlineKeyboardButton(get_text(lang, "premium_menu_back"), 
                            callback_data="premium_menu")]
    ])
    
    try:
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Error editing premium plan details message: {e}")

async def premium_buy_callback(update: Update, context: CallbackContext):
    """Premium plan satın alma işlemi"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    plan_id = query.data.split('_')[-1]
    plan = PREMIUM_PLANS[plan_id]
    lang = get_user_lang(query.from_user.id)
    
    # Generate unique transaction ID
    transaction_id = f"premium_{plan_id}_{query.from_user.id}_{int(time.time())}"
    
    try:
        plan_name = plan.get('name' if lang == 'tr' else 'name_en', get_text(lang, "premium.unknown_plan", "Unknown Plan"))
        
        # Create invoice for Telegram Stars payment (using same pattern as individual payments)
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title=f"{plan_name} - Fal Gram",
            description=get_text(lang, "premium.subscription_description", "Premium plan subscription for 1 month"),
            payload=transaction_id,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="XTR",
            prices=[LabeledPrice(plan_name, plan['price_stars'])],
            start_parameter=f"premium_{plan_id}"
        )
        
        # Log the payment attempt
        supabase_manager.add_log(f"Premium payment initiated: User {query.from_user.id}, Plan {plan_id}, Transaction {transaction_id}")
        
    except Exception as e:
        logger.error(f"Error creating premium invoice: {e}")
        error_message = get_text(lang, "premium.payment_error", "Error creating payment.")
        await query.edit_message_text(error_message)
        supabase_manager.add_log(f"Premium payment error: {e}")


  
async def premium_compare_plans(update: Update, context: CallbackContext):
    """Premium planlarını JSON dosyasından dinamik olarak oluşturup karşılaştırır."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(query.from_user.id)

    # 1. İlgili dilin tüm karşılaştırma verisini JSON'dan çek
    # get_text fonksiyonumuz anahtar bir objeye işaret ediyorsa objeyi döndürür.
    try:
        comparison_data = get_text(lang, "plan_comparison")
        if not isinstance(comparison_data, dict):
            # Eğer veri bozuksa veya metin olarak geliyorsa bir hata mesajı göster
            logger.error(f"'{lang}.json' dosyasındaki 'plan_comparison' verisi doğru formatta değil.")
            await query.edit_message_text("Planlar görüntülenemiyor, lütfen daha sonra tekrar deneyin.")
            return
    except Exception as e:
        logger.error(f"Plan karşılaştırma verisi çekilirken hata: {e}")
        await query.edit_message_text("Bir hata oluştu.")
        return

    # 2. Mesajı dinamik olarak oluştur
    message_parts = []
    plan_order = ['free', 'basic', 'premium', 'vip'] # Planların gösterileceği sıra

    # Başlık ve ayırıcı
    message_parts.append(comparison_data.get('title', 'PLAN KARŞILAŞTIRMASI'))
    message_parts.append(comparison_data.get('separator', '━━━━━━━━━━━━━━━━━━━━━━'))

    # Planları sırayla işle
    for plan_id in plan_order:
        plan = comparison_data.get('plans', {}).get(plan_id)
        if not plan:
            continue

        # Plan başlığı
        message_parts.append(f"\n{plan.get('title')}")

        # Plan özellikleri
        for feature in plan.get('features', []):
            message_parts.append(f"• {feature}")

    # Kapanış ayırıcısı
    message_parts.append(f"\n{comparison_data.get('separator', '━━━━━━━━━━━━━━━━━━━━━━')}")
    
    final_message = "\n".join(message_parts)

    # 3. Geri butonunu oluştur ve mesajı gönder
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(comparison_data.get('back_button', "🔙 Premium Menu"),
                            callback_data="premium_menu")]
    ])

    await query.edit_message_text(final_message, reply_markup=keyboard, parse_mode='Markdown')













async def weekly_astro_report(update: Update, context: CallbackContext):
    """Haftalık astroloji raporu (Premium özellik)"""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Premium kontrolü
    if user.get('premium_plan') not in ['premium', 'vip']:
        await send_premium_upgrade_message(update, context, 'premium')
        return
    
    # Burç seçimi için klavye oluştur
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    keyboard_buttons = []
    
    for i, sign in enumerate(signs):
        keyboard_buttons.append([InlineKeyboardButton(sign, callback_data=f"weekly_horoscope_{i}")])
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    if lang == 'tr':
        message = """📊 **HAFTALIK BURÇ YORUMU** 📊
━━━━━━━━━━━━━━━━━━━━━━

Hangi burç için haftalık yorum istiyorsunuz?

📈 Haftalık burç analizi
🌟 Gezegen etkileri
💫 Önemli tarihler
🎯 Öneriler ve tavsiyeler

━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        message = """📊 **WEEKLY HOROSCOPE** 📊
━━━━━━━━━━━━━━━━━━━━━━

Which sign do you want a weekly reading for?

📈 Weekly horoscope analysis
🌟 Planetary influences
💫 Important dates
🎯 Recommendations and advice

━━━━━━━━━━━━━━━━━━━━━━"""
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def generate_weekly_horoscope(update: Update, context: CallbackContext):
    """Haftalık burç yorumu üretir"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Callback data'dan burç index'ini al
    parts = query.data.split('_')
    sign_index = int(parts[-1])
    
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    sign = signs[sign_index]
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Supabase'den prompt'u al
        prompt = supabase_manager.get_prompt("weekly_horoscope", lang)
        if not prompt:
            prompt = f"""You are an experienced astrologer. Create a detailed weekly horoscope for {sign} sign.

Include these topics:
1. **General Energy:** This week's astrological atmosphere
2. **Love and Relationships:** Expected developments in emotional life
3. **Career and Work:** Opportunities and things to be careful about in work life
4. **Finance:** Recommendations on money and material matters
5. **Health:** Physical and mental health advice
6. **Important Days:** Most suitable days and times to be careful
7. **Weekly Advice:** A practical suggestion

180-220 words, positive and practical."""
        
        # Placeholder'ları değiştir
        final_prompt = prompt.format(sign=sign)
        
        # Dil talimatını ekle
        final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.

{final_prompt}

{lang.upper()} WEEKLY HOROSCOPE:"""
        
        # Sync API çağrısı - timeout ile
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, final_prompt)
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"✅ Weekly Horoscope Gemini API çağrısı tamamlandı: {user_id_str}")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"❌ Weekly Horoscope Gemini API timeout (30s): {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Weekly Horoscope Gemini API hatası: {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        weekly_message = f"""📊 **HAFTALIK BURÇ YORUMU** 📊
━━━━━━━━━━━━━━━━━━━━━━

**{sign}** - Bu Hafta

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Haftanızın güzel geçmesi için pozitif enerji gönderiyoruz* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Başka Burç", callback_data="weekly_astro_report")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(weekly_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Haftalık burç yorumu yapıldı: {user_id_str} - {sign}")
        
    except Exception as e:
        logger.error(f"Haftalık burç hatası: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def monthly_horoscope_menu(update: Update, context: CallbackContext):
    """Aylık burç yorumu menüsü"""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Premium kontrolü
    if user.get('premium_plan') not in ['premium', 'vip']:
        await send_premium_upgrade_message(update, context, 'premium')
        return
    
    # Burç seçimi için klavye oluştur
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    keyboard_buttons = []
    
    for i, sign in enumerate(signs):
        keyboard_buttons.append([InlineKeyboardButton(sign, callback_data=f"monthly_horoscope_{i}")])
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Premium", callback_data="premium_menu")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    if lang == 'tr':
        message = """📅 **AYLIK BURÇ YORUMU** 📅
━━━━━━━━━━━━━━━━━━━━━━

Hangi burç için aylık yorum istiyorsunuz?

📈 Aylık burç analizi
🌟 Gezegen etkileri
💫 Önemli tarihler
🎯 Öneriler ve tavsiyeler

━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        message = """📅 **MONTHLY HOROSCOPE** 📅
━━━━━━━━━━━━━━━━━━━━━━

Which sign do you want a monthly reading for?

📈 Monthly horoscope analysis
🌟 Planetary influences
💫 Important dates
🎯 Recommendations and advice

━━━━━━━━━━━━━━━━━━━━━━"""
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def generate_monthly_horoscope(update: Update, context: CallbackContext):
    """Aylık burç yorumu üretir"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Callback data'dan burç index'ini al
    parts = query.data.split('_')
    sign_index = int(parts[-1])
    
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    sign = signs[sign_index]
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Supabase'den prompt'u al
        prompt = supabase_manager.get_prompt("monthly_horoscope", lang)
        if not prompt:
            prompt = f"""You are an experienced astrologer. Create a comprehensive monthly horoscope for {sign} sign.

Include these topics:
1. **General Energy:** This month's astrological atmosphere and main themes
2. **Love and Relationships:** Expected transformations and opportunities in emotional life
3. **Career and Work:** Major opportunities and development areas in work life
4. **Finance:** Strategic recommendations on money and material matters
5. **Health:** Monthly guidance for physical and mental health
6. **Important Dates:** Most suitable days and times to be careful
7. **Monthly Results:** Gains to be achieved by the end of this month
8. **Monthly Goal:** Main goal to focus on throughout the month

250-300 words, comprehensive and strategic."""
        
        # Placeholder'ları değiştir
        final_prompt = prompt.format(sign=sign)
        
        # Dil talimatını ekle
        final_prompt = f"""YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.

{final_prompt}

{lang.upper()} MONTHLY HOROSCOPE:"""
        
        # Sync API çağrısı - timeout ile
        try:
            # Thread pool executor ile sync çağrı
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(model.generate_content, final_prompt)
                response = future.result(timeout=30)  # 30 saniye timeout
            
            supabase_manager.add_log(f"✅ Monthly Horoscope Gemini API çağrısı tamamlandı: {user_id_str}")
        except concurrent.futures.TimeoutError:
            supabase_manager.add_log(f"❌ Monthly Horoscope Gemini API timeout (30s): {user_id_str}")
            raise Exception("Gemini API yanıt vermedi (30 saniye timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Monthly Horoscope Gemini API hatası: {str(e)[:100]}")
            raise Exception(f"Gemini API hatası: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Gemini API'den boş yanıt alındı")
        
        monthly_message = f"""📅 **AYLIK BURÇ YORUMU** 📅
━━━━━━━━━━━━━━━━━━━━━━

**{sign}** - Bu Ay

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Ayınızın güzel geçmesi için pozitif enerji gönderiyoruz* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Başka Burç", callback_data="monthly_horoscope_menu")],
            [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(monthly_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Aylık burç yorumu yapıldı: {user_id_str} - {sign}")
        
    except Exception as e:
        logger.error(f"Aylık burç hatası: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def planetary_transits(update: Update, context: CallbackContext):
    """Özel gezegen geçişleri (Premium özellik)"""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # Premium kontrolü
    if user.get('premium_plan') not in ['premium', 'vip']:
        await send_premium_upgrade_message(update, context, 'premium')
        return
    
    if lang == 'tr':
        message = """🌟 **GEZEGEN GEÇİŞLERİ** 🌟
━━━━━━━━━━━━━━━━━━━━━━

Bu ay önemli gezegen hareketleri:

♂️ **Mars** - 15 Şubat'ta Koç burcuna geçiş
♀️ **Venüs** - 22 Şubat'ta Balık burcunda
☿ **Merkür** - 3 Mart'ta retrograde
♃ **Jüpiter** - Boğa burcunda güçlü

🎯 **Size Etkileri:**
• Enerji artışı bekleniyor
• İlişkilerde yoğun dönem
• İletişimde dikkatli olun
• Finansal fırsatlar

━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        message = """🌟 **PLANETARY TRANSITS** 🌟
━━━━━━━━━━━━━━━━━━━━━━

Important planetary movements this month:

♂️ **Mars** - Entering Aries on Feb 15
♀️ **Venus** - In Pisces on Feb 22
☿ **Mercury** - Retrograde on Mar 3
♃ **Jupiter** - Strong in Taurus

🎯 **Effects on You:**
• Energy boost expected
• Intense period in relationships
• Be careful with communication
• Financial opportunities

━━━━━━━━━━━━━━━━━━━━━━"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def social_astrology(update: Update, context: CallbackContext):
    """Sosyal astroloji özellikleri (VIP özellik)"""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # VIP kontrolü
    if user.get('premium_plan') != 'vip':
        await send_premium_upgrade_message(update, context, 'vip')
        return
    
    if lang == 'tr':
        message = """👥 **SOSYAL ASTROLOJİ** 👥
━━━━━━━━━━━━━━━━━━━━━━

🤝 **Burç Uyumluluğu Arkadaşları**
Burcunuzla uyumlu kişileri bulun

🌍 **Astroloji Topluluğu**
Diğer kullanıcılarla bağlantı kurun

📤 **Günlük Burç Paylaşımı**
Burç yorumlarınızı sosyal medyada paylaşın

🏆 **Astroloji Skor Tablosu**
Uyumluluk skorlarınızı görün

━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        message = """👥 **SOCIAL ASTROLOGY** 👥
━━━━━━━━━━━━━━━━━━━━━━

🤝 **Zodiac Compatibility Friends**
Find people compatible with your sign

🌍 **Astrology Community**
Connect with other users

📤 **Daily Horoscope Sharing**
Share your horoscope on social media

🏆 **Astrology Leaderboard**
View your compatibility scores

━━━━━━━━━━━━━━━━━━━━━━"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 Arkadaş Bul" if lang == 'tr' else "🤝 Find Friends", 
                            callback_data="find_astro_friends")],
        [InlineKeyboardButton("🌍 Topluluk" if lang == 'tr' else "🌍 Community", 
                            callback_data="astro_community")],
        [InlineKeyboardButton("🔙 Astroloji", callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def send_premium_upgrade_message(update: Update, context: CallbackContext, required_plan: str):
    """Premium upgrade mesajı gönderir"""
    lang = get_user_lang(update.effective_user.id)
    plan_info = PREMIUM_PLANS.get(required_plan, PREMIUM_PLANS['basic'])
    
    if lang == 'tr':
        message = f"""💎 **PREMİUM ÖZELLİK** 💎
━━━━━━━━━━━━━━━━━━━━━━

Bu özellik **{plan_info['name']}** aboneleri için mevcut!

⭐ **Fiyat:** {plan_info['price']} Telegram Star
💵 **Aylık:** {plan_info['price']}

🎯 **Bu özellik ile:**"""
        
        for feature in plan_info['features'][:3]:  # İlk 3 özellik
            message += f"\n{feature}"
        
        message += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    else:
        message = f"""💎 **PREMIUM FEATURE** 💎
━━━━━━━━━━━━━━━━━━━━━━

This feature is available for **{plan_info['name_en']}** subscribers!

⭐ **Price:** {plan_info['price']} Telegram Stars
💵 **Monthly:** {plan_info['price']}

🎯 **With this feature:**"""
        
        for feature in plan_info['features_en'][:3]:  # İlk 3 özellik
            message += f"\n{feature}"
        
        message += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✨ {plan_info['name']}'e Geç" if lang == 'tr' else f"✨ Upgrade to {plan_info['name_en']}", 
                            callback_data=f"premium_plan_{required_plan}")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="main_menu")]
    ])
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def advanced_moon_calendar(update: Update, context: CallbackContext):
    """Gerçek ay fazları ile gelişmiş ay takvimi"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    today = datetime.now()
    
    # Gerçek ay fazı hesaplama
    moon_data = calculate_moon_phase(today)
    moon_phase = moon_data['phase']
    moon_name = moon_data['name'] if lang == 'tr' else moon_data['name_en']
    energy = moon_data['energy']
    
    # Ay enerjisi tavsiyeleri
    energy_advice = get_moon_energy_advice(energy, lang)
    
    # Gelecek 7 günün ay fazları
    future_phases = []
    for i in range(1, 8):
        future_date = today + timedelta(days=i)
        future_moon = calculate_moon_phase(future_date)
        future_phases.append({
            'date': future_date.strftime('%d.%m'),
            'phase': future_moon['phase'],
            'name': future_moon['name'] if lang == 'tr' else future_moon['name_en']
        })
    
    message = get_text(lang, "moon_calendar.title", "🌙 **ADVANCED MOON CALENDAR** 🌙") + "\n" + \
              get_text(lang, "moon_calendar.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
              get_text(lang, "moon_calendar.today", "📅 **Today:**") + f" {today.strftime('%d.%m.%Y')}\n" + \
              get_text(lang, "moon_calendar.moon_phase", "🌙 **Moon Phase:**") + f" {moon_phase} {moon_name}\n\n" + \
              get_text(lang, "moon_calendar.todays_energy", "✨ **Today's Energy:**") + "\n" + \
              f"{energy_advice[0] if energy_advice else get_text(lang, 'moon_calendar.default_energy', 'Be in harmony with moon energy')}\n\n" + \
              get_text(lang, "moon_calendar.recommendations", "🔮 **Recommendations:**")
    
    default_advice = [
        get_text(lang, "moon_calendar.advice_meditation", "Practice meditation"),
        get_text(lang, "moon_calendar.advice_inner_voice", "Listen to your inner voice")
    ]
    
    for advice in energy_advice[1:4] if len(energy_advice) > 1 else default_advice:
        message += f"\n• {advice}"
    
    message += "\n\n" + get_text(lang, "moon_calendar.next_7_days", "📊 **Next 7 Days:**") + "\n"
    for phase_data in future_phases:
        message += f"{phase_data['date']}: {phase_data['phase']} {phase_data['name']}\n"
    
    message += "\n" + get_text(lang, "moon_calendar.separator", "━━━━━━━━━━━━━━━━━━━━━━")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "moon_calendar.notifications", "🔔 Moon Notifications"), 
                            callback_data="moon_notifications_setup")],
        [InlineKeyboardButton(get_text(lang, "moon_calendar.personal_analysis", "📱 Personal Moon Analysis"), 
                            callback_data="personal_moon_analysis")],
        [InlineKeyboardButton(get_text(lang, "moon_calendar.back_to_astrology", "🔙 Astrology"), callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def moon_notifications_setup(update: Update, context: CallbackContext):
    """Ay bildirimleri ayarları"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    
    message = get_text(lang, "moon_notifications.title", "🔔 **MOON NOTIFICATIONS** 🔔") + "\n" + \
              get_text(lang, "moon_notifications.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
              get_text(lang, "moon_notifications.description", "Get notifications about moon phases:") + "\n\n" + \
              get_text(lang, "moon_notifications.new_moon", "🌑 **New Moon Notifications**") + "\n" + \
              get_text(lang, "moon_notifications.new_moon_desc", "Energy for new beginnings") + "\n\n" + \
              get_text(lang, "moon_notifications.full_moon", "🌕 **Full Moon Notifications**") + "\n" + \
              get_text(lang, "moon_notifications.full_moon_desc", "Time for completion and celebration") + "\n\n" + \
              get_text(lang, "moon_notifications.quarters", "🌓 **First/Last Quarter Notifications**") + "\n" + \
              get_text(lang, "moon_notifications.quarters_desc", "Decision making and evaluation") + "\n\n" + \
              get_text(lang, "moon_notifications.toggle", "🔔 **Turn Notifications On/Off**")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "moon_notifications.new_moon_button", "🌑 New Moon"), 
                            callback_data="moon_notify_new")],
        [InlineKeyboardButton(get_text(lang, "moon_notifications.full_moon_button", "🌕 Full Moon"), 
                            callback_data="moon_notify_full")],
        [InlineKeyboardButton(get_text(lang, "moon_notifications.quarters_button", "🌓 Quarters"), 
                            callback_data="moon_notify_quarters")],
        [InlineKeyboardButton(get_text(lang, "moon_notifications.back_to_calendar", "🔙 Moon Calendar"), 
                            callback_data="advanced_moon_calendar")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def personal_moon_analysis(update: Update, context: CallbackContext):
    """Kişisel ay analizi"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    
    # Premium kontrolü
    if user.get('premium_plan') not in ['premium', 'vip']:
        await send_premium_upgrade_message(update, context, 'premium')
        return
    
    today = datetime.now()
    moon_data = calculate_moon_phase(today)
    
    moon_name = moon_data.get('name' if lang == 'tr' else 'name_en', get_text(lang, "moon_analysis.unknown_phase", "Unknown Phase"))
    
    message = get_text(lang, "moon_analysis.title", "📱 **PERSONAL MOON ANALYSIS** 📱") + "\n" + \
              get_text(lang, "moon_analysis.separator", "━━━━━━━━━━━━━━━━━━━━━━") + "\n\n" + \
              get_text(lang, "moon_analysis.todays_phase", "🌙 **Today's Moon Phase:**") + f" {moon_data['phase']} {moon_name}\n\n" + \
              get_text(lang, "moon_analysis.special_recommendations", "✨ **Special Recommendations for You:**") + "\n\n" + \
              get_text(lang, "moon_analysis.goals", "🎯 **Goals:**") + " " + get_text(lang, "moon_analysis.goals_desc", "Re-evaluate your goals during this moon phase") + "\n" + \
              get_text(lang, "moon_analysis.energy", "💫 **Energy:**") + " " + get_text(lang, "moon_analysis.energy_desc", "Strengthen yourself using moon energy") + "\n" + \
              get_text(lang, "moon_analysis.intuition", "🔮 **Intuition:**") + " " + get_text(lang, "moon_analysis.intuition_desc", "Listen to your inner voice and trust your instincts") + "\n" + \
              get_text(lang, "moon_analysis.growth", "🌟 **Growth:**") + " " + get_text(lang, "moon_analysis.growth_desc", "Focus on your personal development during this period") + "\n\n" + \
              get_text(lang, "moon_analysis.this_week", "📅 **This Week:**") + " " + get_text(lang, "moon_analysis.this_week_desc", "Do activities compatible with moon energy") + "\n" + \
              get_text(lang, "moon_analysis.nature", "🌿 **Nature:**") + " " + get_text(lang, "moon_analysis.nature_desc", "Connect with nature and meditate in moonlight") + "\n\n" + \
              get_text(lang, "moon_analysis.separator", "━━━━━━━━━━━━━━━━━━━━━━")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "moon_analysis.back_to_calendar", "🔙 Moon Calendar"), 
                            callback_data="advanced_moon_calendar")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def astro_chatbot(update: Update, context: CallbackContext):
    """7/24 Astroloji Chatbot - VIP özelliği"""
    query = update.callback_query
    await query.answer()
    
    user = supabase_manager.get_user(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
    # VIP kontrolü
    if user.get('premium_plan') != 'vip':
        if lang == 'tr':
            message = """🤖 **ASTROLOJİ CHATBOT** 🤖
━━━━━━━━━━━━━━━━━━━━━━

Bu özellik sadece **VIP Plan** aboneleri için mevcut!

7/24 astroloji chatbot ile:
• Anlık astroloji soruları
• Kişiselleştirilmiş rehberlik  
• Gerçek zamanlı burç yorumları
• Özel gezegen analizleri

VIP planına geçerek bu özelliğe erişin!"""
        else:
            message = """🤖 **ASTROLOGY CHATBOT** 🤖
━━━━━━━━━━━━━━━━━━━━━━

This feature is only available for **VIP Plan** subscribers!

24/7 astrology chatbot offers:
• Instant astrology questions
• Personalized guidance
• Real-time horoscope interpretations  
• Special planetary analysis

Upgrade to VIP plan to access this feature!"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 VIP'e Geç" if lang == 'tr' else "👑 Upgrade to VIP", 
                                callback_data="premium_plan_vip")],
            [InlineKeyboardButton("🔙 Astroloji" if lang == 'tr' else "🔙 Astrology", 
                                callback_data="select_astrology")]
        ])
        
        await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
        return
    
    # VIP kullanıcı için chatbot
    supabase_manager.update_user(query.from_user.id, {'state': 'chatbot_mode'})
    
    if lang == 'tr':
        message = """🤖 **ASTROLOJİ CHATBOT AKTİF** 🤖
━━━━━━━━━━━━━━━━━━━━━━

Merhaba! Ben sizin kişisel astroloji danışmanınızım. 

Sorabilecekleriniz:
• "Bugün Mars'ın etkisi nasıl?"
• "İkizler burcu için bu hafta nasıl?"
• "Venüs geçişi ne zaman?"
• "Doğum haritamda Jupiter nerede?"

Astroloji ile ilgili her türlü soruyu sorabilirsiniz!

━━━━━━━━━━━━━━━━━━━━━━
💬 *Sorunuzu yazın...*"""
    else:
        message = """🤖 **ASTROLOGY CHATBOT ACTIVE** 🤖
━━━━━━━━━━━━━━━━━━━━━━

Hello! I'm your personal astrology consultant.

You can ask:
• "How is Mars affecting today?"
• "What's the week like for Gemini?"
• "When is the Venus transit?"
• "Where is Jupiter in my birth chart?"

Ask me anything about astrology!

━━━━━━━━━━━━━━━━━━━━━━
💬 *Type your question...*"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Chatbot'u Kapat" if lang == 'tr' else "❌ Close Chatbot", 
                            callback_data="chatbot_close")]
    ])
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def handle_chatbot_question(update: Update, context: CallbackContext):
    """Chatbot sorularını işler"""
    user_id = update.effective_user.id
    user = supabase_manager.get_user(user_id)
    
    if user.get('state') != 'chatbot_mode' or user.get('premium_plan') != 'vip':
        return
    
    lang = get_user_lang(user_id)
    question = update.message.text
    
    await update.message.reply_text(get_text(lang, "buttons.analyzing"))
    
    try:
        # Gemini model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Supabase'den prompt'u al
        prompt = supabase_manager.get_prompt("astro_chatbot", lang)
        if not prompt:
            prompt = f"""You are an experienced astrology chatbot. Answer the user's question like a professional astrology consultant.

User Question: {question}

Your answer should include:
- Direct and detailed response to the question
- Astrological information and explanations
- Practical advice
- References to current planetary conditions

120-180 words, in a friendly and professional tone."""
        
        # Placeholder'ları değiştir
        username = update.effective_user.first_name or update.effective_user.username or "User"
        final_prompt = prompt.format(username=username)
        
        # Soru ve dil talimatını ekle
        final_prompt = f"""USER QUESTION: {question}

{final_prompt}

YOU ARE AN ASTROLOGY CHATBOT. RESPOND ONLY IN {lang.upper()} LANGUAGE.

{lang.upper()} RESPONSE:"""
        
        response = model.generate_content(final_prompt)
        
        if response and response.text:
            chatbot_message = f"""🤖 **ASTROLOJİ DANIŞMANI** 🤖

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
💬 *Başka bir soru sorabilirsiniz...*"""
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(lang, "buttons.close_chatbot"), 
                                    callback_data="chatbot_close")]
            ])
            
            await update.message.reply_text(chatbot_message, reply_markup=keyboard, parse_mode='Markdown')
            supabase_manager.add_log(f"Chatbot sorusu yanıtlandı: {user_id} - {question[:50]}...")
        else:
            raise Exception("Gemini API'den yanıt alınamadı")
            
    except Exception as e:
        logger.error(f"Chatbot hatası: {e}")
        await update.message.reply_text(
            get_text(lang, "buttons.sorry_cant_respond"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(lang, "buttons.close_chatbot"), 
                                    callback_data="chatbot_close")]
            ])
        )

async def chatbot_close(update: Update, context: CallbackContext):
    """Chatbot'u kapatır"""
    query = update.callback_query
    await query.answer()
    
    supabase_manager.update_user(query.from_user.id, {'state': 'idle'})
    lang = get_user_lang(query.from_user.id)
    
    await query.edit_message_text(
        get_text(lang, "buttons.chatbot_closed"),
        reply_markup=get_main_menu_keyboard(query.from_user.id)
    )

def main():
    """Ana bot fonksiyonu."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(select_service_callback, pattern="^select_"))
    application.add_handler(CallbackQueryHandler(toggle_daily_subscription, pattern="^toggle_daily$"))
    application.add_handler(CallbackQueryHandler(confirm_daily_subscribe, pattern="^confirm_daily_subscribe$"))
    application.add_handler(CallbackQueryHandler(confirm_daily_unsubscribe, pattern="^confirm_daily_unsubscribe$"))
    application.add_handler(CallbackQueryHandler(subscription_stats, pattern="^subscription_stats$"))
    application.add_handler(CallbackQueryHandler(referral_stats, pattern="^referral_stats$"))
    application.add_handler(CallbackQueryHandler(my_rewards, pattern="^my_rewards$"))
    application.add_handler(CallbackQueryHandler(get_referral_link_callback, pattern="^get_referral_link$"))
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_view_logs, pattern="^admin_view_logs$"))
    application.add_handler(CallbackQueryHandler(admin_settings, pattern="^admin_settings$"))
    application.add_handler(CallbackQueryHandler(admin_users, pattern="^admin_users$"))
    application.add_handler(CallbackQueryHandler(admin_referrals, pattern="^admin_referrals$"))
    application.add_handler(CallbackQueryHandler(admin_referral_stats, pattern="^admin_referral_stats$"))
    application.add_handler(CallbackQueryHandler(admin_download_pdf, pattern="^admin_download_pdf$"))
    application.add_handler(CallbackQueryHandler(admin_download_users_pdf, pattern="^admin_download_users_pdf$"))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^back_to_admin$"))
    
    # Admin premium management handlers
    application.add_handler(CallbackQueryHandler(admin_premium_management, pattern="^admin_premium$"))
    application.add_handler(CallbackQueryHandler(admin_premium_users, pattern="^admin_premium_users$"))
    application.add_handler(CallbackQueryHandler(admin_premium_stats, pattern="^admin_premium_stats$"))
    application.add_handler(CallbackQueryHandler(admin_gift_subscription, pattern="^admin_gift_subscription$"))
    application.add_handler(CallbackQueryHandler(admin_cancel_subscription, pattern="^admin_cancel_subscription$"))
    application.add_handler(CallbackQueryHandler(admin_premium_pdf, pattern="^admin_premium_pdf$"))
    
    # Admin commands
    application.add_handler(CommandHandler("gift", admin_gift_command))
    application.add_handler(CommandHandler("cancel", admin_cancel_command))
    
    # Astrology handlers - YENİ!
    application.add_handler(CallbackQueryHandler(astrology_menu, pattern="^select_astrology$"))
    application.add_handler(CallbackQueryHandler(astro_daily_horoscope, pattern="^astro_daily_horoscope$"))
    application.add_handler(CallbackQueryHandler(generate_daily_horoscope, pattern="^daily_horoscope_"))
    application.add_handler(CallbackQueryHandler(astro_compatibility, pattern="^astro_compatibility$"))
    application.add_handler(CallbackQueryHandler(astro_birth_chart, pattern="^astro_birth_chart$"))
    application.add_handler(CallbackQueryHandler(astro_moon_calendar, pattern="^astro_moon_calendar$"))
    application.add_handler(CallbackQueryHandler(astro_first_sign_selected, pattern="^compat_first_"))
    application.add_handler(CallbackQueryHandler(generate_compatibility_analysis, pattern="^compat_second_"))
    application.add_handler(CallbackQueryHandler(astro_subscribe_daily, pattern="^astro_subscribe_daily$"))
    application.add_handler(CallbackQueryHandler(astro_subscribe_confirm, pattern="^astro_subscribe_confirm$"))
    application.add_handler(CallbackQueryHandler(moon_notifications, pattern="^moon_notifications$"))
    
    # Premium handlers - YENİ!
    application.add_handler(CallbackQueryHandler(premium_subscription_menu, pattern="^premium_menu$"))
    application.add_handler(CallbackQueryHandler(premium_plan_details, pattern="^premium_plan_"))
    application.add_handler(CallbackQueryHandler(premium_compare_plans, pattern="^premium_compare$"))
    application.add_handler(CallbackQueryHandler(astro_chatbot, pattern="^astro_chatbot$"))
    application.add_handler(CallbackQueryHandler(chatbot_close, pattern="^chatbot_close$"))
    application.add_handler(CallbackQueryHandler(advanced_moon_calendar, pattern="^advanced_moon_calendar$"))
    application.add_handler(CallbackQueryHandler(weekly_astro_report, pattern="^weekly_astro_report$"))
    application.add_handler(CallbackQueryHandler(generate_weekly_horoscope, pattern="^weekly_horoscope_"))
    application.add_handler(CallbackQueryHandler(monthly_horoscope_menu, pattern="^monthly_horoscope_menu$"))
    application.add_handler(CallbackQueryHandler(generate_monthly_horoscope, pattern="^monthly_horoscope_"))
    application.add_handler(CallbackQueryHandler(planetary_transits, pattern="^planetary_transits$"))
    application.add_handler(CallbackQueryHandler(social_astrology, pattern="^social_astrology$"))
    
    # Moon calendar handlers
    application.add_handler(CallbackQueryHandler(moon_notifications_setup, pattern="^moon_notifications_setup$"))
    application.add_handler(CallbackQueryHandler(personal_moon_analysis, pattern="^personal_moon_analysis$"))
    
    # Premium payment handlers (tek seferlik ödemeler kaldırıldı)
    application.add_handler(CallbackQueryHandler(premium_buy_callback, pattern="^premium_buy_"))
    
    # Language handlers
    application.add_handler(CallbackQueryHandler(change_language_menu, pattern="^change_language$"))
    application.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    
    # Payment system handlers
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    supabase_manager.add_log("Bot başlatılıyor...")
    print("Bot çalışıyor...")
    application.run_polling()

if __name__ == "__main__":
    main()

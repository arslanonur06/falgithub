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
    """Get localized text for a given key"""
    # Get the text from locale file
    text = LOCALES.get(lang, {}).get(key, LOCALES.get('en', {}).get(key, key))
    
    # Format with any provided kwargs
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    
    return text

def get_user_language(user_id: int) -> str:
    """Get user's preferred language from database"""
    user = supabase_manager.get_user(user_id)
    return user.get('language', 'tr') if user else 'tr'

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

def get_text(lang: str, key: str, **kwargs) -> str:
    """Dil dosyasından metin alır ve parametreleri yerleştirir."""
    text = locales.get(lang, locales["tr"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

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
        [InlineKeyboardButton("🇪🇸 Español", callback_data='set_lang_es'),
         InlineKeyboardButton("🇫🇷 Français", callback_data='set_lang_fr')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='set_lang_ru'),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data='set_lang_de')],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data='set_lang_ar'),
         InlineKeyboardButton("🇮🇹 Italiano", callback_data='set_lang_it')],
        [InlineKeyboardButton("🇵🇹 Português", callback_data='set_lang_pt')]
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
                    new_count = referrer.get('referred_count', 0) + 1
                    new_earnings = referrer.get('referral_earnings', 0) + 50
                    supabase_manager.update_user(referrer_user_id, {'referred_count': new_count, 'referral_earnings': new_earnings})
                    supabase_manager.add_log(f"Referral işlemi tamamlandı: {user_id_str} - Referrer: {referrer_id}")
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


# --- Handler Implementations ---

async def show_main_menu(query, lang):
    """Show main menu"""
    await safe_edit_message(
        query,
        get_text("start_message", lang),
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
    card = random.choice(TAROT_CARDS)
    
    await query.message.reply_text(
        get_text("tarot_card_drawn", lang, card=card),
        parse_mode='Markdown'
    )
    
    # Generate interpretation
    await generate_tarot_interpretation(query, card, lang)

async def handle_dream_analysis(query, lang):
    """Handle dream analysis selection"""
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
    
    is_subscribed = user.get('daily_card_subscription', False)
    
    if is_subscribed:
        # Unsubscribe
        supabase_manager.update_user(user_id, {'daily_card_subscription': False})
        message = get_text("daily_card_unsubscribe", lang)
    else:
        # Subscribe
        supabase_manager.update_user(user_id, {'daily_card_subscription': True})
        message = get_text("daily_card_subscribe", lang)
    
    keyboard = [[InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_referral_info(query, lang):
    """Show referral information"""
    user_id = query.from_user.id
    user = supabase_manager.get_user(user_id)
    
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    referred_count = user.get('referred_count', 0)
    referral_earnings = user.get('referral_earnings', 0)
    
    message = get_text("referral_info_message", lang, 
                      referral_link=referral_link,
                      referred_count=referred_count,
                      referral_earnings=referral_earnings)
    
    keyboard = [[InlineKeyboardButton(get_text("main_menu_button", lang), callback_data='main_menu')]]
    
    await safe_edit_message(
        query,
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_language_menu(query):
    """Show language selection menu"""
    await safe_edit_message(
        query,
        get_text("language_selection", "en"),  # Always show in English
        reply_markup=create_language_keyboard(),
        parse_mode='Markdown'
    )

async def handle_language_change(query, new_lang):
    """Handle language change"""
    user_id = query.from_user.id
    
    # Update user language
    supabase_manager.update_user(user_id, {'language': new_lang})
    
    # Send confirmation in new language
    lang_name = LOCALES[new_lang].get('language_name', new_lang)
    message = get_text("language_updated", new_lang, lang=lang_name)
    
    await safe_edit_message(
        query,
        message,
        reply_markup=create_main_menu_keyboard(new_lang),
        parse_mode='Markdown'
    )


# --- Message Handlers ---

async def handle_message(update: Update, context: CallbackContext):
    """Handle all text messages"""
    if not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    text = update.message.text
    
    # Check if user is in a conversation state
    user_data = context.user_data
    
    if user_data.get('waiting_for') == 'dream_text':
        await process_dream_text(update, context, text, lang)
    elif user_data.get('waiting_for') == 'birth_info':
        await process_birth_info(update, context, text, lang)
    elif user_data.get('chatbot_active'):
        await handle_chatbot_question(update, context, text, lang)
    else:
        # Default response
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
    await generate_coffee_fortune(update, photo_bytes, lang)


# --- Main Function ---

def main():
    """Ana fonksiyon"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("gift", gift))
    application.add_handler(CommandHandler("cancel", cancel))
    
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
    
    # Start scheduler
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

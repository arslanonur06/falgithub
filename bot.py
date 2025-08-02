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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            # Return time until oldest request expires
            return 60 - (now - user_requests[0])
        return 0

# Global rate limiter instance
gemini_rate_limiter = GeminiRateLimiter(max_requests_per_minute=60)

# --- Environment Variables and Constants ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

FREE_READING_LIMIT = 5
PAID_READING_STARS = 250
CHOOSING, TYPING_REPLY = range(2)

# Premium Plan Definitions
PREMIUM_PLANS = {
    'free': {
        'name': 'Ücretsiz',
        'name_en': 'Free',
        'name_es': 'Gratis',
        'name_fr': 'Gratuit',
        'price': 0,
        'price_stars': 0,
        'description': 'Temel özelliklerle başlayın',
        'description_en': 'Start with basic features',
        'description_es': 'Comienza con funciones básicas',
        'description_fr': 'Commencez avec des fonctionnalités de base',
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
        ],
        'features_es': [
            '☕ 5 lecturas gratis (Café, Tarot, Sueño)',
            '♈ Horóscopo diario',
            '🔮 Características básicas de astrología',
            '📱 Soporte básico de chatbot',
            '🎁 Bonos de referidos'
        ],
        'features_fr': [
            '☕ 5 lectures gratuites (Café, Tarot, Rêve)',
            '♈ Horoscope quotidien',
            '🔮 Fonctionnalités d\'astrologie de base',
            '📱 Support chatbot de base',
            '🎁 Bonus de parrainage'
        ]
    },
    'basic': {
        'name': 'Temel Plan',
        'name_en': 'Basic Plan',
        'name_es': 'Plan Básico',
        'name_fr': 'Plan de Base',
        'price': 500,
        'price_stars': 500,
        'description': 'Sınırsız fal ve gelişmiş özellikler',
        'description_en': 'Unlimited readings and advanced features',
        'description_es': 'Lecturas ilimitadas y funciones avanzadas',
        'description_fr': 'Lectures illimitées et fonctionnalités avancées',
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
        ],
        'features_es': [
            '♾️ Lecturas ilimitadas (Café, Tarot, Sueño)',
            '📊 Reporte semanal de horóscopo',
            '🔮 Análisis avanzado de astrología',
            '💫 Interpretación de carta natal',
            '🌙 Características del calendario lunar',
            '💬 Chatbot avanzado',
            '🎯 Recomendaciones personalizadas',
            '📈 Historial detallado de lecturas',
            '🔔 Notificaciones especiales'
        ],
        'features_fr': [
            '♾️ Lectures illimitées (Café, Tarot, Rêve)',
            '📊 Rapport d\'horoscope hebdomadaire',
            '🔮 Analyse astrologique avancée',
            '💫 Interprétation de carte natale',
            '🌙 Fonctionnalités du calendrier lunaire',
            '💬 Chatbot avancé',
            '🎯 Recommandations personnalisées',
            '📈 Historique détaillé des lectures',
            '🔔 Notifications spéciales'
        ]
    },
    'premium': {
        'name': 'Premium Plan',
        'name_en': 'Premium Plan',
        'name_es': 'Plan Premium',
        'name_fr': 'Plan Premium',
        'price': 1000,
        'price_stars': 1000,
        'description': 'Tam astroloji paketi ve özel özellikler',
        'description_en': 'Complete astrology package and special features',
        'description_es': 'Paquete completo de astrología y funciones especiales',
        'description_fr': 'Pack d\'astrologie complet et fonctionnalités spéciales',
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
        ],
        'features_es': [
            '✨ Características del Plan Básico',
            '📅 Horóscopo mensual',
            '🪐 Análisis de tránsitos planetarios',
            '💕 Compatibilidad zodiacal',
            '🌙 Calendario lunar avanzado',
            '📈 Reportes detallados de astrología',
            '🎯 Recomendaciones personalizadas',
            '🔮 Tipos de lectura especiales',
            '📊 Estadísticas de astrología',
            '🎁 Contenido exclusivo',
            '⚡ Soporte prioritario'
        ],
        'features_fr': [
            '✨ Fonctionnalités du Plan de Base',
            '📅 Horoscope mensuel',
            '🪐 Analyse des transits planétaires',
            '💕 Compatibilité zodiacale',
            '🌙 Calendrier lunaire avancé',
            '📈 Rapports d\'astrologie détaillés',
            '🎯 Recommandations personnalisées',
            '🔮 Types de lecture spéciaux',
            '📊 Statistiques d\'astrologie',
            '🎁 Contenu exclusif',
            '⚡ Support prioritaire'
        ]
    },
    'vip': {
        'name': 'VIP Plan',
        'name_en': 'VIP Plan',
        'name_es': 'Plan VIP',
        'name_fr': 'Plan VIP',
        'price': 2000,
        'price_stars': 2000,
        'description': 'En üst düzey deneyim ve öncelikli destek',
        'description_en': 'Ultimate experience with priority support',
        'description_es': 'Experiencia definitiva con soporte prioritario',
        'description_fr': 'Expérience ultime avec support prioritaire',
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
        ],
        'features_es': [
            '👑 Características del Plan Premium',
            '🤖 Chatbot de Astrología 24/7',
            '👥 Características sociales de astrología',
            '🎁 Contenido VIP exclusivo',
            '⚡ Soporte prioritario',
            '📊 Analíticas avanzadas',
            '🎯 Consultor de astrología personal',
            '🌟 Tipos de lectura VIP exclusivos',
            '💎 Contenido exclusivo ilimitado',
            '🎪 Eventos especiales',
            '📱 Interfaz VIP exclusiva',
            '🔮 Guía personal con IA'
        ],
        'features_fr': [
            '👑 Fonctionnalités du Plan Premium',
            '🤖 Chatbot d\'Astrologie 24/7',
            '👥 Fonctionnalités sociales d\'astrologie',
            '🎁 Contenu VIP exclusif',
            '⚡ Support prioritaire',
            '📊 Analyses avancées',
            '🎯 Consultant en astrologie personnel',
            '🌟 Types de lecture VIP exclusifs',
            '💎 Contenu exclusif illimité',
            '🎪 Événements spéciaux',
            '📱 Interface VIP exclusive',
            '🔮 Guide personnel alimenté par l\'IA'
        ]
    }
}

genai.configure(api_key=GEMINI_API_KEY)

# --- SupabaseManager Class ---
class SupabaseManager:
    def __init__(self, url: str, key: str):
        try:
            self.client: Client = create_client(url, key)
            logger.info("Supabase client successfully initialized.")
        except Exception as e:
            logger.critical(f"Failed to initialize Supabase client: {e}")
            self.client = None

    # --- User Functions ---
    def get_user(self, user_id: int):
        try:
            result = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_user error: {e}")
            return None

    def create_user(self, user_data: dict):
        try:
            result = self.client.table("users").insert(user_data).execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase create_user error: {e}")
            return None
    
    def update_user(self, user_id: int, data: dict):
        try:
            self.client.table("users").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_user error: {e}")
            return False

    def get_all_users(self):
        try:
            result = self.client.table("users").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_all_users error: {e}")
            return []

    def get_subscribed_users(self):
        try:
            result = self.client.table("users").select("id").eq("daily_subscribed", True).execute()
            return [user["id"] for user in result.data]
        except Exception as e:
            logger.error(f"Supabase get_subscribed_users error: {e}")
            return []
    
    def get_premium_users(self):
        """Get premium users"""
        try:
            result = self.client.table("users").select("*").not_.is_("premium_plan", "null").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_premium_users error: {e}")
            return []
    
    def get_user_subscriptions(self):
        """Get all user subscriptions"""
        try:
            result = self.client.table("user_subscriptions").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_user_subscriptions error: {e}")
            return []
    
    def update_user_premium_plan(self, user_id: int, plan_id: str, expires_at=None):
        """Update user's premium plan"""
        try:
            data = {'premium_plan': plan_id}
            if expires_at:
                data['premium_expires_at'] = expires_at
            self.client.table("users").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_user_premium_plan error: {e}")
            return False
    
    def get_payment_statistics(self):
        """Get payment statistics"""
        try:
            result = self.client.table("payment_transactions").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_payment_statistics error: {e}")
            return []
    
    def get_referral_relationships(self):
        """Get referral relationships."""
        try:
            # Get all users and check referral information
            result = self.client.table("users").select("id, first_name, username, referred_count, referral_earnings").execute()
            users = result.data
            
            # Analyze referral relationships
            referral_data = []
            for user in users:
                if user.get('referred_count', 0) > 0:
                    referral_data.append({
                        'user_id': user['id'],
                        'name': user.get('first_name', 'Unknown'),
                        'username': user.get('username', ''),
                        'referred_count': user.get('referred_count', 0),
                        'earnings': user.get('referral_earnings', 0)
                    })
            
            return referral_data
        except Exception as e:
            logger.error(f"Supabase get_referral_relationships error: {e}")
            return []

    # --- Logging Functions ---
    def add_log(self, message: str):
        try:
            self.client.table("logs").insert({"message": message}).execute()
        except Exception as e:
            logger.error(f"Supabase add_log error: {e}")

    def get_logs(self, limit: int = 100):
        try:
            result = self.client.table("logs").select("*").order("timestamp", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Supabase get_logs error: {e}")
            return []

    # --- Config and Prompt Functions ---
    def get_config(self, key: str):
        try:
            result = self.client.table("config").select("value").eq("key", key).single().execute()
            return result.data.get("value") if result.data else None
        except Exception as e:
            logger.error(f"Supabase get_config error: {e}")
            return None

    def update_config(self, key: str, value):
        try:
            self.client.table("config").upsert({"key": key, "value": value}).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_config error: {e}")
            return False

    def get_prompt(self, prompt_type: str, lang: str):
        try:
            result = self.client.table("prompts").select("content").eq("prompt_type", prompt_type).eq("language", lang).single().execute()
            return result.data.get("content") if result.data else None
        except Exception as e:
            logger.error(f"Supabase get_prompt error: {e}")
            return None

    def update_prompt(self, prompt_type: str, lang: str, content: str):
        try:
            self.client.table("prompts").upsert({
                "prompt_type": prompt_type,
                "language": lang,
                "content": content
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase update_prompt error: {e}")
            return False

    def get_tarot_cards(self):
        try:
            cards = self.get_config("tarot_cards")
            if isinstance(cards, str):
                return json.loads(cards)
            return cards or []
        except Exception as e:
            logger.error(f"Supabase get_tarot_cards error: {e}")
            return []

    def get_daily_card_time(self):
        try:
            hour = self.get_config("daily_card_hour")
            minute = self.get_config("daily_card_minute")
            return int(hour) if hour else 9, int(minute) if minute else 0
        except Exception as e:
            logger.error(f"Supabase get_daily_card_time error: {e}")
            return 9, 0

# Global Supabase Manager
supabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)

# --- Moon Phase Calculation Functions ---
def calculate_moon_phase(date=None):
    """Calculate moon phase"""
    if date is None:
        date = datetime.now()
    
    # Moon phase calculation algorithm (simplified)
    # In real application, more complex astronomical calculations would be used
    days_since_new_moon = (date - datetime(2000, 1, 6)).days % 29.53058867
    
    if days_since_new_moon < 3.69:
        return {
            'phase': '🌑',
            'name': 'Yeni Ay',
            'name_en': 'New Moon',
            'name_es': 'Luna Nueva',
            'name_fr': 'Nouvelle Lune',
            'energy': 'new'
        }
    elif days_since_new_moon < 7.38:
        return {
            'phase': '🌒',
            'name': 'İlk Hilal',
            'name_en': 'Waxing Crescent',
            'name_es': 'Luna Creciente',
            'name_fr': 'Premier Croissant',
            'energy': 'waxing'
        }
    elif days_since_new_moon < 11.07:
        return {
            'phase': '🌓',
            'name': 'İlk Dördün',
            'name_en': 'First Quarter',
            'name_es': 'Cuarto Creciente',
            'name_fr': 'Premier Quartier',
            'energy': 'first_quarter'
        }
    elif days_since_new_moon < 14.76:
        return {
            'phase': '🌔',
            'name': 'Şişkin Ay',
            'name_en': 'Waxing Gibbous',
            'name_es': 'Luna Gibosa Creciente',
            'name_fr': 'Gibbeuse Croissante',
            'energy': 'waxing'
        }
    elif days_since_new_moon < 18.45:
        return {
            'phase': '🌕',
            'name': 'Dolunay',
            'name_en': 'Full Moon',
            'name_es': 'Luna Llena',
            'name_fr': 'Pleine Lune',
            'energy': 'full'
        }
    elif days_since_new_moon < 22.14:
        return {
            'phase': '🌖',
            'name': 'Azalan Ay',
            'name_en': 'Waning Gibbous',
            'name_es': 'Luna Gibosa Menguante',
            'name_fr': 'Gibbeuse Décroissante',
            'energy': 'waning'
        }
    elif days_since_new_moon < 25.83:
        return {
            'phase': '🌗',
            'name': 'Son Dördün',
            'name_en': 'Last Quarter',
            'name_es': 'Cuarto Menguante',
            'name_fr': 'Dernier Quartier',
            'energy': 'last_quarter'
        }
    else:
        return {
            'phase': '🌘',
            'name': 'Son Hilal',
            'name_en': 'Waning Crescent',
            'name_es': 'Luna Menguante',
            'name_fr': 'Dernier Croissant',
            'energy': 'waning'
        }

def get_moon_energy_advice(energy, lang='tr'):
    """Give advice based on moon energy"""
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
    elif lang == 'en':
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
    elif lang == 'es':
        advice_map = {
            'new': [
                'Tiempo perfecto para nuevos comienzos',
                'Establece tus intenciones',
                'Inicia nuevos proyectos',
                'Explora tu mundo interior'
            ],
            'waxing': [
                'Tiempo de crecimiento y desarrollo',
                'Aumenta tu energía',
                'Aprovecha nuevas oportunidades',
                'Avanza con pensamientos positivos'
            ],
            'first_quarter': [
                'Tiempo de tomar decisiones',
                'Enfócate en tus metas',
                'Haz planes de acción',
                'Da pasos firmes'
            ],
            'full': [
                'Tiempo de completar y celebrar',
                'Evalúa tus logros',
                'Comparte con seres queridos',
                'Siente las energías místicas'
            ],
            'waning': [
                'Tiempo de soltar y limpiar',
                'Libera viejos hábitos',
                'Limpia energías negativas',
                'Encuentra tu paz interior'
            ],
            'last_quarter': [
                'Tiempo de evaluar y aprender',
                'Analiza el pasado',
                'Aprende tus lecciones',
                'Prepárate para el futuro'
            ]
        }
    elif lang == 'fr':
        advice_map = {
            'new': [
                'Temps parfait pour de nouveaux commencements',
                'Définissez vos intentions',
                'Démarrez de nouveaux projets',
                'Explorez votre monde intérieur'
            ],
            'waxing': [
                'Temps de croissance et de développement',
                'Augmentez votre énergie',
                'Saisissez de nouvelles opportunités',
                'Avancez avec des pensées positives'
            ],
            'first_quarter': [
                'Temps de prendre des décisions',
                'Concentrez-vous sur vos objectifs',
                'Faites des plans d\'action',
                'Prenez des mesures fortes'
            ],
            'full': [
                'Temps d\'achèvement et de célébration',
                'Évaluez vos réalisations',
                'Partagez avec vos proches',
                'Sentez les énergies mystiques'
            ],
            'waning': [
                'Temps de lâcher prise et de nettoyage',
                'Libérez les vieilles habitudes',
                'Nettoyez les énergies négatives',
                'Trouvez votre paix intérieure'
            ],
            'last_quarter': [
                'Temps d\'évaluation et d\'apprentissage',
                'Analysez le passé',
                'Apprenez vos leçons',
                'Préparez-vous pour l\'avenir'
            ]
        }
    else:
        advice_map = {
            'new': ['Yeni başlangıçlar için mükemmel zaman'],
            'waxing': ['Büyüme ve gelişme zamanı'],
            'first_quarter': ['Kararlar alma zamanı'],
            'full': ['Tamamlanma ve kutlama zamanı'],
            'waning': ['Bırakma ve temizlenme zamanı'],
            'last_quarter': ['Değerlendirme ve öğrenme zamanı']
        }
    
    return advice_map.get(energy, ['Ay enerjisi ile uyum halinde olun' if lang == 'tr' else 'Be in harmony with moon energy'])

# --- Language and Text Functions (Supabase supported) ---
@lru_cache(maxsize=32)
def get_config_from_db(key):
    return supabase_manager.get_config(key)

def get_locales():
    """
    Load language texts from JSON files in 'locales' folder.
    Example: tr.json, en.json, es.json, fr.json
    """
    locales_dir = "locales"
    all_locales = {}
    
    # List of supported languages (based on file names)
    supported_langs = ['tr', 'en', 'es', 'fr']  # Only 4 languages as requested

    for lang_code in supported_langs:
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_locales[lang_code] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load localization file: {file_path} - Error: {e}")
            
    return all_locales

locales = get_locales()

def get_text(lang: str, key: str, **kwargs) -> str:
    """Get text from language file and replace parameters."""
    # First try the requested language
    if lang in locales:
        text = locales[lang].get(key, key)
    # If requested language not available, try Turkish
    elif "tr" in locales:
        text = locales["tr"].get(key, key)
    # If Turkish not available, try English
    elif "en" in locales:
        text = locales["en"].get(key, key)
    # If none available, return the key
    else:
        text = key
    
    return text.format(**kwargs) if kwargs else text

def get_user_lang(user_id: int) -> str:
    user = supabase_manager.get_user(user_id)
    return user.get("language", "tr") if user else "tr"

# Supported languages and code mappings
SUPPORTED_LANGUAGES = {
    'tr': '🇹🇷 Türkçe',
    'en': '🇺🇸 English', 
    'es': '🇪🇸 Español',
    'fr': '🇫🇷 Français'
}

# Zodiac signs
ZODIAC_SIGNS = {
    'tr': ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık'],
    'en': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
    'es': ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis'],
    'fr': ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons']
}

def detect_user_language(telegram_user) -> str:
    """
    Detect user's Telegram client language
    """
    try:
        # Get Telegram user's language_code
        if hasattr(telegram_user, 'language_code') and telegram_user.language_code:
            lang_code = telegram_user.language_code.lower()
            
            # Check two-letter language codes
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
            
            # Clean regional codes (tr-TR, en-US, etc.)
            if '-' in lang_code:
                base_lang = lang_code.split('-')[0]
                if base_lang in SUPPORTED_LANGUAGES:
                    return base_lang
        
        # Default language
        return 'tr'
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return 'tr'

async def get_or_create_user(user_id: int, telegram_user) -> dict:
    """
    Create user or get existing user
    With automatic language detection
    """
    user = supabase_manager.get_user(user_id)
    
    if not user:
        # Automatic language detection
        detected_lang = detect_user_language(telegram_user)
        
        user_data = {
            'id': user_id,  # Primary key
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'language': detected_lang,  # Automatically detected language
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
        
        # Log language detection
        supabase_manager.add_log(f"New user created: {user_id} - Detected language: {detected_lang}")
    
    return user

# --- Menu and Button Creators ---
def get_main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Generate main menu keyboard based on user language"""
    lang = get_user_lang(user_id)
    user = supabase_manager.get_user(user_id)
    premium_plan = user.get('premium_plan', 'free') if user else 'free'
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, "coffee_fortune"), callback_data="select_coffee")],
        [InlineKeyboardButton(get_text(lang, "tarot_fortune"), callback_data="select_tarot")],
        [InlineKeyboardButton(get_text(lang, "dream_analysis"), callback_data="select_dream")],
        [InlineKeyboardButton(get_text(lang, "astrology"), callback_data="select_astrology")],
        [
            InlineKeyboardButton(get_text(lang, "daily_card"), callback_data="toggle_daily"),
            InlineKeyboardButton(get_text(lang, "referral"), callback_data="get_referral_link")
        ]
    ]
    
    # Premium button
    if premium_plan == 'free':
        keyboard.append([InlineKeyboardButton(get_text(lang, "premium_upgrade"), 
                                            callback_data="premium_menu")])
    else:
        plan_name = PREMIUM_PLANS.get(premium_plan, {}).get('name', 'Premium')
        keyboard.append([InlineKeyboardButton(f"💎 {plan_name}", callback_data="premium_menu")])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, "language"), callback_data="change_language")])
    
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_button(lang: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ " + get_text(lang, "main_menu_button"), callback_data="main_menu")]
    ])

def get_navigation_keyboard(lang: str, include_back=True, include_forward=False):
    """Create navigation keyboard."""
    buttons = []
    if include_back:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
    if include_forward:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data="next_page"))
    
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def show_main_menu(update: Update, context: CallbackContext, message: str = None):
    """Show main menu."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    lang = get_user_lang(update.effective_user.id)
    
    menu_text = message or get_text(lang, "start_message")
    keyboard = get_main_menu_keyboard(update.effective_user.id)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(menu_text, reply_markup=keyboard, parse_mode='Markdown')

# --- Main Commands ---
async def start(update: Update, context: CallbackContext):
    """Handle bot start command."""
    user = await get_or_create_user(update.effective_user.id, update.effective_user)
    user_id_str = str(update.effective_user.id)
    
    # Automatic language detection
    detected_lang = detect_user_language(update.effective_user)
    current_lang = get_user_lang(update.effective_user.id)
    
    # Update user language if different
    if detected_lang != current_lang:
        supabase_manager.update_user(update.effective_user.id, {'language': detected_lang})
        supabase_manager.add_log(f"User language updated: {user_id_str} - {current_lang} → {detected_lang}")
        current_lang = detected_lang
    
    # Referral link check
    if context.args:
        referrer_id = context.args[0]
        supabase_manager.add_log(f"User came via referral link: {user_id_str} - Referrer: {referrer_id}")
        
        try:
            referrer_user_id = int(referrer_id)
            if referrer_user_id != update.effective_user.id:  # Can't refer yourself
                referrer = supabase_manager.get_user(referrer_user_id)
                if referrer:
                    # Increase referrer's earnings
                    new_count = referrer.get('referred_count', 0) + 1
                    new_earnings = referrer.get('referral_earnings', 0) + 1
                    bonus_readings = referrer.get('bonus_readings', 0) + 1
                    supabase_manager.update_user(referrer_user_id, {
                        'referred_count': new_count,
                        'referral_earnings': new_earnings,
                        'bonus_readings': bonus_readings
                    })
                    
                    supabase_manager.add_log(f"Referral processed: {referrer_id} -> {user_id_str}")
        except ValueError:
            supabase_manager.add_log(f"Invalid referral ID: {referrer_id}")
    
    # Welcome message (in detected language)
    welcome_message = get_text(current_lang, "start_message")
    
    # Add language detection notification (only for new users)
    if user.get('readings_count', 0) == 0:
        lang_name = SUPPORTED_LANGUAGES.get(current_lang, 'Turkish')
        lang_detect_msg = get_text(current_lang, "language_detected").format(lang=lang_name)
        welcome_message = f"{lang_detect_msg}\n\n{welcome_message}"
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard(update.effective_user.id),
        parse_mode='Markdown'
    )
    
    supabase_manager.add_log(f"Start command processed: {user_id_str} - Language: {current_lang}")

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
        
        # Admin check - admin has unlimited access
        if user_id == ADMIN_ID:
            supabase_manager.update_user(user_id, {'state': 'waiting_for_dream'})
            try:
                await query.edit_message_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
            except Exception as e:
                await query.message.reply_text(get_text(lang, "dream_analysis_prompt"), reply_markup=get_main_menu_keyboard(query.from_user.id))
            return
        
        # Free reading limit check
        readings_count = user.get("readings_count", 0)
        if readings_count >= FREE_READING_LIMIT:
            # Redirect to premium plans
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium Plans", callback_data="premium_menu")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
            await query.edit_message_text(
                f"🎯 **Free reading limit reached!**\n\n✨ **Upgrade to Premium Plans for unlimited readings:**\n\n" +
                f"• **Basic Plan (500 ⭐):** Unlimited readings + advanced features\n" +
                f"• **Premium Plan (1000 ⭐):** Complete astrology package\n" +
                f"• **VIP Plan (2000 ⭐):** Ultimate experience\n\n" +
                f"🌟 **Premium benefits:**\n" +
                f"♾️ Unlimited readings (Coffee, Tarot, Dream)\n" +
                f"🔮 Advanced astrology features\n" +
                f"📊 Detailed reports and analysis", 
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
    """Draw tarot card and create interpretation."""
    query = update.callback_query
    await query.answer()
    
    user = await get_or_create_user(query.from_user.id, query.from_user)
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
    
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
        await query.edit_message_text(get_text(lang, "tarot_drawing"))
        
        try:
            tarot_cards = supabase_manager.get_tarot_cards()
            card = random.choice(tarot_cards) if tarot_cards else "The Fool"
            
            # Simple model selection
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-pro')
            
            # Simple prompt
            simple_prompt = f"You are a tarot reader. Write a short interpretation for {user.get('first_name', 'Friend')} who drew the {card} card. 100 words, in {lang}."
            
            # Try Gemini API first, then fallback to DeepSeek
            try:
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, model.generate_content, simple_prompt),
                    timeout=10.0  # 10 second timeout
                )
                
                supabase_manager.add_log(f"✅ Tarot Gemini API call completed ({lang})")
            except Exception as gemini_error:
                supabase_manager.add_log(f"❌ Gemini API error, switching to DeepSeek: {str(gemini_error)[:100]}")
                
                # Fallback to DeepSeek API
                try:
                    deepseek_response = await asyncio.wait_for(
                        loop.run_in_executor(None, call_deepseek_api, simple_prompt),
                        timeout=15.0  # 15 second timeout for DeepSeek
                    )
                    
                    # Create a response object similar to Gemini
                    response = type('Response', (), {'text': deepseek_response})()
                    supabase_manager.add_log(f"✅ Tarot DeepSeek API call completed ({lang})")
                except Exception as deepseek_error:
                    supabase_manager.add_log(f"❌ DeepSeek API error: {str(deepseek_error)[:100]}")
                    # Fallback response
                    response = type('Response', (), {'text': f"""🔮 **{card} Card Interpretation**

**Card Meaning:** The {card} card heralds new beginnings and opportunities.

**Personal Message:** {user.get('first_name', 'Friend')}, important changes are approaching in your life.

**Advice:** Gather your courage and seize new opportunities."""})()
            
            supabase_manager.add_log(f"Admin tarot reading generated. User: {user_id_str}. Card: {card}")
            await query.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(query.from_user.id))
        except Exception as e:
            logger.error(f"Admin tarot reading error: {e}")
            await query.edit_message_text(
                get_text(lang, "fortune_error"), 
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
            f"{get_text(lang, 'fortune_limit_reached')}\n\n💫 **Continue with Telegram Stars:**", 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    await query.edit_message_text(get_text(lang, "tarot_drawing"))
    
    try:
        tarot_cards = supabase_manager.get_tarot_cards()
        card = random.choice(tarot_cards) if tarot_cards else "The Fool"
        
        # Simple and reliable model selection
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Simple and fast prompt
        simple_prompt = f"You are a tarot reader. Write a short interpretation for {user.get('first_name', 'Friend')} who drew the {card} card. 100 words, in {lang}."
        
        # Try Gemini API first, then fallback to DeepSeek
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, model.generate_content, simple_prompt),
                timeout=10.0  # 10 second timeout
            )
            
            supabase_manager.add_log(f"✅ Tarot Gemini API call completed ({lang})")
        except Exception as gemini_error:
            supabase_manager.add_log(f"❌ Gemini API error, switching to DeepSeek: {str(gemini_error)[:100]}")
            
            # Fallback to DeepSeek API
            try:
                deepseek_response = await asyncio.wait_for(
                    loop.run_in_executor(None, call_deepseek_api, simple_prompt),
                    timeout=15.0  # 15 second timeout for DeepSeek
                )
                
                # Create a response object similar to Gemini
                response = type('Response', (), {'text': deepseek_response})()
                supabase_manager.add_log(f"✅ Tarot DeepSeek API call completed ({lang})")
            except Exception as deepseek_error:
                supabase_manager.add_log(f"❌ DeepSeek API error: {str(deepseek_error)[:100]}")
                # Fallback response
                response = type('Response', (), {'text': f"""🔮 **{card} Card Interpretation**

**Card Meaning:** The {card} card heralds new beginnings and opportunities.

**Personal Message:** {user.get('first_name', 'Friend')}, important changes are approaching in your life.

**Advice:** Gather your courage and seize new opportunities."""})()
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini API")
        
        supabase_manager.add_log(f"Gemini tarot response received ({lang}): {len(response.text)} characters")
        
        # Update reading count
        supabase_manager.update_user(query.from_user.id, {
            "readings_count": supabase_manager.get_user(query.from_user.id)["readings_count"] + 1
        })
        
        supabase_manager.add_log(f"Tarot reading generated. User: {user_id_str}. Card: {card}")
        await query.message.reply_text(response.text, reply_markup=get_main_menu_keyboard(query.from_user.id))
    except Exception as e:
        logger.error(f"Tarot reading error: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"), 
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def handle_dream_text(update: Update, context: CallbackContext):
    """Handle dream text, birth chart information, and chatbot questions."""
    user_id_str = str(update.effective_user.id)
    user = supabase_manager.get_user(update.effective_user.id)
    
    supabase_manager.add_log(f"handle_dream_text called: {user_id_str}")
    supabase_manager.add_log(f"User state: {user.get('state') if user else 'no_user'}")
    
    # Check user state
    if user and user.get('state') == 'waiting_for_dream':
        # Dream interpretation process
        lang = get_user_lang(update.effective_user.id)
        dream_text = update.message.text
        
        supabase_manager.add_log(f"Dream text received: {user_id_str}. Text: {dream_text[:50]}...")
        
        await update.message.reply_text(get_text(lang, "dream_analyzing"))
        
        try:
            # Simple and reliable model selection
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-pro')
            
            # Get prompt from Supabase
            prompt = supabase_manager.get_prompt("dream", lang)
            if not prompt:
                prompt = f"You are an experienced dream interpreter. Create a dream interpretation for {update.effective_user.first_name}.\n\nDescribe what they saw in their dream first. For example: 'In your dream, you saw a butterfly...'\n\nThen explain the meaning of these symbols and make a personal interpretation for {update.effective_user.first_name}.\n\n150-200 words."
            
            # Prepare prompt
            final_prompt = prompt.replace("{username}", update.effective_user.first_name).replace("{dream_text}", dream_text)
            
            # Add language instruction
            if lang == 'tr':
                final_prompt = f"YOU ARE A DREAM INTERPRETER. WRITE ONLY DREAM INTERPRETATION IN TURKISH.\n\n{final_prompt}\n\nTURKISH INTERPRETATION:"
            elif lang == 'en':
                final_prompt = f"YOU ARE A DREAM INTERPRETER. WRITE ONLY DREAM INTERPRETATION IN ENGLISH.\n\n{final_prompt}\n\nENGLISH INTERPRETATION:"
            elif lang == 'es':
                final_prompt = f"ERES UN INTÉRPRETE DE SUEÑOS. ESCRIBE SOLO LA INTERPRETACIÓN DEL SUEÑO EN ESPAÑOL.\n\n{final_prompt}\n\nINTERPRETACIÓN EN ESPAÑOL:"
            elif lang == 'fr':
                final_prompt = f"VOUS ÊTES UN INTERPRÈTE DE RÊVES. ÉCRIVEZ SEULEMENT L'INTERPRÉTATION DU RÊVE EN FRANÇAIS.\n\n{final_prompt}\n\nINTERPRÉTATION EN FRANÇAIS:"
            else:
                final_prompt = f"YOU ARE A DREAM INTERPRETER. WRITE ONLY DREAM INTERPRETATION.\n\n{final_prompt}\n\nINTERPRETATION:"
            
            supabase_manager.add_log(f"Dream prompt prepared ({lang}): {len(final_prompt)} characters")
            supabase_manager.add_log(f"Gemini API call in progress (dream, {lang}): {user_id_str}")
            
            # Send to Gemini (async API) - with timeout
            try:
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, model.generate_content, final_prompt),
                    timeout=10.0  # 10 second timeout
                )
                
                supabase_manager.add_log(f"Gemini API response successfully received: {user_id_str}")
            except asyncio.TimeoutError:
                supabase_manager.add_log(f"Gemini API timeout (10s): {user_id_str}")
                raise Exception("Gemini API did not respond (10 second timeout)")
            except Exception as e:
                supabase_manager.add_log(f"Gemini API error: {str(e)[:100]}")
                raise Exception(f"Gemini API error: {str(e)[:100]}")
            
            supabase_manager.add_log(f"Gemini API response received: {response}")
            
            if not response:
                raise Exception("No response received from Gemini API")
            
            if not response.text:
                raise Exception("Empty response received from Gemini API")
            
            supabase_manager.add_log(f"Gemini dream response received: {len(response.text)} characters")
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
                get_text(lang, "fortune_error"), 
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

# Astrology module functions
async def astrology_menu(update: Update, context: CallbackContext):
    """Show astrology main menu"""
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
            InlineKeyboardButton("🌙 Advanced Moon Calendar", callback_data="advanced_moon_calendar")
        ]
    ]
    
    # Premium features
    if premium_plan in ['premium', 'vip']:
        keyboard.append([
            InlineKeyboardButton("📊 Weekly Report", callback_data="weekly_astro_report"),
            InlineKeyboardButton("🌟 Planetary Transits", callback_data="planetary_transits")
        ])
    
    # VIP features
    if premium_plan == 'vip':
        keyboard.append([
            InlineKeyboardButton("🤖 24/7 Astrology Chatbot", callback_data="astro_chatbot"),
            InlineKeyboardButton("👥 Social Features", callback_data="social_astrology")
        ])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, "main_menu_button"), callback_data="main_menu")])
    
    astro_message = f"""⭐ **ASTROLOGY CENTER** ⭐
━━━━━━━━━━━━━━━━━━━━━━

🌟 **Birth Chart** - Personal astrological analysis
📅 **Daily Horoscope** - Daily guidance for your sign
💕 **Compatibility** - Energy analysis between two signs
🌙 **Advanced Moon Calendar** - Real moon phases and effects

{'📊 **Premium Features Active!**' if premium_plan in ['premium', 'vip'] else ''}
{'🤖 **VIP Features Active!**' if premium_plan == 'vip' else ''}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Discover what the stars tell you* ✨"""
    
    try:
        await query.edit_message_text(astro_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception as e:
        # If message cannot be edited, send new message
        await query.message.reply_text(astro_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def astro_daily_horoscope(update: Update, context: CallbackContext):
    """Show zodiac selection for daily horoscope"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    # Create keyboard with 3 signs per row
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"daily_horoscope_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astrology", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    await query.edit_message_text(
        get_text(lang, "enter_your_sign"),
        reply_markup=keyboard
    )

async def generate_daily_horoscope(update: Update, context: CallbackContext):
    """Generate daily horoscope for selected zodiac sign"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user_id = query.from_user.id
    user_id_str = str(user_id)
    
    # Check rate limit
    if not gemini_rate_limiter.can_make_request(user_id):
        wait_time = gemini_rate_limiter.get_wait_time(user_id)
        await query.edit_message_text(
            f"⚠️ API rate limit exceeded. Please wait {int(wait_time)} seconds before trying again.",
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )
        return
    
    user = await get_or_create_user(query.from_user.id, query.from_user)
    
    # Get sign index from callback data
    sign_index = int(query.data.split('_')[-1])
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    selected_sign = signs[sign_index]
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Simple model selection
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Prepare prompt
        prompt = supabase_manager.get_prompt("daily_horoscope", lang)
        if not prompt:
            prompt = f"You are an experienced astrologer. Create a detailed astrological interpretation for {selected_sign} sign for today.\n\nInclude:\n1. General Energy\n2. Love and Relationships\n3. Career and Finance\n4. Health and Energy\n5. Daily Advice\n\n120-150 words, positive and motivating."
        
        prompt = prompt.replace("{sign}", selected_sign)
        
        # Language-specific final prompt
        final_prompt = f"YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.\n\n{prompt}\n\n{lang.upper()} INTERPRETATION:"
        
        # Gemini API call
        supabase_manager.add_log(f"Prompt length sent to Gemini: {len(final_prompt)} characters")
        supabase_manager.add_log(f"🔄 Gemini API call starting...")
        
        # Async API call - with timeout
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, model.generate_content, final_prompt),
                timeout=15.0  # 15 second timeout
            )
            
            supabase_manager.add_log(f"✅ Gemini API call completed")
        except asyncio.TimeoutError:
            supabase_manager.add_log(f"❌ Gemini API timeout (15s): {user_id_str}")
            raise Exception("Gemini API did not respond (15 second timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Gemini API error: {str(e)[:100]}")
            raise Exception(f"Gemini API error: {str(e)[:100]}")
        
        supabase_manager.add_log(f"Gemini response received: {response is not None}")
        if response:
            supabase_manager.add_log(f"Response text exists: {hasattr(response, 'text') and response.text is not None}")
        
        if not response or not response.text:
            raise Exception("Empty response received from Gemini API")
        
        horoscope_message = f"""📅 **{selected_sign.upper()} - DAILY HOROSCOPE** 📅
━━━━━━━━━━━━━━━━━━━━━━

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
🌟 *Have a great day!* 🌟"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Another Sign", callback_data="astro_daily_horoscope")],
            [InlineKeyboardButton("📱 Horoscope Subscription", callback_data="astro_subscribe_daily")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(horoscope_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Daily horoscope generated: {user_id_str} - {selected_sign}")
        
    except Exception as e:
        logger.error(f"Astrology interpretation error: {e}")
        supabase_manager.add_log(f"Astrology error - {user_id_str}: {str(e)}")
        await query.edit_message_text(
            f"❌ Error creating astrology interpretation:\n{str(e)[:100]}...",
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def astro_compatibility(update: Update, context: CallbackContext):
    """Show first zodiac selection for compatibility analysis"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    # Create zodiac selection keyboard
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"compat_first_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astrology", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    await query.edit_message_text(
        get_text(lang, "compatibility_prompt"),
        reply_markup=keyboard
    )

async def astro_first_sign_selected(update: Update, context: CallbackContext):
    """First sign selected, show second sign selection"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    signs = ZODIAC_SIGNS.get(lang, ZODIAC_SIGNS['en'])
    
    first_sign_index = int(query.data.split('_')[-1])
    first_sign = signs[first_sign_index]
    
    # Second sign selection
    keyboard_buttons = []
    for i in range(0, len(signs), 3):
        row = []
        for j in range(i, min(i + 3, len(signs))):
            sign = signs[j]
            row.append(InlineKeyboardButton(f"{sign}", callback_data=f"compat_second_{first_sign_index}_{j}"))
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Astrology", callback_data="select_astrology")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    if lang == 'tr':
        message = f"💕 **{first_sign}** seçtiniz. Şimdi ikinci burcu seçin:"
    else:
        message = f"💕 You selected **{first_sign}**. Now select the second sign:"
    
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def generate_compatibility_analysis(update: Update, context: CallbackContext):
    """Generate compatibility analysis between two zodiac signs"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user_id = query.from_user.id
    user_id_str = str(user_id)
    
    # Check rate limit
    if not gemini_rate_limiter.can_make_request(user_id):
        wait_time = gemini_rate_limiter.get_wait_time(user_id)
        await query.edit_message_text(
            f"⚠️ API rate limit exceeded. Please wait {int(wait_time)} seconds before trying again.",
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )
        return
    
    # Get user state
    user = supabase_manager.get_user(user_id)
    if not user or not user.get("compatibility_signs"):
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )
        return
    
    signs = user["compatibility_signs"].split(",")
    if len(signs) != 2:
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )
        return
    
    first_sign = signs[0]
    second_sign = signs[1]
    
    await query.edit_message_text(get_text(lang, "astrology_calculating"))
    
    try:
        # Gemini model with rate limiting
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Get prompt from Supabase
        prompt = supabase_manager.get_prompt("compatibility", lang)
        if not prompt:
            prompt = f"You are an experienced astrologer. Analyze the compatibility between {first_sign} and {second_sign} signs.\n\nCover these topics:\n1. General Compatibility\n2. Love and Romance\n3. Friendship\n4. Cooperation\n5. Challenges\n6. Advice\n\n180-220 words, balanced and realistic."
        
        # Replace placeholders
        prompt = prompt.replace("{sign1}", first_sign).replace("{sign2}", second_sign)
        
        # Add language instruction
        final_prompt = f"YOU ARE AN ASTROLOGER. WRITE ONLY IN {lang.upper()} LANGUAGE.\n\n{prompt}\n\n{lang.upper()} ANALYSIS:"
        
        # Async API call - with timeout
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, model.generate_content, final_prompt),
                timeout=15.0  # 15 second timeout
            )
            
            supabase_manager.add_log(f"✅ Compatibility Analysis Gemini API call completed: {user_id_str}")
        except asyncio.TimeoutError:
            supabase_manager.add_log(f"❌ Compatibility Analysis Gemini API timeout (15s): {user_id_str}")
            raise Exception("Gemini API did not respond (15 second timeout)")
        except Exception as e:
            supabase_manager.add_log(f"❌ Compatibility Analysis Gemini API error: {str(e)[:100]}")
            raise Exception(f"Gemini API error: {str(e)[:100]}")
        
        if not response or not response.text:
            raise Exception("Empty response received from Gemini API")
        
        compatibility_message = f"""💕 **COMPATIBILITY ANALYSIS** 💕
━━━━━━━━━━━━━━━━━━━━━━

**{first_sign} ↔️ {second_sign}**

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
✨ *Understanding is the most important element in relationships* ✨"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Another Analysis", callback_data="astro_compatibility")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ])
        
        await query.edit_message_text(compatibility_message, reply_markup=keyboard, parse_mode='Markdown')
        supabase_manager.add_log(f"Compatibility analysis completed: {user_id_str} - {first_sign} & {second_sign}")
        
    except Exception as e:
        logger.error(f"Compatibility analysis error: {e}")
        await query.edit_message_text(
            get_text(lang, "fortune_error"),
            reply_markup=get_main_menu_keyboard(query.from_user.id)
        )

async def astro_birth_chart(update: Update, context: CallbackContext):
    """Request birth chart information"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(query.from_user.id)
    user_id = query.from_user.id
    
    # Update user state
    supabase_manager.update_user(user_id, {'state': 'waiting_for_birth_info'})
    
    birth_info_message = f"""🌟 **BIRTH CHART ANALYSIS** 🌟
━━━━━━━━━━━━━━━━━━━━━━

To create your birth chart, I need the following information:

📅 **Format:** DD.MM.YYYY HH:MM - City
📍 **Example:** 15.06.1990 14:30 - Istanbul

🔮 **Note:** The more accurate the birth time, the more accurate the analysis.

━━━━━━━━━━━━━━━━━━━━━━
✨ *Please write your birth information in the format above* ✨"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Astrology", callback_data="select_astrology")]
    ])
    
    await query.edit_message_text(birth_info_message, reply_markup=keyboard, parse_mode='Markdown')

async def process_birth_chart(update: Update, context: CallbackContext):
    """Process birth chart analysis"""
    user_id = update.effective_user.id
    user_id_str = str(user_id)
    lang = get_user_lang(user_id)
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
    
    lang = get_user_lang(user_id)
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

async def toggle_daily_subscription(update: Update, context: CallbackContext):
    """Toggle daily subscription"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    user = supabase_manager.get_user(query.from_user.id)
    current_status = user.get("daily_subscribed", False)
    lang = get_user_lang(query.from_user.id)
    
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

# --- Essential Functions ---
async def confirm_daily_subscribe(update: Update, context: CallbackContext):
    """Confirm daily subscription"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    supabase_manager.update_user(query.from_user.id, {"daily_subscribed": True})
    lang = get_user_lang(query.from_user.id)
    
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
    lang = get_user_lang(query.from_user.id)
    
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

async def change_language_menu(update: Update, context: CallbackContext):
    """Show language selection menu"""
    query = update.callback_query
    await query.answer()
    
    # Language options
    keyboard = []
    
    # First row: Main languages
    keyboard.append([
        InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr"),
        InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇪🇸 Español", callback_data="set_lang_es")
    ])
    
    # Second row: Additional languages
    keyboard.append([
        InlineKeyboardButton("🇫🇷 Français", callback_data="set_lang_fr")
    ])
    
    # Back button
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 **Language Selection / Selección de Idioma**\n\nPlease select your preferred language:\nPor favor seleccione su idioma preferido:", 
        reply_markup=keyboard_markup, 
        parse_mode='Markdown'
    )

async def set_language(update: Update, context: CallbackContext):
    """Update user's language preference"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[-1]
    user_id = query.from_user.id
    user_id_str = str(user_id)
    
    # Check if language code is valid
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = 'tr'
    
    # Update user's language
    supabase_manager.update_user(user_id, {'language': lang_code})
    supabase_manager.add_log(f"User {user_id_str} changed language to {lang_code}.")
    
    # Language change message
    lang_name = SUPPORTED_LANGUAGES[lang_code]
    
    # Show main menu in new language
    welcome_message = get_text(lang_code, "start_message")
    
    # Add language change notification
    if lang_code == 'tr':
        change_message = f"✅ Diliniz **{lang_name}** olarak güncellendi!"
    elif lang_code == 'en':
        change_message = f"✅ Your language updated to **{lang_name}**!"
    elif lang_code == 'es':
        change_message = f"✅ Tu idioma se actualizó a **{lang_name}**!"
    elif lang_code == 'fr':
        change_message = f"✅ Votre langue mise à jour vers **{lang_name}**!"
    else:
        change_message = f"✅ Language updated to **{lang_name}**!"
    
    full_message = f"{change_message}\n\n{welcome_message}"
    
    await show_main_menu(update, context, message=full_message)

async def get_referral_link_callback(update: Update, context: CallbackContext):
    """Create and show referral link"""
    query = update.callback_query
    await query.answer()
    
    user_id_str = str(query.from_user.id)
    lang = get_user_lang(query.from_user.id)
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

# --- Scheduled Tasks ---
async def send_daily_card(application: Application):
    """Send daily tarot card to subscribers"""
    logger.info("Daily card sending task running.")
    
    subscribed_users = supabase_manager.get_subscribed_users()
    tarot_cards = supabase_manager.get_tarot_cards()
    
    for user_id in subscribed_users:
        try:
            lang = get_user_lang(user_id)
            username = supabase_manager.get_user(user_id).get("first_name", "Friend")
            card = random.choice(tarot_cards) if tarot_cards else "The Fool"
            
            # Simple model selection
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-pro')
            
            prompt = supabase_manager.get_prompt("daily_tarot", lang)
            if not prompt:
                prompt = f"🌅 At the beginning of the day, interpret the energy of the {card} card for {username}.\n\n✨ **Day's Energy:** Explain in detail the main energy that the {card} card offers to {username} today.\n🎯 **Daily Opportunities:** Indicate the special opportunities and luck shown by this card during the day.\n⚠️ **Things to Pay Attention To:** Highlight the points to be careful about today and potential difficulties.\n💪 **Daily Motivation:** Give {username} a strong and motivating message to start the day positively.\n🔮 **Day's Advice:** Practical advice to use this card's energy in the best way.\n\n**Language Tone:** Energetic, hopeful and motivating.\n**Limitations:** 80-100 words."
            
            prompt = prompt.replace("{card}", card).replace("{username}", username)
            
            supabase_manager.add_log(f"Daily card prompt prepared ({lang}): {len(prompt)} characters")
            supabase_manager.add_log(f"Gemini API call in progress (daily card, {lang}): {user_id}")
            
            # Add language instruction
            if lang != 'tr':
                prompt = f"Please respond in {lang.upper()} language.\n\n{prompt}"
            
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response received from Gemini API")
            
            supabase_manager.add_log(f"Gemini daily card response received: {len(response.text)} characters")
            
            # Create beautiful daily card message
            daily_message = f"""🌟 **FAL GRAM - CARD OF THE DAY** 🌟
━━━━━━━━━━━━━━━━━━━━━━
🃏 **{card}**
━━━━━━━━━━━━━━━━━━━━━━

{response.text}

━━━━━━━━━━━━━━━━━━━━━━
🌅 **Have a great day {username}!**
✨ *Fal Gram with new discoveries every day*"""
            
            await application.bot.send_message(
                chat_id=user_id, 
                text=daily_message, 
                parse_mode='Markdown'
            )
            supabase_manager.add_log(f"Daily card sent: {user_id} (Card: {card})")
        except Exception as e:
            logger.error(f"Daily card sending error ({user_id}): {e}")

async def post_init(application: Application):
    """Start scheduler after application initialization"""
    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    hour, minute = supabase_manager.get_daily_card_time()
    scheduler.add_job(send_daily_card, CronTrigger(hour=hour, minute=minute), args=[application])
    scheduler.start()
    supabase_manager.add_log(f"Scheduler set up: {hour}:{minute}")
    application.bot_data['scheduler'] = scheduler

# --- Main Function ---
def main():
    """Main bot function"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(select_service_callback, pattern="^select_"))
    application.add_handler(CallbackQueryHandler(toggle_daily_subscription, pattern="^toggle_daily$"))
    application.add_handler(CallbackQueryHandler(confirm_daily_subscribe, pattern="^confirm_daily_subscribe$"))
    application.add_handler(CallbackQueryHandler(confirm_daily_unsubscribe, pattern="^confirm_daily_unsubscribe$"))
    application.add_handler(CallbackQueryHandler(get_referral_link_callback, pattern="^get_referral_link$"))
    
    # Astrology handlers
    application.add_handler(CallbackQueryHandler(astrology_menu, pattern="^select_astrology$"))
    application.add_handler(CallbackQueryHandler(astro_daily_horoscope, pattern="^astro_daily_horoscope$"))
    application.add_handler(CallbackQueryHandler(generate_daily_horoscope, pattern="^daily_horoscope_"))
    application.add_handler(CallbackQueryHandler(astro_compatibility, pattern="^astro_compatibility$"))
    application.add_handler(CallbackQueryHandler(astro_birth_chart, pattern="^astro_birth_chart$"))
    application.add_handler(CallbackQueryHandler(astro_first_sign_selected, pattern="^compat_first_"))
    application.add_handler(CallbackQueryHandler(generate_compatibility_analysis, pattern="^compat_second_"))
    
    # Language handlers
    application.add_handler(CallbackQueryHandler(change_language_menu, pattern="^change_language$"))
    application.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream_text))
    
    supabase_manager.add_log("Bot starting...")
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()

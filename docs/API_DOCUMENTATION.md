# 📘 API Documentation - Fal Gram v3.1.1

Bu doküman Fal Gram botunun **v3.1.1 Gelişmiş Admin Panel & Dil Desteği** sürümü için kapsamlı API referansını içerir.

---

## 📋 **İçindekiler**

1. [Genel Bakış](#genel-bakış)
2. [Telegram Bot API](#telegram-bot-api)
3. [Google Gemini AI API](#google-gemini-ai-api)
4. [Supabase Database API](#supabase-database-api)
5. [Premium Payment API](#premium-payment-api)
6. [Internal Bot Functions](#internal-bot-functions)
7. [Webhook & Callbacks](#webhook--callbacks)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Security](#security)

---

## 🌟 **Genel Bakış**

Fal Gram v3.1.0, aşağıdaki API'leri entegre eder:

- **Telegram Bot API** - Mesajlaşma ve ödeme sistemi
- **Google Gemini AI** - Yapay zeka model entegrasyonu (Sync API)
- **Supabase PostgreSQL** - Veritabanı, backend servisleri ve dinamik prompt yönetimi
- **Telegram Stars** - Premium abonelik ödeme sistemi
- **Moon Phase Calculator** - Ay fazları hesaplama algoritması
- **Dynamic Prompt System** - Supabase tabanlı AI prompt yönetimi

---

## 🤖 **Telegram Bot API**

### **Temel Bot Konfigürasyonu**

```python
# Bot initialization
application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

# Webhook configuration (production)
application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TELEGRAM_BOT_TOKEN,
    webhook_url=f"https://yourdomain.com/{TELEGRAM_BOT_TOKEN}"
)
```

### **Command Handlers**

#### **Kullanıcı Komutları**
```python
# Başlangıç komutu
/start [referral_id] - Bot başlatma ve referral sistemi

# Admin komutu (ADMIN_ID gerekli)
/admin - Admin paneline erişim

# Admin komutları (ADMIN_ID gerekli)
/gift <user_id> <plan> <days> - Premium abonelik hediye etme
/cancel <user_id> - Premium abonelik iptal etme
```

#### **Callback Query Patterns**
```python
# Ana navigasyon
"^main_menu$" - Ana menüye dönüş
"^select_(coffee|tarot|dream|astrology)$" - Servis seçimi

# Astroloji sistemi
"^astro_(daily_horoscope|compatibility|birth_chart|moon_calendar)$"
"^daily_horoscope_\d+$" - Burç seçimi (0-11 index)
"^compat_(first|second)_\d+(_\d+)?$" - Uyumluluk analizi
"^weekly_horoscope_\d+$" - Haftalık burç seçimi (0-11 index)
"^monthly_horoscope_\d+$" - Aylık burç seçimi (0-11 index)
"^weekly_astro_report$" - Haftalık burç menüsü
"^monthly_horoscope_menu$" - Aylık burç menüsü

# Premium sistem
"^premium_(menu|plan_\w+|compare|buy_\w+)$"
"^astro_chatbot$" - 7/24 chatbot (VIP)

# Admin panel sistemi
"^admin_(stats|view_logs|settings|users|download_pdf|download_users_pdf)$"
"^back_to_admin$" - Admin paneline dönüş

# Premium yönetimi (Admin)
"^admin_premium$" - Premium yönetim menüsü
"^admin_premium_users$" - Premium kullanıcı listesi
"^admin_premium_stats$" - Premium istatistikleri
"^admin_gift_subscription$" - Hediye abonelik menüsü
"^admin_cancel_subscription$" - Abonelik iptal menüsü
"^admin_premium_pdf$" - Premium PDF raporu

# Dil sistemi
"^change_language$" - Dil seçim menüsü
"^set_lang_[a-z]{2}$" - Dil değiştirme (ISO 639-1)
```

### **Message Handlers**

#### **Text Handler States**
```python
# Kullanıcı state'leri
"waiting_for_dream" - Rüya tabiri bekleme
"waiting_for_birth_info" - Doğum haritası bilgi bekleme
"chatbot_mode" - VIP chatbot aktif
"idle" - Varsayılan durum
```

#### **Photo Handler**
```python
# Kahve falı için fotoğraf işleme
filters.PHOTO - Kahve fincanı görsel analizi
```

### **Payment Integration**

#### **Telegram Stars Implementation**
```python
# Premium plan satın alma
async def premium_buy_plan(update, context):
    plan = PREMIUM_PLANS[plan_id]
    prices = [LabeledPrice("Premium Plan", plan['price_stars'])]
    
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=f"{plan['name']} Aboneliği",
        description=plan['description'],
        payload=f"premium_{plan_id}_{user_id}",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="XTR",  # Telegram Stars
        prices=prices
    )

# Ödeme doğrulama
async def precheckout_callback(update, context):
    query = update.pre_checkout_query
    await query.answer(ok=True)

# Başarılı ödeme işleme
async def successful_payment_callback(update, context):
    payment = update.message.successful_payment
    # Premium plan aktivasyonu
    activate_premium_plan(user_id, plan_type, payment.total_amount)
```

---

## 🧠 **Google Gemini AI API**

### **Model Configuration**

#### **Model Selection & Fallback**
```python
# Gemini 2.0 Flash Experimental (primary)
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logging.info("Gemini 2.0 Flash Exp model kullanılıyor")
except Exception:
    # Fallback to Gemini 1.5 Flash
    model = genai.GenerativeModel('gemini-1.5-flash')
    logging.info("Gemini 1.5 Flash model kullanılıyor")
```

#### **API Configuration**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]
```

### **Content Generation Endpoints**

#### **Kahve Falı - Vision Analysis**
```python
async def process_coffee_fortune(image_data, lang, user_name):
    prompt = get_localized_prompt("coffee", lang)
    
    # Dil-spesifik final prompt
    if lang == 'tr':
        final_prompt = f"""SEN BİR KAHVE FALCISISIN. SADECE TÜRKÇE FAL YORUMUNU YAZ.
        
        {prompt}
        
        TÜRKÇE YORUM:"""
    
    response = await model.generate_content_async([
        image_data,
        final_prompt
    ])
    
    return response.text
```

#### **Astroloji Chatbot - Conversational AI**
```python
async def handle_chatbot_question(question, lang, user_context):
    prompt = f"""Sen deneyimli bir astroloji chatbot'usun.
    
    Kullanıcı Sorusu: {question}
    Kullanıcı Dili: {lang}
    Bağlam: {user_context}
    
    120-180 kelime arası, samimi ve profesyonel yanıt ver."""
    
    response = await model.generate_content_async(prompt)
    return response.text
```

#### **Doğum Haritası - Comprehensive Analysis**
```python
async def generate_birth_chart(birth_info, lang):
    prompt = f"""Sen profesyonel bir astrologsun.
    
    Doğum Bilgisi: {birth_info}
    
    Kapsamlı analiz:
    1. Güneş Burcu Analizi
    2. Yükselen Burç
    3. Ay Burcu
    4. Gezegen pozisyonları
    5. Genel kişilik değerlendirmesi
    
    200-250 kelime, kişiselleştirilmiş analiz."""
    
    response = await model.generate_content_async(prompt)
    return response.text
```

### **Multi-Language Prompt System**

#### **Localized Prompts**
```python
PROMPT_TEMPLATES = {
    'coffee': {
        'tr': "Sen profesyonel bir kahve falcısısın...",
        'en': "You are a professional coffee fortune teller...",
        'es': "Eres un lector profesional de café...",
        # ... diğer diller
    },
    'daily_horoscope': {
        'tr': "Sen deneyimli bir astrologsun. {sign} burcu için...",
        'en': "You are an experienced astrologer. For {sign} sign...",
        # ... diğer diller
    }
}

def get_localized_prompt(prompt_type, lang, **kwargs):
    template = PROMPT_TEMPLATES[prompt_type].get(lang, PROMPT_TEMPLATES[prompt_type]['en'])
    return template.format(**kwargs)
```

---

## 🗄️ **Supabase Database API**

### **Database Schema v3.0.0**

#### **Users Table - Enhanced**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    language TEXT DEFAULT 'tr',
    readings_count INTEGER DEFAULT 0,
    daily_subscribed BOOLEAN DEFAULT FALSE,
    referred_count INTEGER DEFAULT 0,
    referral_earnings INTEGER DEFAULT 0,
    bonus_readings INTEGER DEFAULT 0,
    state TEXT DEFAULT 'idle',
    premium_plan TEXT DEFAULT 'free', -- NEW: free, basic, premium, vip
    premium_expires_at TIMESTAMP, -- NEW
    astro_subscribed BOOLEAN DEFAULT FALSE, -- NEW
    moon_notifications BOOLEAN DEFAULT FALSE, -- NEW
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **Premium Subscriptions Table - NEW**
```sql
CREATE TABLE premium_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    plan_type TEXT NOT NULL, -- basic, premium, vip
    stars_paid INTEGER NOT NULL,
    starts_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **Chatbot History Table - NEW**
```sql
CREATE TABLE chatbot_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **Weekly Reports Table - NEW**
```sql
CREATE TABLE weekly_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    week_start DATE NOT NULL,
    report_content TEXT NOT NULL,
    report_type TEXT DEFAULT 'astrology',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, week_start, report_type)
);
```

### **Database Operations**

#### **SupabaseManager Class**
```python
class SupabaseManager:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # User management
    def get_user(self, user_id: int) -> dict:
        response = self.supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    
    def update_user_premium(self, user_id: int, plan: str, expires_at: str):
        return self.supabase.table("users").update({
            "premium_plan": plan,
            "premium_expires_at": expires_at
        }).eq("user_id", user_id).execute()
    
    # Premium subscriptions
    def create_premium_subscription(self, subscription_data: dict):
        return self.supabase.table("premium_subscriptions").insert(subscription_data).execute()
    
    def get_active_subscriptions(self, user_id: int):
        return self.supabase.table("premium_subscriptions").select("*").eq("user_id", user_id).eq("active", True).execute()
    
    # Chatbot history
    def save_chatbot_interaction(self, user_id: int, question: str, response: str):
        return self.supabase.table("chatbot_history").insert({
            "user_id": user_id,
            "question": question,
            "response": response
        }).execute()
    
    # Weekly reports
    def create_weekly_report(self, user_id: int, week_start: str, content: str):
        return self.supabase.table("weekly_reports").insert({
            "user_id": user_id,
            "week_start": week_start,
            "report_content": content
        }).execute()
```

#### **Advanced Queries**
```python
# Premium kullanıcıları getir
def get_premium_users():
    return supabase.table("users").select("*").neq("premium_plan", "free").execute()

# VIP kullanıcıları için chatbot geçmişi
def get_vip_chatbot_history(user_id: int, limit: int = 10):
    return supabase.table("chatbot_history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()

# Haftalık rapor kontrolü
def check_weekly_report_exists(user_id: int, week_start: str):
    response = supabase.table("weekly_reports").select("id").eq("user_id", user_id).eq("week_start", week_start).execute()
    return len(response.data) > 0
```

---

## 💎 **Premium Payment API**

### **Telegram Stars Integration**

#### **Plan Configuration**
```python
PREMIUM_PLANS = {
    'basic': {
        'name': 'Temel Plan',
        'price_stars': 500,
        'price_monthly': '$2.99',
        'duration_days': 30,
        'features': ['unlimited_readings', 'no_ads', 'daily_horoscope']
    },
    'premium': {
        'name': 'Premium Plan',
        'price_stars': 1000,
        'price_monthly': '$4.99',
        'duration_days': 30,
        'features': ['basic_features', 'weekly_reports', 'pdf_download', 'moon_notifications']
    },
    'vip': {
        'name': 'VIP Plan',
        'price_stars': 2000,
        'price_monthly': '$9.99',
        'duration_days': 30,
        'features': ['premium_features', 'chatbot_24_7', 'social_features', 'priority_support']
    }
}
```

#### **Payment Flow**
```python
# 1. Invoice oluşturma
async def create_premium_invoice(update, context, plan_id):
    plan = PREMIUM_PLANS[plan_id]
    
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=f"{plan['name']} Aboneliği",
        description=f"Fal Gram {plan['name']} - {plan['duration_days']} gün",
        payload=f"premium_{plan_id}_{update.effective_user.id}",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="XTR",
        prices=[LabeledPrice(plan['name'], plan['price_stars'])]
    )

# 2. Pre-checkout validation
async def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    payload = query.invoice_payload
    
    # Payload validation
    if payload.startswith("premium_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Geçersiz ödeme")

# 3. Successful payment processing
async def successful_payment_callback(update: Update, context: CallbackContext):
    payment = update.message.successful_payment
    payload_parts = payment.invoice_payload.split("_")
    
    plan_id = payload_parts[1]
    user_id = int(payload_parts[2])
    
    # Premium planı aktifleştir
    activate_premium_plan(user_id, plan_id, payment.total_amount)
```

#### **Subscription Management**
```python
def activate_premium_plan(user_id: int, plan_id: str, amount_paid: int):
    """Premium planı aktifleştirir"""
    plan = PREMIUM_PLANS[plan_id]
    expires_at = datetime.now() + timedelta(days=plan['duration_days'])
    
    # Kullanıcı planını güncelle
    supabase_manager.update_user(user_id, {
        'premium_plan': plan_id,
        'premium_expires_at': expires_at.isoformat()
    })
    
    # Abonelik geçmişi kaydet
    supabase_manager.create_premium_subscription({
        'user_id': user_id,
        'plan_type': plan_id,
        'stars_paid': amount_paid,
        'expires_at': expires_at.isoformat()
    })

def check_premium_status(user_id: int) -> str:
    """Kullanıcının premium durumunu kontrol eder"""
    user = supabase_manager.get_user(user_id)
    
    if not user or user.get('premium_plan') == 'free':
        return 'free'
    
    expires_at = user.get('premium_expires_at')
    if expires_at and datetime.fromisoformat(expires_at) > datetime.now():
        return user.get('premium_plan', 'free')
    else:
        # Süre dolmuş, free'ye düşür
        supabase_manager.update_user(user_id, {'premium_plan': 'free'})
        return 'free'
```

---

## 🛠️ **Internal Bot Functions**

### **Core Bot API**

#### **User Management**
```python
async def get_or_create_user(user_id: int, telegram_user) -> dict:
    """Kullanıcıyı oluşturur veya mevcut kullanıcıyı getirir"""
    user = supabase_manager.get_user(user_id)
    
    if not user:
        # Otomatik dil tespiti
        detected_lang = detect_user_language(telegram_user)
        
        user_data = {
            'user_id': user_id,
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'language': detected_lang,
            'premium_plan': 'free'
        }
        supabase_manager.create_user(user_data)
        return user_data
    
    return user

def get_user_lang(user_id: int) -> str:
    """Kullanıcının dil tercihini getirir"""
    user = supabase_manager.get_user(user_id)
    return user.get("language", "tr") if user else "tr"

def check_user_premium_access(user_id: int, required_plan: str) -> bool:
    """Kullanıcının premium erişimini kontrol eder"""
    user_plan = check_premium_status(user_id)
    
    plan_hierarchy = ['free', 'basic', 'premium', 'vip']
    required_level = plan_hierarchy.index(required_plan)
    user_level = plan_hierarchy.index(user_plan)
    
    return user_level >= required_level
```

#### **Language Detection**
```python
SUPPORTED_LANGUAGES = {
    'tr': '🇹🇷 Türkçe', 'en': '🇺🇸 English', 'es': '🇪🇸 Español',
    'fr': '🇫🇷 Français', 'ru': '🇷🇺 Русский', 'de': '🇩🇪 Deutsch',
    'ar': '🇸🇦 العربية', 'it': '🇮🇹 Italiano', 'pt': '🇵🇹 Português'
}

def detect_user_language(telegram_user) -> str:
    """Kullanıcının Telegram client dilini tespit eder"""
    try:
        if hasattr(telegram_user, 'language_code') and telegram_user.language_code:
            lang_code = telegram_user.language_code.lower()
            
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
            
            # Bölgesel kodları (tr-TR, en-US) temizle
            if '-' in lang_code:
                base_lang = lang_code.split('-')[0]
                if base_lang in SUPPORTED_LANGUAGES:
                    return base_lang
        
        return 'tr'  # Varsayılan
    except Exception:
        return 'tr'
```

### **Moon Phase Calculator API**

#### **Astronomical Calculations**
```python
def calculate_moon_phase(date=None):
    """Ay fazını hesaplar (matematiksel algoritma)"""
    if date is None:
        date = datetime.now()
    
    # Bilinen yeni ay: 2000-01-06 18:14 UTC
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    synodic_month = 29.530588853  # gün
    
    days_since = (date - known_new_moon).total_seconds() / 86400
    phase = (days_since % synodic_month) / synodic_month
    
    if phase < 0.0625:
        return {'phase': '🌑', 'name': 'Yeni Ay', 'energy': 'new_beginnings'}
    elif phase < 0.1875:
        return {'phase': '🌒', 'name': 'Hilal', 'energy': 'growth'}
    # ... diğer fazlar
    
def get_moon_energy_advice(energy, lang='tr'):
    """Ay enerjisine göre tavsiyeleri getirir"""
    advice_map = {
        'new_beginnings': {
            'tr': ['Yeni projelere başlamak için ideal', 'Niyetlerinizi belirleyin'],
            'en': ['Ideal for starting new projects', 'Set your intentions']
        },
        # ... diğer enerjiler
    }
    return advice_map.get(energy, {}).get(lang, [])
```

### **Astrology Chatbot Engine**

#### **Conversational AI**
```python
async def handle_chatbot_question(update: Update, context: CallbackContext):
    """VIP kullanıcılar için 7/24 chatbot"""
    user_id = update.effective_user.id
    user = supabase_manager.get_user(user_id)
    
    # VIP kontrolü
    if user.get('premium_plan') != 'vip':
        await send_vip_upgrade_message(update, context)
        return
    
    question = update.message.text
    lang = get_user_lang(user_id)
    
    try:
        # Gemini model
        model = get_gemini_model()
        
        # Chatbot prompt
        prompt = f"""Sen deneyimli bir astroloji chatbot'usun.
        
        Kullanıcı: {update.effective_user.first_name}
        Soru: {question}
        Dil: {lang}
        
        Samimi ve profesyonel yanıt ver (120-180 kelime)."""
        
        response = await model.generate_content_async(prompt)
        
        # Yanıtı kaydet
        supabase_manager.save_chatbot_interaction(user_id, question, response.text)
        
        await update.message.reply_text(f"🤖 **Astroloji Danışmanı**\n\n{response.text}")
        
    except Exception as e:
        logger.error(f"Chatbot hatası: {e}")
        await update.message.reply_text("Üzgünüm, şu anda yanıt veremiyorum.")
```

---

## 🔗 **Webhook & Callbacks**

### **Callback Query Routing**

#### **Pattern-Based Routing**
```python
CALLBACK_PATTERNS = {
    # Main navigation
    r"^main_menu$": main_menu_callback,
    r"^select_(\w+)$": select_service_callback,
    
    # Astrology system
    r"^astro_(\w+)$": astrology_router,
    r"^daily_horoscope_(\d+)$": generate_daily_horoscope,
    r"^compat_first_(\d+)$": astro_first_sign_selected,
    r"^compat_second_(\d+)_(\d+)$": generate_compatibility_analysis,
    
    # Premium system
    r"^premium_(\w+)$": premium_router,
    r"^premium_plan_(\w+)$": premium_plan_details,
    r"^premium_buy_(\w+)$": premium_buy_plan,
    
    # Language system
    r"^set_lang_([a-z]{2})$": set_language,
    
    # Admin system
    r"^admin_(\w+)$": admin_router
}

def register_callback_handlers(application):
    """Callback handler'ları kaydeder"""
    for pattern, handler in CALLBACK_PATTERNS.items():
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))
```

#### **Dynamic Routing**
```python
async def astrology_router(update: Update, context: CallbackContext):
    """Astroloji callback'lerini yönlendirir"""
    query = update.callback_query
    action = query.data.split('_')[1]
    
    routes = {
        'daily': astro_daily_horoscope,
        'compatibility': astro_compatibility,
        'birth': astro_birth_chart,
        'moon': advanced_moon_calendar,
        'chatbot': astro_chatbot
    }
    
    handler = routes.get(action, astrology_menu)
    await handler(update, context)
```

---

## ⚠️ **Error Handling**

### **Comprehensive Error Management**

#### **API Error Handling**
```python
class FalGramError(Exception):
    """Base exception class for Fal Gram"""
    pass

class GeminiAPIError(FalGramError):
    """Gemini API related errors"""
    pass

class PremiumAccessError(FalGramError):
    """Premium access related errors"""
    pass

class DatabaseError(FalGramError):
    """Database operation errors"""
    pass

async def handle_api_error(update, context, error):
    """Genel API hata işleyici"""
    lang = get_user_lang(update.effective_user.id)
    
    error_messages = {
        'tr': "❌ Bir hata oluştu. Lütfen tekrar deneyin.",
        'en': "❌ An error occurred. Please try again.",
        'es': "❌ Ocurrió un error. Por favor, inténtalo de nuevo."
    }
    
    message = error_messages.get(lang, error_messages['tr'])
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_main_menu_keyboard(update.effective_user.id)
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=get_main_menu_keyboard(update.effective_user.id)
        )
    
    # Log error
    logger.error(f"API Error: {error}", exc_info=True)
```

#### **Retry Mechanisms**
```python
from functools import wraps
import asyncio

def retry_on_failure(max_retries=3, delay=1):
    """Hata durumunda yeniden deneme decorator'u"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
async def gemini_api_call(prompt):
    """Retry ile Gemini API çağrısı"""
    model = get_gemini_model()
    response = await model.generate_content_async(prompt)
    
    if not response or not response.text:
        raise GeminiAPIError("Empty response from Gemini API")
    
    return response.text
```

---

## 🚦 **Rate Limiting**

### **API Rate Limiting**

#### **Gemini API Limits**
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.calls = defaultdict(list)
    
    def can_make_call(self, user_id: int) -> bool:
        """Rate limit kontrolü"""
        now = time.time()
        user_calls = self.calls[user_id]
        
        # Son 1 dakikadaki çağrıları filtrele
        recent_calls = [call_time for call_time in user_calls if now - call_time < 60]
        self.calls[user_id] = recent_calls
        
        return len(recent_calls) < self.calls_per_minute
    
    def record_call(self, user_id: int):
        """Çağrıyı kaydet"""
        self.calls[user_id].append(time.time())

# Global rate limiter
gemini_rate_limiter = RateLimiter(calls_per_minute=10)

async def rate_limited_gemini_call(user_id: int, prompt: str):
    """Rate limit ile korunmuş Gemini çağrısı"""
    if not gemini_rate_limiter.can_make_call(user_id):
        raise GeminiAPIError("Rate limit exceeded")
    
    gemini_rate_limiter.record_call(user_id)
    return await gemini_api_call(prompt)
```

#### **Premium User Privileges**
```python
def get_user_rate_limit(user_id: int) -> int:
    """Kullanıcı planına göre rate limit"""
    premium_plan = check_premium_status(user_id)
    
    limits = {
        'free': 3,      # 3 çağrı/dakika
        'basic': 10,    # 10 çağrı/dakika
        'premium': 20,  # 20 çağrı/dakika
        'vip': 50       # 50 çağrı/dakika
    }
    
    return limits.get(premium_plan, 3)
```

---

## 🔒 **Security**

### **Authentication & Authorization**

#### **Admin Access Control**
```python
def require_admin(func):
    """Admin erişimi gerektiren decorator"""
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        
        if str(user_id) != ADMIN_ID:
            await update.message.reply_text("❌ Bu komut için yetkiniz yok.")
            return
        
        return await func(update, context)
    return wrapper

@require_admin
async def admin_command(update: Update, context: CallbackContext):
    """Admin paneli (sadece ADMIN_ID erişebilir)"""
    await admin_panel(update, context)
```

#### **Premium Access Control**
```python
def require_premium(plan_required='basic'):
    """Premium erişimi gerektiren decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            
            if not check_user_premium_access(user_id, plan_required):
                await send_premium_upgrade_message(update, context, plan_required)
                return
            
            return await func(update, context)
        return wrapper
    return decorator

@require_premium('vip')
async def astro_chatbot(update: Update, context: CallbackContext):
    """VIP özelliği - 7/24 chatbot"""
    await handle_chatbot_activation(update, context)
```

### **Data Protection**

#### **User Data Encryption**
```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key=None):
        if key:
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt_text(self, text: str) -> str:
        """Metni şifreler"""
        encrypted = self.cipher.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Metni çözer"""
        encrypted = base64.urlsafe_b64decode(encrypted_text.encode())
        return self.cipher.decrypt(encrypted).decode()

# Sensitive data encryption
encryption = DataEncryption(key=ENCRYPTION_KEY)

def encrypt_sensitive_data(data: dict) -> dict:
    """Hassas verileri şifreler"""
    sensitive_fields = ['birth_info', 'personal_data']
    
    for field in sensitive_fields:
        if field in data:
            data[field] = encryption.encrypt_text(data[field])
    
    return data
```

---

## 📊 **Monitoring & Analytics**

### **Performance Monitoring**

#### **Response Time Tracking**
```python
import time

async def track_performance(func_name: str, func, *args, **kwargs):
    """Fonksiyon performansını takip eder"""
    start_time = time.time()
    
    try:
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        # Performance log
        supabase_manager.add_log(
            f"Performance: {func_name} - {end_time - start_time:.2f}s"
        )
        
        return result
    except Exception as e:
        end_time = time.time()
        
        # Error performance log
        supabase_manager.add_log(
            f"Performance ERROR: {func_name} - {end_time - start_time:.2f}s - {str(e)}"
        )
        
        raise e
```

#### **Usage Analytics**
```python
def track_feature_usage(user_id: int, feature: str, premium_required: bool = False):
    """Özellik kullanımını takip eder"""
    user_plan = check_premium_status(user_id)
    
    analytics_data = {
        'user_id': user_id,
        'feature': feature,
        'user_plan': user_plan,
        'premium_required': premium_required,
        'timestamp': datetime.now().isoformat()
    }
    
    # Analytics veritabanına kaydet
    supabase_manager.add_log(f"Analytics: {analytics_data}")
```

---

## 🔄 **Best Practices**

### **Development Guidelines**

1. **Async/Await Pattern**
   - Tüm I/O operasyonları async olmalı
   - Database ve API çağrıları await ile beklemeli

2. **Error Handling**
   - Her API çağrısı try-catch ile korunmalı
   - Kullanıcı dostu hata mesajları gösterilmeli

3. **Performance**
   - Database sorguları optimize edilmeli
   - Gereksiz API çağrıları önlenmeli

4. **Security**
   - Kullanıcı girdileri validate edilmeli
   - Sensitive data şifrelenmeli

5. **Monitoring**
   - Tüm önemli işlemler loglanmalı
   - Performance metrikleri takip edilmeli

---

## 📱 **Testing**

### **API Testing Examples**

#### **Unit Test Examples**
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_premium_plan_activation():
    """Premium plan aktivasyonu testi"""
    user_id = 12345
    plan_id = 'premium'
    
    with patch('supabase_manager.update_user') as mock_update:
        await activate_premium_plan(user_id, plan_id, 1000)
        
        mock_update.assert_called_once()
        args = mock_update.call_args[0]
        assert args[0] == user_id
        assert args[1]['premium_plan'] == plan_id

@pytest.mark.asyncio
async def test_chatbot_vip_access():
    """VIP chatbot erişim testi"""
    user_id = 12345
    
    with patch('check_premium_status', return_value='vip'):
        with patch('get_gemini_model') as mock_model:
            mock_model.return_value.generate_content_async = AsyncMock(
                return_value=type('Response', (), {'text': 'Test response'})()
            )
            
            # Test chatbot functionality
            result = await handle_chatbot_question(mock_update, mock_context)
            assert result is not None
```

---

*Bu doküman Fal Gram v3.0.0 için kapsamlı API referansıdır. Güncel versiyonlar için GitHub repository'yi takip edin.*

**Son güncellenme: 27 Ocak 2025** 
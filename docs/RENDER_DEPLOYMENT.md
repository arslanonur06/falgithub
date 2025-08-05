# 🚀 FAL GRAM - Render.com Deployment Kılavuzu

**Version: 3.1.1** | Production Deployment & Web Service Setup

---

## 📋 **Genel Bakış**

Bu kılavuz, Fal Gram Telegram Bot'unu **Render.com** platformunda production ortamında deploy etmek için adım adım talimatları içerir. Render.com, Python web servisleri için ücretsiz ve kolay deployment imkanı sunar.

---

## 🎯 **Render.com Avantajları**

### **✅ Ücretsiz Plan**
- **Web Service**: 750 saat/ay ücretsiz
- **Database**: PostgreSQL ücretsiz
- **SSL**: Otomatik HTTPS sertifikası
- **Custom Domain**: Ücretsiz subdomain

### **✅ Kolay Deployment**
- **GitHub Integration**: Otomatik deployment
- **Environment Variables**: Güvenli API key yönetimi
- **Health Checks**: Otomatik sağlık kontrolü
- **Logs**: Gerçek zamanlı log görüntüleme

---

## 🛠️ **Ön Gereksinimler**

### **1. GitHub Repository**
```bash
# Projenizi GitHub'a yükleyin
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin https://github.com/username/fal-gram-bot.git
git push -u origin main
```

### **2. Render.com Hesabı**
- [Render.com](https://render.com) hesabı oluşturun
- GitHub hesabınızı bağlayın

### **3. API Keys Hazırlığı**
```bash
# Gerekli API anahtarları:
TELEGRAM_BOT_TOKEN=your_bot_token
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PAYMENT_PROVIDER_TOKEN=your_payment_token
ADMIN_ID=your_telegram_user_id
```

---

## 📁 **Proje Dosya Yapısı**

### **Gerekli Dosyalar**
```
fal-gram-bot/
├── bot.py                    # Ana bot dosyası
├── requirements.txt          # Python dependencies
├── render.yaml              # Render konfigürasyonu
├── .env.example             # Environment variables örneği
├── database_setup.sql       # Veritabanı kurulumu
├── premium_plans_setup.sql  # Premium plan kurulumu
├── README.md               # Proje dokümantasyonu
└── RENDER_DEPLOYMENT.md    # Bu dosya
```

### **requirements.txt**
```txt
# Core dependencies
python-telegram-bot==20.7
python-dotenv==1.0.0
supabase==2.3.4
google-generativeai==0.8.3

# Async and scheduling
apscheduler==3.10.4
asyncio==3.4.3

# PDF generation
fpdf2==2.7.8

# HTTP client
httpx==0.27.0

# Database and utilities
psycopg2-binary==2.9.9
python-dateutil==2.8.2

# Development and testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Logging and monitoring
structlog==23.2.0

# Security
cryptography==41.0.7

# Performance
uvloop==0.19.0; sys_platform != "win32"
```

---

## 🚀 **Render.com Deployment Adımları**

### **1. Render Dashboard'a Giriş**
1. [Render.com](https://render.com) hesabınıza giriş yapın
2. **"New +"** butonuna tıklayın
3. **"Web Service"** seçin

### **2. GitHub Repository Bağlama**
```
Repository: username/fal-gram-bot
Branch: main
Root Directory: (boş bırakın)
```

### **3. Service Konfigürasyonu**
```
Name: fal-gram-bot
Environment: Python 3
Region: Frankfurt (EU) veya en yakın bölge
Branch: main
Root Directory: (boş bırakın)
Build Command: pip install -r requirements.txt
Start Command: python bot.py
```

### **4. Environment Variables**
```
TELEGRAM_BOT_TOKEN=your_bot_token
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PAYMENT_PROVIDER_TOKEN=your_payment_token
ADMIN_ID=your_telegram_user_id
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

### **5. Advanced Settings**
```
Auto-Deploy: Yes
Health Check Path: /health
Health Check Timeout: 180
```

---

## 🔧 **Bot.py Web Service Adaptasyonu**

### **Health Check Endpoint Ekleme**
```python
# bot.py dosyasına ekleyin
from flask import Flask, jsonify
import threading

# Flask app oluştur
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Render.com health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def home():
    """Ana sayfa"""
    return jsonify({
        'message': 'Fal Gram Bot is running!',
        'version': '3.1.1',
        'status': 'active'
    })

def run_flask():
    """Flask server'ı ayrı thread'de çalıştır"""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Ana fonksiyonda Flask'ı başlat
if __name__ == '__main__':
    # Flask server'ı başlat
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot'u başlat
    main()
```

### **Güncellenmiş requirements.txt**
```txt
# Web service için ek dependency
flask==3.0.0
gunicorn==21.2.0
```

---

## 🗄️ **Veritabanı Kurulumu**

### **1. Supabase Kullanımı (Önerilen)**
```bash
# Supabase projesi oluşturun
# database_setup.sql dosyasını çalıştırın
# premium_plans_setup.sql dosyasını çalıştırın
```

### **2. Render PostgreSQL (Alternatif)**
```yaml
# render.yaml dosyasına ekleyin
databases:
  - name: fal-gram-db
    databaseName: falgram
    user: falgram_user
    plan: starter
```

### **3. Veritabanı Bağlantı Kontrolü**
```python
# bot.py'de veritabanı bağlantı testi
def test_database_connection():
    try:
        # Supabase bağlantı testi
        result = supabase_manager.get_all_users()
        logger.info(f"Database connection successful. Users: {len(result)}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
```

---

## 🔐 **Güvenlik ve Environment Variables**

### **1. Environment Variables Yönetimi**
```bash
# Render Dashboard > Environment > Environment Variables
TELEGRAM_BOT_TOKEN=8349051304:AAEPIzAp05qKPCz4h205lYzFEIzzcwRLtTI
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
PAYMENT_PROVIDER_TOKEN=your_telegram_stars_token
ADMIN_ID=123456789
ENVIRONMENT=production
```

### **2. .env.example Dosyası**
```bash
# .env.example dosyası oluşturun
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
PAYMENT_PROVIDER_TOKEN=your_payment_token_here
ADMIN_ID=your_telegram_user_id_here
ENVIRONMENT=production
```

### **3. Güvenlik Kontrolleri**
```python
# bot.py'de environment kontrolü
def validate_environment():
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'GEMINI_API_KEY', 
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'PAYMENT_PROVIDER_TOKEN',
        'ADMIN_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {missing_vars}")
    
    logger.info("All environment variables are set correctly")
```

---

## 📊 **Monitoring ve Logs**

### **1. Render Logs**
```bash
# Render Dashboard > Logs
# Gerçek zamanlı log görüntüleme
# Error tracking ve debugging
```

### **2. Health Check Monitoring**
```python
# Health check endpoint'i
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'bot_status': 'running',
        'database': test_database_connection(),
        'gemini_api': test_gemini_connection(),
        'timestamp': datetime.now().isoformat()
    })
```

### **3. Error Tracking**
```python
# Hata loglama
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hata yakalama
try:
    # Bot işlemleri
    pass
except Exception as e:
    logger.error(f"Bot error: {e}")
    # Render logs'a gönder
```

---

## 🔄 **Continuous Deployment**

### **1. Auto-Deploy Ayarları**
```yaml
# render.yaml
autoDeploy: true
```

### **2. GitHub Webhook**
- Render otomatik olarak GitHub webhook'u kurar
- Her `git push` işleminde otomatik deployment
- Branch protection kuralları

### **3. Deployment Pipeline**
```bash
# Deployment süreci
1. GitHub'a kod push
2. Render webhook tetiklenir
3. Build process başlar
4. Dependencies yüklenir
5. Bot başlatılır
6. Health check yapılır
7. Deployment tamamlanır
```

---

## 🚨 **Troubleshooting**

### **1. Yaygın Hatalar**

#### **Build Error: Requirements**
```bash
# requirements.txt dosyasını kontrol edin
# Python versiyonunu kontrol edin
# Dependency çakışmalarını çözün
```

#### **Runtime Error: Environment Variables**
```bash
# Render Dashboard > Environment Variables
# Tüm gerekli değişkenlerin set edildiğini kontrol edin
# Değişken isimlerinin doğru olduğunu kontrol edin
```

#### **Database Connection Error**
```bash
# Supabase bağlantı bilgilerini kontrol edin
# Network erişimini kontrol edin
# Database tablolarının oluşturulduğunu kontrol edin
```

### **2. Performance Optimizasyonu**
```python
# Bot performans optimizasyonları
import asyncio
import uvloop

# uvloop kullan (Linux'ta)
if sys.platform != "win32":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Connection pooling
# Async operations
# Memory management
```

---

## 📈 **Scaling ve Production**

### **1. Production Ayarları**
```yaml
# render.yaml production ayarları
services:
  - type: web
    name: fal-gram-bot
    env: python
    plan: standard  # Ücretli plan
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
    envVars:
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /health
    autoDeploy: true
    numInstances: 2  # Çoklu instance
```

### **2. Load Balancing**
```python
# Gunicorn konfigürasyonu
# workers = 4
# timeout = 120
# bind = 0.0.0.0:$PORT
```

### **3. Monitoring ve Alerts**
```python
# Custom monitoring
@app.route('/metrics')
def metrics():
    return jsonify({
        'active_users': get_active_users_count(),
        'total_readings': get_total_readings(),
        'premium_users': get_premium_users_count(),
        'revenue_today': get_today_revenue()
    })
```

---

## 🔗 **Domain ve SSL**

### **1. Custom Domain**
```bash
# Render Dashboard > Settings > Custom Domain
# Domain adınızı ekleyin
# DNS ayarlarını yapın
```

### **2. SSL Sertifikası**
```bash
# Render otomatik SSL sağlar
# HTTPS zorunlu
# Certificate renewal otomatik
```

---

## 📞 **Destek ve İletişim**

### **1. Render Support**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

### **2. Bot Support**
- GitHub Issues
- Telegram Support Channel
- Email Support

---

## ✅ **Deployment Checklist**

### **Pre-Deployment**
- [ ] GitHub repository hazır
- [ ] requirements.txt güncel
- [ ] Environment variables hazır
- [ ] Database kurulumu tamamlandı
- [ ] Bot.py web service uyumlu

### **Deployment**
- [ ] Render.com hesabı oluşturuldu
- [ ] Web service oluşturuldu
- [ ] Environment variables set edildi
- [ ] Build başarılı
- [ ] Health check geçti

### **Post-Deployment**
- [ ] Bot çalışıyor
- [ ] Database bağlantısı aktif
- [ ] Premium özellikler çalışıyor
- [ ] Admin panel erişilebilir
- [ ] Logs kontrol edildi

---

**Son Güncelleme**: 29 Temmuz 2025  
**Versiyon**: 3.1.1  
**Platform**: Render.com  
**Dokümantasyon**: Deployment Kılavuzu 
# 🚀 Deployment Guide - Fal Gram v3.1.1

Bu rehber **Fal Gram v3.1.1 Gelişmiş Admin Panel & Dil Desteği** sürümünün production ortamına deploy edilmesi için kapsamlı bir kılavuzdur.

---

## 📋 **İçindekiler**

1. [Genel Bakış](#genel-bakış)
2. [Sistem Gereksinimleri](#sistem-gereksinimleri)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Production Deployment](#production-deployment)
5. [Database Migration](#database-migration)
6. [Premium Features Activation](#premium-features-activation)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Hardening](#security-hardening)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## 🌟 **Genel Bakış**

Fal Gram v3.1.1 aşağıdaki yeni bileşenleri içerir:

- **Gelişmiş Admin Panel** - Kapsamlı premium yönetim sistemi
- **Premium Yönetimi** - Hediye abonelik, iptal etme, istatistikler
- **Çok Dilli Admin Panel** - 9 dilde admin panel desteği
- **Admin Komutları** - Terminal üzerinden premium yönetimi
- **Premium PDF Raporları** - Detaylı premium kullanıcı raporları
- **Dinamik Dil Desteği** - Butonlar ve mesajlar dil değişiminde güncelleniyor
- **Tam Astroloji Modülü** - Haftalık ve aylık burç yorumları
- **Supabase Prompt Yönetim Sistemi** - Dinamik AI prompt kontrolü

---

## 🖥️ **Sistem Gereksinimleri**

### **Minimum Sistem Özellikleri**
```bash
# Server Specifications
CPU: 2 vCPU (4 vCPU önerilen)
RAM: 2 GB (4 GB önerilen)
Disk: 20 GB SSD (50 GB önerilen)
Network: 100 Mbps
OS: Ubuntu 20.04 LTS / CentOS 8 / Debian 11
```

### **Software Dependencies**
```bash
# Required Software
Python 3.9+ (3.11 önerilen)
pip 21.0+
systemd (service management)
nginx (reverse proxy)
certbot (SSL certificates)
git 2.25+
```

### **External Services**
```bash
# API Services
Telegram Bot API
Google Gemini AI API
Supabase PostgreSQL Database
Telegram Stars Payment Gateway

# Monitoring (opsiyonel)
Sentry (error tracking)
New Relic / DataDog (performance)
Uptime Robot (availability)
```

---

## ✅ **Pre-Deployment Checklist**

### **1. Environment Variables**
```bash
# .env dosyası kontrol listesi
✅ TELEGRAM_BOT_TOKEN=your_bot_token
✅ GEMINI_API_KEY=your_gemini_key
✅ SUPABASE_URL=your_supabase_url
✅ SUPABASE_KEY=your_supabase_anon_key
✅ PAYMENT_PROVIDER_TOKEN=your_telegram_stars_token
✅ ADMIN_ID=your_telegram_user_id
✅ ENCRYPTION_KEY=your_32_byte_key  # NEW for v3.0.0
✅ SENTRY_DSN=your_sentry_dsn       # Optional
```

### **2. API Keys Validation**
```bash
# API erişim testleri
✅ Telegram Bot Token geçerli
✅ Gemini API Key aktif (2.0 Flash Exp erişimi)
✅ Supabase Database bağlantısı
✅ Telegram Stars Provider Token geçerli
✅ Rate limit kontrolü yapıldı
```

### **3. Database Schema**
```bash
# Veritabanı hazırlığı
✅ Supabase project oluşturuldu
✅ database_setup.sql çalıştırıldı
✅ Premium tables oluşturuldu
✅ Indexes ve triggers aktif
✅ Default config değerleri set edildi
```

### **4. Premium System Configuration**
```bash
# Premium özellik kontrolü
✅ Telegram Stars payment test edildi
✅ Plan fiyatları doğrulandı
✅ Premium features test edildi
✅ Subscription flow test edildi
✅ VIP chatbot çalışıyor
```

---

## 🚀 **Production Deployment**

### **1. Server Setup**

#### **Ubuntu/Debian Server Kurulumu**
```bash
# System update
sudo apt update && sudo apt upgrade -y

# Python 3.11 installation
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# System dependencies
sudo apt install nginx git curl certbot python3-certbot-nginx htop -y

# Firewall configuration
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### **Application User Setup**
```bash
# Dedicated user for application
sudo useradd -m -s /bin/bash falbot
sudo usermod -aG sudo falbot
sudo su - falbot

# SSH key setup (optional)
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Copy your public key to ~/.ssh/authorized_keys
```

### **2. Application Deployment**

#### **Code Deployment**
```bash
# Clone repository
cd /home/falbot
git clone https://github.com/yourusername/fal-gram.git
cd fal-gram

# Checkout production branch/tag
git checkout v3.0.0

# Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Dependencies installation
pip install --upgrade pip
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
nano .env  # Configure all environment variables
```

#### **File Permissions**
```bash
# Set proper permissions
chmod +x bot.py
chmod 600 .env  # Secure environment file
chown -R falbot:falbot /home/falbot/fal-gram
```

### **3. Systemd Service Configuration**

#### **Service File Creation**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/falbot.service
```

```ini
[Unit]
Description=Fal Gram Telegram Bot v3.1.0
After=network.target
Wants=network.target

[Service]
Type=simple
User=falbot
Group=falbot
WorkingDirectory=/home/falbot/fal-gram
Environment=PATH=/home/falbot/fal-gram/venv/bin
ExecStart=/home/falbot/fal-gram/venv/bin/python bot.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Resource limits
MemoryMax=1G
CPUQuota=200%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/falbot/fal-gram

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=falbot

[Install]
WantedBy=multi-user.target
```

#### **Service Management**
```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable falbot.service
sudo systemctl start falbot.service

# Check status
sudo systemctl status falbot.service

# View logs
sudo journalctl -u falbot.service -f
```

### **4. Nginx Reverse Proxy (Optional)**

#### **Nginx Configuration**
```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/falgram
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Webhook endpoint for Telegram
    location /webhook/your_bot_token {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=telegram_webhook burst=10 nodelay;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8080;
        access_log off;
    }

    # Block all other requests
    location / {
        return 444;
    }
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=telegram_webhook:10m rate=1r/s;
}
```

#### **SSL Certificate**
```bash
# Enable site and get SSL
sudo ln -s /etc/nginx/sites-available/falgram /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get Let's Encrypt certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## 🗄️ **Database Migration**

### **1. Supabase Setup**

#### **Project Creation**
```bash
# 1. Supabase dashboard (https://supabase.com)
# 2. Create new project
# 3. Configure database password
# 4. Note down project URL and anon key
```

#### **Database Schema Deployment**
```sql
-- Run in Supabase SQL Editor
-- 1. Copy contents of database_setup.sql
-- 2. Execute in SQL Editor
-- 3. Verify all tables created

-- Check table creation
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Expected tables:
-- users, logs, config, prompts
-- premium_subscriptions (NEW)
-- chatbot_history (NEW)
-- moon_notifications (NEW)
-- user_connections (NEW)
-- weekly_reports (NEW)
```

### **2. Data Migration (if upgrading)**

#### **User Data Migration**
```python
# Migration script for existing users
import asyncio
from supabase import create_client

async def migrate_existing_users():
    """Mevcut kullanıcıları v3.0.0 formatına migrate eder"""
    
    # Get all users
    users = supabase.table("users").select("*").execute()
    
    for user in users.data:
        user_id = user['user_id']
        
        # Add new premium fields
        updates = {
            'premium_plan': 'free',
            'astro_subscribed': False,
            'moon_notifications': False
        }
        
        supabase.table("users").update(updates).eq("user_id", user_id).execute()
        print(f"Migrated user {user_id}")

# Run migration
asyncio.run(migrate_existing_users())
```

### **3. Backup Strategy**

#### **Automated Backups**
```bash
# Daily backup script
#!/bin/bash
# /home/falbot/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/falbot/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Supabase backup (via API)
curl -X POST \
  "https://your-supabase-url.supabase.co/rest/v1/rpc/backup_database" \
  -H "apikey: your-service-role-key" \
  -H "Authorization: Bearer your-service-role-key" \
  > $BACKUP_DIR/database_backup_$DATE.sql

# Keep last 7 days
find $BACKUP_DIR -name "database_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### **Crontab Setup**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/falbot/scripts/backup.sh >> /var/log/falbot_backup.log 2>&1
```

---

## 📝 **SQL Prompt Dosyaları Kurulumu**

### **1. Supabase SQL Editor'da Çalıştırılacak Dosyalar**

#### **Sıralı Kurulum**
```sql
-- 1. Doğum haritası prompt'ları
-- update_birth_chart_prompts.sql dosyasını çalıştırın

-- 2. Uyumluluk analizi prompt'ları  
-- update_compatibility_prompts.sql dosyasını çalıştırın

-- 3. Haftalık burç prompt'ları
-- update_weekly_horoscope_prompts.sql dosyasını çalıştırın

-- 4. Aylık burç prompt'ları
-- update_monthly_horoscope_prompts.sql dosyasını çalıştırın

-- 5. Astroloji chatbot prompt'ları
-- update_astro_chatbot_prompts.sql dosyasını çalıştırın
```

#### **Prompt Dosyaları İçeriği**
Her dosya aşağıdaki dillerde prompt'ları içerir:
- 🇹🇷 Türkçe (TR)
- 🇺🇸 İngilizce (EN) 
- 🇪🇸 İspanyolca (ES)
- 🇫🇷 Fransızca (FR)
- 🇷🇺 Rusça (RU)
- 🇩🇪 Almanca (DE)
- 🇸🇦 Arapça (AR)
- 🇮🇹 İtalyanca (IT)
- 🇵🇹 Portekizce (PT)

#### **Veritabanı Kontrolü**
```sql
-- Prompt'ların başarıyla eklendiğini kontrol edin
SELECT prompt_type, language, COUNT(*) as count 
FROM prompts 
WHERE prompt_type IN ('birth_chart', 'compatibility', 'weekly_horoscope', 'monthly_horoscope', 'astro_chatbot')
GROUP BY prompt_type, language
ORDER BY prompt_type, language;

-- Toplam 45 prompt olmalı (5 tip × 9 dil)
```

### **2. Prompt Sistemi Testi**

#### **Bot.py Test Fonksiyonları**
```python
# Test prompt retrieval
def test_prompt_system():
    """Prompt sistemini test eder"""
    
    test_cases = [
        ('birth_chart', 'tr'),
        ('compatibility', 'en'),
        ('weekly_horoscope', 'es'),
        ('monthly_horoscope', 'fr'),
        ('astro_chatbot', 'ru')
    ]
    
    for prompt_type, lang in test_cases:
        prompt = supabase_manager.get_prompt(prompt_type, lang)
        if prompt:
            print(f"✅ {prompt_type} - {lang}: OK")
        else:
            print(f"❌ {prompt_type} - {lang}: FAILED")
```

#### **Placeholder Test**
```python
# Test placeholder replacement
def test_placeholders():
    """Placeholder değiştirme sistemini test eder"""
    
    test_data = {
        'username': 'TestUser',
        'sign': 'Aslan',
        'birth_date': '15.08.1990',
        'first_sign': 'Aslan',
        'second_sign': 'Terazi'
    }
    
    prompt = supabase_manager.get_prompt('birth_chart', 'tr')
    if prompt:
        formatted = prompt.format(**test_data)
        print(f"Formatted prompt: {formatted[:100]}...")
```

---

## 💎 **Premium Features Activation**

### **1. Telegram Stars Configuration**

#### **Payment Provider Setup**
```python
# Bot configuration for payments
PAYMENT_PROVIDER_TOKEN = "your_telegram_stars_token"

# Test payment in development
from telegram import LabeledPrice

async def test_payment():
    prices = [LabeledPrice("Test Premium", 100)]  # 100 stars
    
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Test Premium Plan",
        description="Test payment flow",
        payload="test_premium_12345",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="XTR",
        prices=prices
    )
```

#### **Payment Webhook Validation**
```python
# Production webhook validation
def validate_payment_webhook(update):
    """Telegram Stars ödeme webhook'unu doğrular"""
    
    # Check if payment is successful
    if not update.message.successful_payment:
        return False
    
    payment = update.message.successful_payment
    
    # Validate currency
    if payment.currency != "XTR":
        return False
    
    # Validate payload format
    if not payment.invoice_payload.startswith("premium_"):
        return False
    
    return True
```

### **2. Premium Feature Testing**

#### **Plan Activation Test**
```bash
# Test all premium plans
echo "Testing premium plan activation..."

# Basic plan test
curl -X POST "your-bot-webhook/test_premium" \
  -H "Content-Type: application/json" \
  -d '{"plan": "basic", "user_id": 12345, "amount": 500}'

# Premium plan test  
curl -X POST "your-bot-webhook/test_premium" \
  -H "Content-Type: application/json" \
  -d '{"plan": "premium", "user_id": 12345, "amount": 1000}'

# VIP plan test
curl -X POST "your-bot-webhook/test_premium" \
  -H "Content-Type: application/json" \
  -d '{"plan": "vip", "user_id": 12345, "amount": 2000}'
```

#### **VIP Chatbot Testing**
```python
# Test VIP chatbot functionality
async def test_vip_chatbot():
    """VIP chatbot test"""
    
    # Set user as VIP
    supabase_manager.update_user(12345, {'premium_plan': 'vip'})
    
    # Test chatbot interaction
    test_questions = [
        "Bugün Mars'ın etkisi nasıl?",
        "Aslan burcu için bu hafta nasıl?",
        "Venüs geçişi ne zaman?"
    ]
    
    for question in test_questions:
        response = await handle_chatbot_question(question, 'tr', 12345)
        assert response is not None
        print(f"Q: {question}")
        print(f"A: {response[:100]}...")
```

---

## 📊 **Monitoring & Logging**

### **1. System Monitoring**

#### **Health Check Endpoint**
```python
# Add to bot.py
from datetime import datetime
import psutil

@app.route('/health')
async def health_check():
    """Sistem sağlık kontrolü"""
    
    try:
        # Database connectivity test
        users_count = len(supabase_manager.get_all_users())
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'users_count': users_count,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            }
        }
        
        return health_data
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
```

#### **Log Aggregation**
```bash
# Centralized logging with rsyslog
sudo nano /etc/rsyslog.d/99-falbot.conf
```

```bash
# Falbot logs
:programname, isequal, "falbot" /var/log/falbot/app.log
& stop

# Log rotation
sudo nano /etc/logrotate.d/falbot
```

```bash
/var/log/falbot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    copytruncate
    notifempty
}
```

### **2. Error Tracking**

#### **Sentry Integration**
```python
# Add to bot.py
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Sentry configuration
sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[sentry_logging],
    traces_sample_rate=0.1,
    environment="production"
)

# Custom error tracking
def track_error(error, user_id=None, context=None):
    """Özel hata takip fonksiyonu"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_user({"id": user_id})
        scope.set_context("bot_context", context)
        sentry_sdk.capture_exception(error)
```

#### **Performance Monitoring**
```python
# Performance metrics collection
import time
from functools import wraps

def monitor_performance(func_name):
    """Performance monitoring decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful execution
                logger.info(f"Performance: {func_name} completed in {duration:.2f}s")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error with timing
                logger.error(f"Performance: {func_name} failed after {duration:.2f}s - {str(e)}")
                raise e
                
        return wrapper
    return decorator

# Usage example
@monitor_performance("premium_plan_activation")
async def activate_premium_plan(user_id, plan_id, amount):
    # Implementation
    pass
```

---

## 🔒 **Security Hardening**

### **1. Server Security**

#### **Firewall Configuration**
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3
```

#### **SSH Hardening**
```bash
# SSH configuration
sudo nano /etc/ssh/sshd_config

# Recommended settings:
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
AllowUsers falbot
```

### **2. Application Security**

#### **Environment Security**
```bash
# Secure .env file
chmod 600 /home/falbot/fal-gram/.env
chown falbot:falbot /home/falbot/fal-gram/.env

# Check file permissions
ls -la /home/falbot/fal-gram/.env
# Should show: -rw------- 1 falbot falbot
```

#### **API Security**
```python
# Rate limiting implementation
from collections import defaultdict
import time

class SecurityManager:
    def __init__(self):
        self.rate_limits = defaultdict(list)
        self.blocked_users = set()
    
    def check_rate_limit(self, user_id, limit=10, window=60):
        """Rate limiting check"""
        now = time.time()
        user_requests = self.rate_limits[user_id]
        
        # Clean old requests
        recent_requests = [req_time for req_time in user_requests if now - req_time < window]
        self.rate_limits[user_id] = recent_requests
        
        if len(recent_requests) >= limit:
            self.blocked_users.add(user_id)
            return False
        
        # Record request
        self.rate_limits[user_id].append(now)
        return True
    
    def is_user_blocked(self, user_id):
        """Check if user is blocked"""
        return user_id in self.blocked_users

# Global security manager
security_manager = SecurityManager()
```

---

## ⚡ **Performance Optimization**

### **1. Database Optimization**

#### **Connection Pooling**
```python
# Supabase connection optimization
from supabase import create_client, Client
import asyncio

class OptimizedSupabaseManager:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self._connection_pool = None
    
    async def get_connection(self):
        """Connection pool management"""
        if not self._connection_pool:
            self._connection_pool = await asyncio.create_task(
                self._create_connection_pool()
            )
        return self._connection_pool
    
    async def _create_connection_pool(self):
        """Create optimized connection pool"""
        # Implementation depends on Supabase SDK
        return self.client
```

#### **Query Optimization**
```python
# Optimized database queries
class DatabaseOptimizations:
    
    @staticmethod
    async def get_user_with_premium_info(user_id: int):
        """Single query for user + premium info"""
        query = """
        SELECT u.*, ps.plan_type, ps.expires_at
        FROM users u
        LEFT JOIN premium_subscriptions ps ON u.user_id = ps.user_id 
        WHERE u.user_id = %s AND (ps.active = true OR ps.active IS NULL)
        ORDER BY ps.created_at DESC
        LIMIT 1
        """
        return await supabase_manager.execute_query(query, [user_id])
    
    @staticmethod
    async def get_premium_users_batch(limit=100):
        """Batch processing for premium users"""
        query = """
        SELECT user_id, premium_plan 
        FROM users 
        WHERE premium_plan != 'free'
        LIMIT %s
        """
        return await supabase_manager.execute_query(query, [limit])
```

### **2. Caching Strategy**

#### **Redis Caching (Optional)**
```python
# Redis caching for frequently accessed data
import redis
import json
from functools import wraps

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def cache_result(self, key_prefix, expiration=3600):
        """Caching decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key, 
                    expiration, 
                    json.dumps(result, default=str)
                )
                
                return result
            return wrapper
        return decorator

# Usage
cache_manager = CacheManager()

@cache_manager.cache_result("user_premium", expiration=1800)
async def get_user_premium_status(user_id):
    return check_premium_status(user_id)
```

### **3. Memory Management**

#### **Memory Monitoring**
```python
import psutil
import gc

class MemoryManager:
    @staticmethod
    def monitor_memory():
        """Memory usage monitoring"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def cleanup_memory():
        """Force garbage collection"""
        gc.collect()
        
        # Log memory usage after cleanup
        memory_usage = MemoryManager.monitor_memory()
        logger.info(f"Memory after cleanup: {memory_usage}")

# Periodic memory cleanup
async def periodic_memory_cleanup():
    """Periodic memory cleanup task"""
    while True:
        await asyncio.sleep(3600)  # Every hour
        MemoryManager.cleanup_memory()
```

---

## 🔧 **Troubleshooting**

### **1. Common Issues & Solutions**

#### **Bot Not Responding**
```bash
# Check service status
sudo systemctl status falbot.service

# Check logs
sudo journalctl -u falbot.service -f --lines=50

# Common fixes:
sudo systemctl restart falbot.service
sudo systemctl reload falbot.service

# If still not working:
sudo systemctl stop falbot.service
cd /home/falbot/fal-gram
source venv/bin/activate
python bot.py  # Run manually to see errors
```

#### **Database Connection Issues**
```python
# Database connectivity test
async def test_database_connection():
    """Test Supabase connection"""
    try:
        # Simple query test
        result = supabase_manager.supabase.table("users").select("user_id").limit(1).execute()
        print(f"Database connection: OK - Sample data: {result.data}")
        return True
    except Exception as e:
        print(f"Database connection: FAILED - Error: {e}")
        return False

# Run test
asyncio.run(test_database_connection())
```

#### **Gemini API Issues**
```python
# Gemini API test
async def test_gemini_api():
    """Test Gemini API connectivity"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async("Test message")
        print(f"Gemini API: OK - Response: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"Gemini API: FAILED - Error: {e}")
        return False

# Run test
asyncio.run(test_gemini_api())
```

### **2. Performance Issues**

#### **High Memory Usage**
```bash
# Check memory usage
free -h
ps aux | grep python | grep bot.py

# Restart service if memory > 1GB
if [ $(ps -o pid,vsz,comm | grep bot.py | awk '{print $2}') -gt 1000000 ]; then
    sudo systemctl restart falbot.service
    echo "Bot restarted due to high memory usage"
fi
```

#### **Slow Response Times**
```python
# Response time monitoring
import time

async def monitor_response_times():
    """Monitor and log response times"""
    
    # Test different operations
    operations = {
        'database_query': lambda: supabase_manager.get_user(12345),
        'gemini_api': lambda: gemini_model.generate_content_async("test"),
        'premium_check': lambda: check_premium_status(12345)
    }
    
    for name, operation in operations.items():
        start_time = time.time()
        try:
            await operation()
            duration = time.time() - start_time
            print(f"{name}: {duration:.2f}s")
        except Exception as e:
            duration = time.time() - start_time
            print(f"{name}: FAILED after {duration:.2f}s - {e}")
```

### **3. Premium Feature Issues**

#### **Payment Not Processing**
```python
# Payment debugging
def debug_payment_webhook(update):
    """Debug payment webhook issues"""
    
    if not update.message:
        print("No message in update")
        return
    
    if not update.message.successful_payment:
        print("No successful_payment in message")
        return
    
    payment = update.message.successful_payment
    print(f"Payment debug:")
    print(f"  Currency: {payment.currency}")
    print(f"  Total amount: {payment.total_amount}")
    print(f"  Payload: {payment.invoice_payload}")
    print(f"  Provider payment charge id: {payment.provider_payment_charge_id}")
    
    # Validate payload
    if not payment.invoice_payload.startswith("premium_"):
        print("ERROR: Invalid payload format")
        return
    
    payload_parts = payment.invoice_payload.split("_")
    print(f"  Parsed payload: {payload_parts}")
```

#### **VIP Features Not Working**
```python
# VIP feature debugging
async def debug_vip_features(user_id):
    """Debug VIP feature access"""
    
    user = supabase_manager.get_user(user_id)
    print(f"User debug for {user_id}:")
    print(f"  Premium plan: {user.get('premium_plan')}")
    print(f"  Premium expires: {user.get('premium_expires_at')}")
    
    # Check premium status
    current_plan = check_premium_status(user_id)
    print(f"  Current plan (calculated): {current_plan}")
    
    # Check VIP access
    has_vip = check_user_premium_access(user_id, 'vip')
    print(f"  VIP access: {has_vip}")
    
    # Test chatbot state
    user_state = user.get('state')
    print(f"  User state: {user_state}")
```

---

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
```bash
# Load balancer configuration (nginx)
upstream falbot_backends {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    location / {
        proxy_pass http://falbot_backends;
    }
}
```

### **Database Scaling**
```sql
-- Read replicas for heavy queries
-- Use Supabase Read Replicas for analytics queries

-- Partitioning for large tables
CREATE TABLE logs_2025_01 PARTITION OF logs
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

**Bu deployment guide'ı Fal Gram v3.0.0'ın production ortamında güvenli ve verimli çalışması için gerekli tüm adımları içerir.**

**Son güncellenme: 27 Ocak 2025** 
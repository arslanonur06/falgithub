# 🔮 Fal Gram - AI-Powered Fortune Telling Telegram Bot

**Version: 3.1.0** | Tam Astroloji Modülü & Supabase Prompt Sistemi

Fal Gram, kullanıcılara **kahve falı**, **tarot okuma**, **rüya tabiri** ve **gelişmiş astroloji hizmetleri** sunan yenilikçi bir Telegram botudur. Google Gemini AI teknolojisi ile desteklenen bot, **8 farklı dilde** hizmet vermekte ve **3 seviyeli premium abonelik sistemi** sunmaktadır.

---

## 🌟 **Ana Özellikler**

### 🔮 **AI Destekli Falcılık**
- **☕ Kahve Falı** - Fincan fotoğrafı ile AI görsel analizi
- **🎴 Tarot Okuma** - Otomatik kart çekimi ve AI yorumlama
- **💭 Rüya Tabiri** - Kişiselleştirilmiş rüya analizi

### ⭐ **Kapsamlı Astroloji Sistemi**
- **🌟 Doğum Haritası** - Detaylı kişisel astrolojik analiz
- **📅 Günlük Burç** - 12 burç için günlük AI yorumları
- **📊 Haftalık Burç** - Premium kullanıcılar için haftalık detaylı yorumlar
- **📅 Aylık Burç** - Premium kullanıcılar için aylık kapsamlı raporlar
- **💕 Uyumluluk Analizi** - İki burç arasındaki astrolojik uyumluluk
- **🌙 Gelişmiş Ay Takvimi** - Gerçek ay fazları ve etkileri
- **🤖 7/24 Astroloji Chatbot** - VIP özelliği

### 💎 **Premium Abonelik Seviyeleri**

#### 🆓 **Ücretsiz Plan**
- 5  ücretsiz fal hakkı
- Temel özellikler
- Reklamlar

#### ⭐ **Temel Plan - 500 Telegram Star ($2.99/ay)**
- ✅ Sınırsız kahve falı
- ✅ Sınırsız tarot falı
- ✅ Sınırsız rüya tabiri
- ✅ Günlük burç yorumu
- ✅ Temel doğum haritası
- ⭐ Reklamsız deneyim

#### 🌟 **Premium Plan - 1000 Telegram Star ($4.99/ay)**
- 🌟 Temel Plan + tüm özellikler
- ✅ Haftalık burç yorumları
- ✅ Aylık burç yorumları
- ✅ Detaylı uyumluluk analizi
- ✅ Ay takvimi bildirimleri
- ✅ PDF raporları indirme
- ✅ Özel gezegen geçişleri
- 💎 Premium içerikler

#### 👑 **VIP Plan - 2000 Telegram Star ($9.99/ay)**
- 👑 Premium Plan + tüm özellikler
- ✅ 7/24 Astroloji Chatbot
- ✅ Kişisel astroloji danışmanı
- ✅ Aylık detaylı raporlar
- ✅ Sosyal özellikler erişimi
- ✅ Öncelikli destek
- ✅ Özel VIP içerikler
- 🎯 Kişiselleştirilmiş öneriler

### 🌐 **Çoklu Dil Desteği**
- 🇹🇷 Türkçe | 🇺🇸 English | 🇪🇸 Español | 🇫🇷 Français | 🇷🇺 Русский
- 🇩🇪 Deutsch | 🇸🇦 العربية | 🇮🇹 Italiano
- **Otomatik dil tespiti** - Telegram client dilinizi algılar
- **Kültürel uyarlama** - Her dil için özel terimler

### 🚀 **Gelişmiş Özellikler**
- **👥 Referral Sistemi** - Arkadaş davet etme ve ödül kazanma
- **📱 Günlük Kart Aboneliği** - Otomatik tarot kartı gönderimi
- **🔧 Kapsamlı Admin Panel** - Kullanıcı yönetimi, premium yönetimi ve PDF raporlar
- **💎 Premium Yönetimi** - Abonelik hediye etme, iptal etme, istatistikler
- **📊 Detaylı İstatistikler** - Kullanım analitikleri ve gelir raporları
- **🌙 Ay Bildirimleri** - Dolunay/yeniay özel mesajları
- **🗄️ Supabase Prompt Sistemi** - Dinamik AI prompt yönetimi
- **🌍 Çok Dilli AI Yanıtlar** - 8 dilde doğal AI yorumları
- **🎁 Hediye Abonelik Sistemi** - Admin komutları ile premium hediye etme
- **📈 Gerçek Zamanlı Analitik** - Canlı kullanıcı ve gelir takibi

---

## 🛠 **Teknoloji Stack**

### **Backend & AI**
- **Python 3.9+** - Ana geliştirme dili
- **python-telegram-bot 20.x** - Telegram Bot API
- **Google Gemini 2.0 Flash** - AI model (fallback: 1.5 Flash)
- **Supabase PostgreSQL** - Veritabanı ve backend
- **APScheduler** - Zamanlanmış görevler

### **Libraries & Tools**
- **Pillow** - Görsel işleme
- **fpdf2** - PDF rapor oluşturma
- **python-dotenv** - Ortam değişkenleri
- **asyncio** - Asenkron işlemler
- **logging** - Sistem logları

### **Deployment & Infrastructure**
- **Supabase** - Database as a Service
- **Telegram Bot API** - Mesajlaşma platformu
- **Google AI Studio** - Gemini API erişimi
- **GitHub** - Versiyon kontrol

---

## 📋 **Kurulum ve Çalıştırma**

### **1. Gereksinimler**
```bash
Python 3.9+
Telegram Bot Token
Google Gemini API Key
Supabase Project
Telegram Stars Provider Token
```

### **2. Proje Kurulumu**
```bash
# Repository klonlama
git clone https://github.com/yourusername/fal-gram.git
cd fal-gram

# Virtual environment oluşturma
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Bağımlılıkları yükleme
pip install -r requirements.txt
```

### **3. Ortam Değişkenleri**
`.env` dosyası oluşturun:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
PAYMENT_PROVIDER_TOKEN=your_telegram_stars_token
ADMIN_ID=your_telegram_user_id
```

### **4. Veritabanı Kurulumu**
```bash
# Supabase SQL Editor'da çalıştırın
psql -f database_setup.sql
```

### **5. Botı Başlatma**
```bash
python bot.py
```

---

## 📱 **Kullanım Senaryoları**

### **🔮 Günlük Kullanıcı**
1. `/start` - Botu başlat
2. **Kahve Falı** - Fincan fotoğrafı gönder
3. **AI Analizi** - Gemini ile fal yorumu al
4. **Günlük Burç** - Burcunuzu öğren

### **💎 Premium Kullanıcı**
1. **Premium'a Geç** - Plan seç ve öde
2. **Sınırsız Fallar** - Tüm özelliklere erişim
3. **Haftalık Raporlar** - Detaylı astroloji analizi
4. **PDF İndir** - Raporları kaydet

### **👑 VIP Kullanıcı**
1. **7/24 Chatbot** - Astroloji soruları sor
2. **Sosyal Özellikler** - Arkadaşlarla burç uyumu
3. **Kişisel Danışman** - Özel rehberlik
4. **Öncelikli Destek** - Hızlı yardım

---

## 🎯 **Bot Komutları**

### **Kullanıcı Komutları**
- `/start` - Botu başlat ve ana menüyü göster
- Ana menü navigasyonu ile tüm özellikler

### **Admin Komutları**
- `/admin` - Admin paneline erişim (ADMIN_ID gerekli)
- **Kullanıcı Yönetimi** - Detaylı kullanıcı listesi ve PDF raporları
- **💎 Premium Yönetimi** - Abonelik yönetimi, hediye verme, iptal etme
- **📊 İstatistikler** - Gerçek zamanlı kullanıcı ve gelir analitikleri
- **📝 Log Kayıtları** - Sistem aktivitelerini izleme
- **⚙️ Ayarlar** - Bot konfigürasyonu ve prompt yönetimi
- **📄 PDF Raporlar** - Kapsamlı raporlar indirme
- **🎁 Hediye Abonelik** - `/gift <user_id> <plan> <days>` komutu
- **❌ Abonelik İptal** - `/cancel <user_id>` komutu

---

## 📊 **Özellik Matrisi**

| Özellik | Ücretsiz | Temel | Premium | VIP |
|---------|----------|-------|---------|-----|
| Kahve Falı | 3 hak | ∞ | ∞ | ∞ |
| Tarot Falı | 3 hak | ∞ | ∞ | ∞ |
| Rüya Tabiri | 3 hak | ∞ | ∞ | ∞ |
| Günlük Burç | ❌ | ✅ | ✅ | ✅ |
| Doğum Haritası | ❌ | Temel | Detaylı | Premium |
| Haftalık Burç | ❌ | ❌ | ✅ | ✅ |
| Aylık Burç | ❌ | ❌ | ✅ | ✅ |
| PDF İndir | ❌ | ❌ | ✅ | ✅ |
| 7/24 Chatbot | ❌ | ❌ | ❌ | ✅ |
| Sosyal Özellikler | ❌ | ❌ | ❌ | ✅ |
| Reklamlar | ✅ | ❌ | ❌ | ❌ |

---

## 🔗 **API Entegrasyonları**

- **Telegram Bot API** - Mesajlaşma ve ödeme sistemi
- **Google Gemini API** - AI model ve görsel analiz
- **Supabase API** - Veritabanı işlemleri
- **Telegram Stars** - Premium abonelik ödemeleri

---

## 🗺 **Roadmap**

### **v3.1.0 - Tam Astroloji Modülü & Gelişmiş Admin Panel** ✅
- 📊 Haftalık burç yorumları (Premium)
- 📅 Aylık burç yorumları (Premium)
- 🗄️ Supabase prompt yönetim sistemi
- 🌍 9 dilde AI yanıtları
- 🔧 Dinamik prompt güncelleme
- 📝 SQL prompt dosyaları
- 💎 Kapsamlı Premium Yönetimi
- 🎁 Hediye Abonelik Sistemi
- 📈 Gerçek Zamanlı Analitik
- 🔧 Gelişmiş Admin Panel
- 📄 Premium PDF Raporları

### **v3.2.0 - Yapay Zeka Plus**
- 🧠 Gelişmiş kişiselleştirme
- 📈 Trend analizi
- 🎯 Akıllı öneriler
- 📱 Push bildirimleri

### **v4.0.0 - Multi-Platform**
- 🌐 Web uygulaması
- 📱 Mobil uygulama
- 💻 Desktop client
- 🔗 API açılımı

---

## 🤝 **Katkıda Bulunma**

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📄 **Lisans**

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

## 📞 **Destek ve İletişim**

- **GitHub Issues** - Bug raporları ve özellik istekleri
- **Telegram** - [@FalGramBot](https://t.me/FalGramBot)
- **Email** - support@falgram.com

---

## 🙏 **Teşekkürler**

- **Google Gemini AI** - Güçlü AI model desteği
- **Telegram** - Excellent bot platform
- **Supabase** - Backend as a Service
- **Python Telegram Bot** - Harika library

---

**⭐ Projeyi beğendiyseniz star vermeyi unutmayın!**

*Son güncellenme: 28 Temmuz 2025*
 
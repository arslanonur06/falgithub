# 🌟 FAL GRAM - Premium Plan Sistemi

## 📋 Genel Bakış

Fal Gram, kullanıcılarına **Premium odaklı** bir deneyim sunar. Ücretsiz kullanıcılar **5 fal hakkı** ile başlar ve sonrasında **Premium Planlara** yönlendirilir.

---

## 🎯 Plan Yapısı

### 🆓 **Ücretsiz Plan**
- **Fiyat:** 0 ⭐
- **Fal Hakkı:** 5 ücretsiz fal (Kahve, Tarot, Rüya)
- **Özellikler:**
  - ☕ 5 ücretsiz fal (Kahve, Tarot, Rüya)
  - ♈ Günlük burç yorumu
  - 🔮 Temel astroloji özellikleri
  - 📱 Temel chatbot desteği
  - 🎁 Referral bonusları

### 💎 **Temel Plan**
- **Fiyat:** 500 ⭐
- **Fal Hakkı:** ♾️ Sınırsız
- **Özellikler:**
  - ♾️ Sınırsız fal (Kahve, Tarot, Rüya)
  - 📊 Haftalık burç raporu
  - 🔮 Gelişmiş astroloji analizi
  - 💫 Doğum haritası yorumu
  - 🌙 Ay takvimi özellikleri
  - 💬 Gelişmiş chatbot
  - 🎯 Kişiselleştirilmiş öneriler
  - 📈 Detaylı fal geçmişi
  - 🔔 Özel bildirimler

### ⭐ **Premium Plan**
- **Fiyat:** 1000 ⭐
- **Fal Hakkı:** ♾️ Sınırsız
- **Özellikler:**
  - ✨ Temel Plan özellikleri
  - 📅 Aylık burç yorumu
  - 🪐 Gezegen geçişleri analizi
  - 💕 Burç uyumluluğu
  - 🌙 Gelişmiş ay takvimi
  - 📈 Detaylı astroloji raporları
  - 🎯 Kişiselleştirilmiş öneriler
  - 🔮 Özel fal türleri
  - 📊 Astroloji istatistikleri
  - 🎁 Özel içerikler
  - ⚡ Öncelikli destek

### 👑 **VIP Plan**
- **Fiyat:** 2000 ⭐
- **Fal Hakkı:** ♾️ Sınırsız
- **Özellikler:**
  - 👑 Premium Plan özellikleri
  - 🤖 7/24 Astroloji Chatbot
  - 👥 Sosyal astroloji özellikleri
  - 🎁 Özel VIP içerikler
  - ⚡ Öncelikli destek
  - 📊 Gelişmiş analitikler
  - 🎯 Kişisel astroloji danışmanı
  - 🌟 Özel VIP fal türleri
  - 💎 Sınırsız özel içerik
  - 🎪 Özel etkinlikler
  - 📱 Özel VIP arayüzü
  - 🔮 AI destekli kişisel rehberlik

---

## 📊 Özellik Matrisi

| Özellik | Ücretsiz | Temel | Premium | VIP |
|---------|----------|-------|---------|-----|
| **Fal Hakkı** | 5 | ♾️ | ♾️ | ♾️ |
| **Günlük Burç** | ✅ | ✅ | ✅ | ✅ |
| **Haftalık Rapor** | ❌ | ✅ | ✅ | ✅ |
| **Aylık Burç** | ❌ | ❌ | ✅ | ✅ |
| **Doğum Haritası** | ❌ | ✅ | ✅ | ✅ |
| **Ay Takvimi** | ❌ | ✅ | ✅ | ✅ |
| **Gezegen Analizi** | ❌ | ❌ | ✅ | ✅ |
| **Burç Uyumluluğu** | ❌ | ❌ | ✅ | ✅ |
| **7/24 Chatbot** | ❌ | ❌ | ❌ | ✅ |
| **Sosyal Özellikler** | ❌ | ❌ | ❌ | ✅ |
| **Özel İçerikler** | ❌ | ❌ | ✅ | ✅ |
| **Öncelikli Destek** | ❌ | ❌ | ✅ | ✅ |
| **Kişisel Danışman** | ❌ | ❌ | ❌ | ✅ |

---

## 💰 Fiyatlandırma Detayları

### **Ücretsiz Plan**
- **Fiyat:** 0 ⭐
- **Süre:** Süresiz
- **Fal Hakkı:** 5 fal

### **Temel Plan**
- **Fiyat:** 500 ⭐
- **Süre:** 30 gün
- **Fal Hakkı:** Sınırsız

### **Premium Plan**
- **Fiyat:** 1000 ⭐
- **Süre:** 30 gün
- **Fal Hakkı:** Sınırsız

### **VIP Plan**
- **Fiyat:** 2000 ⭐
- **Süre:** 30 gün
- **Fal Hakkı:** Sınırsız

---

## 🗄️ Veritabanı Şeması

### **1. premium_plans**
```sql
CREATE TABLE premium_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    price_stars INTEGER NOT NULL,
    features JSONB NOT NULL,
    features_en JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **2. user_subscriptions**
```sql
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id VARCHAR(20) NOT NULL REFERENCES premium_plans(plan_id),
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP NOT NULL,
    payment_method VARCHAR(50),
    total_paid INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **3. payment_transactions**
```sql
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id VARCHAR(20) REFERENCES premium_plans(plan_id),
    transaction_id VARCHAR(100) UNIQUE,
    amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'XTR',
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    telegram_payment_charge_id VARCHAR(100),
    telegram_payment_provider_charge_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Uygulama Detayları

### **Ödeme Sistemi**
- **Platform:** Telegram Stars
- **Para Birimi:** XTR (Telegram Stars)
- **Ödeme Yöntemi:** Telegram Payment API
- **Abonelik Süresi:** 30 gün

### **Kullanıcı Deneyimi**
1. **Ücretsiz Kullanım:** 5 fal hakkı
2. **Limit Aşımı:** Premium planlara yönlendirme
3. **Plan Seçimi:** 3 farklı plan seçeneği
4. **Otomatik Yenileme:** 30 günlük döngü

### **Premium Özellikler**
- **Sınırsız Fal:** Tüm fal türleri için sınırsız erişim
- **Gelişmiş Analiz:** AI destekli detaylı yorumlar
- **Özel İçerikler:** Plan seviyesine göre özel içerikler
- **Öncelikli Destek:** Hızlı ve öncelikli müşteri desteği

---

## 📈 Analitik ve Raporlama

### **Admin Panel Özellikleri**
- **Kullanıcı İstatistikleri:** Plan bazlı kullanıcı dağılımı
- **Gelir Analizi:** Plan bazlı gelir raporları
- **Premium Yönetimi:** Kullanıcı plan yönetimi
- **PDF Raporları:** Detaylı analitik raporlar

### **Kullanıcı İstatistikleri**
- **Toplam Kullanıcı:** Tüm kayıtlı kullanıcılar
- **Premium Kullanıcı:** Aktif premium aboneler
- **Dönüşüm Oranı:** Ücretsiz → Premium geçiş oranı
- **Gelir Analizi:** Aylık/yıllık gelir trendleri

---

## 🚀 Gelecek Geliştirmeler

### **Plan İyileştirmeleri**
- [ ] **Yıllık Planlar:** Uzun vadeli abonelik seçenekleri
- [ ] **Aile Planları:** Çoklu kullanıcı paketleri
- [ ] **Kurumsal Planlar:** İşletmeler için özel paketler

### **Özellik Geliştirmeleri**
- [ ] **Video Fal:** Canlı video fal seansları
- [ ] **AI Asistan:** Gelişmiş AI destekli rehberlik
- [ ] **Sosyal Platform:** Kullanıcılar arası etkileşim
- [ ] **Mobil Uygulama:** Native mobil uygulama

### **Ödeme Geliştirmeleri**
- [ ] **Çoklu Ödeme:** Farklı ödeme yöntemleri
- [ ] **Otomatik Yenileme:** Kredi kartı ile otomatik yenileme
- [ ] **İade Sistemi:** Memnuniyet garantisi
- [ ] **Promosyon Kodları:** Özel indirim kodları

---

## 📞 Destek ve İletişim

### **Teknik Destek**
- **E-posta:** support@falgram.com
- **Telegram:** @FalGramSupport
- **Dokümantasyon:** docs.falgram.com

### **Satış Desteği**
- **E-posta:** sales@falgram.com
- **Telegram:** @FalGramSales
- **Canlı Destek:** 7/24 chatbot desteği

---

## 📝 Değişiklik Geçmişi

### **v3.2.0 - Premium Odaklı Sistem**
- ✅ **Ücretsiz limit:** 3 → 5 fal
- ✅ **Tek seferlik ödemeler:** Kaldırıldı
- ✅ **Premium planlar:** İyileştirildi
- ✅ **Yönlendirme sistemi:** Premium odaklı
- ✅ **Özellik matrisi:** Güncellendi

### **v3.1.0 - Admin Panel**
- ✅ **Admin paneli:** Gelişmiş yönetim
- ✅ **Referral sistemi:** Detaylı analitik
- ✅ **PDF raporları:** Kapsamlı raporlama
- ✅ **Premium yönetimi:** Kullanıcı plan yönetimi

### **v3.0.0 - Premium Sistemi**
- ✅ **Premium planlar:** 3 farklı plan
- ✅ **Ödeme sistemi:** Telegram Stars entegrasyonu
- ✅ **Astroloji modülü:** Gelişmiş özellikler
- ✅ **Çok dilli destek:** 9 dil desteği

---

**Son Güncelleme:** 28 Temmuz 2025  
**Versiyon:** 3.2.0  
**Durum:** Aktif 
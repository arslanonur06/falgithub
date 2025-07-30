# 🔧 FAL GRAM - Admin Panel Kullanım Kılavuzu

**Version: 3.1.1** | Gelişmiş Admin Panel & Premium Yönetimi

---

## 📋 **Genel Bakış**

Fal Gram Admin Panel, bot yöneticilerinin kullanıcıları, ödemeleri, premium abonelikleri ve sistem ayarlarını yönetebilmesi için tasarlanmış kapsamlı bir yönetim arayüzüdür.

---

## 🎯 **Ana Özellikler**

### **📊 İstatistikler ve Analitik**
- **Kullanıcı İstatistikleri**: Toplam kullanıcı, aktif kullanıcı, yeni kayıtlar
- **Premium İstatistikleri**: Plan bazlı kullanıcı dağılımı, gelir analizi
- **Fal İstatistikleri**: Kahve, tarot, rüya falı kullanım oranları
- **Ödeme İstatistikleri**: Günlük, haftalık, aylık gelir raporları

### **👥 Kullanıcı Yönetimi**
- **Kullanıcı Listesi**: Tüm kullanıcıları görüntüleme ve filtreleme
- **Premium Kullanıcılar**: Premium abonelik sahiplerini listeleme
- **Kullanıcı Detayları**: Bireysel kullanıcı bilgileri ve geçmişi
- **PDF Raporları**: Kullanıcı verilerini PDF formatında indirme

### **💎 Premium Abonelik Yönetimi**
- **Premium Kullanıcı Listesi**: Plan bazlı kullanıcı dağılımı
- **Abonelik İstatistikleri**: Aktif, süresi dolmuş, iptal edilmiş abonelikler
- **Hediye Abonelik**: Kullanıcılara ücretsiz premium plan hediye etme
- **Abonelik İptal**: Kullanıcı aboneliklerini iptal etme
- **Premium PDF Raporu**: Premium kullanıcı verilerini PDF olarak indirme

### **🔧 Sistem Yönetimi**
- **Log Yönetimi**: Sistem loglarını görüntüleme ve filtreleme
- **Ayar Yönetimi**: Bot ayarlarını değiştirme
- **Prompt Yönetimi**: AI promptlarını düzenleme
- **Veritabanı Yönetimi**: Veritabanı işlemleri ve bakım

---

## 🚀 **Admin Panel Erişimi**

### **Giriş Yöntemi**
```bash
# Bot üzerinden admin paneline erişim
/admin - Admin panelini açar
```

### **Yetki Kontrolü**
- Sadece `ADMIN_ID` olarak tanımlanan kullanıcılar erişebilir
- `.env` dosyasında `ADMIN_ID=your_telegram_user_id` tanımlanmalı

---

## 📊 **İstatistikler Menüsü**

### **Genel İstatistikler**
```
📊 BOT İSTATİSTİKLERİ

👥 Toplam Kullanıcı: 1,234
📈 Aktif Kullanıcı (24s): 89
🆕 Yeni Kayıtlar (Bugün): 12
💎 Premium Kullanıcılar: 156

💰 GELİR İSTATİSTİKLERİ
💵 Toplam Gelir: 45,670 ⭐
📅 Bugünkü Gelir: 890 ⭐
📊 Bu Ay Gelir: 12,450 ⭐

🔮 FAL İSTATİSTİKLERİ
☕ Kahve Falı: 2,340
🎴 Tarot: 1,890
💭 Rüya: 1,567
```

### **Premium İstatistikler**
```
💎 PREMIUM İSTATİSTİKLERİ

📊 Plan Dağılımı:
🆓 Ücretsiz: 1,078 kullanıcı
💎 Temel: 89 kullanıcı
⭐ Premium: 45 kullanıcı
👑 VIP: 22 kullanıcı

💰 Gelir Dağılımı:
💎 Temel Plan: 44,500 ⭐
⭐ Premium Plan: 45,000 ⭐
👑 VIP Plan: 44,000 ⭐
```

---

## 👥 **Kullanıcı Yönetimi**

### **Kullanıcı Listesi**
```
👥 KULLANICI LİSTESİ (Sayfa 1/5)

👤 @username1 - Premium Plan
   📅 Kayıt: 15.07.2024
   💰 Toplam Harcama: 1,500 ⭐
   📊 Fal Sayısı: 23

👤 @username2 - Temel Plan
   📅 Kayıt: 20.07.2024
   💰 Toplam Harcama: 500 ⭐
   📊 Fal Sayısı: 15

[◀️ Önceki] [Sonraki ▶️] [🏠 Ana Menü]
```

### **Kullanıcı Detayları**
```
👤 KULLANICI DETAYLARI

📱 Kullanıcı: @username
🆔 ID: 123456789
🌐 Dil: Türkçe
💎 Plan: Premium Plan
📅 Abonelik Bitiş: 15.08.2024
💰 Toplam Harcama: 1,500 ⭐

📊 KULLANIM İSTATİSTİKLERİ
☕ Kahve Falı: 8 kez
🎴 Tarot: 6 kez
💭 Rüya: 9 kez
📅 Günlük Burç: 15 kez

[📱 PDF İndir] [🔙 Geri]
```

---

## 💎 **Premium Yönetimi**

### **Premium Kullanıcı Listesi**
```
💎 PREMIUM KULLANICILAR

👑 VIP Plan (22 kullanıcı):
👤 @vip_user1 - 15.08.2024'e kadar
👤 @vip_user2 - 20.08.2024'e kadar

⭐ Premium Plan (45 kullanıcı):
👤 @premium_user1 - 10.08.2024'e kadar
👤 @premium_user2 - 12.08.2024'e kadar

💎 Temel Plan (89 kullanıcı):
👤 @basic_user1 - 05.08.2024'e kadar
👤 @basic_user2 - 08.08.2024'e kadar

[📊 İstatistikler] [🎁 Hediye Abonelik] [❌ İptal Et]
```

### **Hediye Abonelik**
```
🎁 HEDİYE ABONELİK

Kullanıcı ID'sini girin:
(Örnek: 123456789)

Plan Seçin:
💎 Temel Plan (500 ⭐)
⭐ Premium Plan (1000 ⭐)
👑 VIP Plan (2000 ⭐)

Süre Seçin:
📅 1 Ay
📅 3 Ay
📅 6 Ay
📅 1 Yıl

[✅ Onayla] [🔙 Geri]
```

### **Abonelik İptal**
```
❌ ABONELİK İPTAL

Kullanıcı ID'sini girin:
(Örnek: 123456789)

⚠️ DİKKAT: Bu işlem geri alınamaz!

Kullanıcı: @username
Mevcut Plan: Premium Plan
Bitiş Tarihi: 15.08.2024

[❌ İptal Et] [🔙 Geri]
```

---

## 🔧 **Sistem Yönetimi**

### **Log Yönetimi**
```
📋 SİSTEM LOGLARI (Son 50)

🕐 16:30:15 - Premium abonelik aktifleştirildi: @user123
🕐 16:28:42 - Yeni kullanıcı kaydı: @newuser456
🕐 16:25:18 - Ödeme başarılı: 1000 ⭐ - @premium_user
🕐 16:22:33 - Kahve falı tamamlandı: @coffee_user
🕐 16:20:15 - Tarot kartı çekildi: @tarot_user

[📥 Daha Fazla] [🔙 Geri]
```

### **Ayar Yönetimi**
```
⚙️ SİSTEM AYARLARI

🔮 Günlük Kart Saati: 09:00
📊 Haftalık Rapor Günü: Pazartesi
🌙 Ay Bildirimleri: Aktif
💬 Chatbot Modu: VIP Only
📱 Dil Varsayılan: Türkçe

[✏️ Düzenle] [🔙 Geri]
```

---

## 📱 **PDF Raporları**

### **Kullanıcı PDF Raporu**
```
📱 PDF RAPORU İNDİR

Rapor Türü:
👥 Tüm Kullanıcılar
💎 Premium Kullanıcılar
📊 Aktif Kullanıcılar
📅 Yeni Kayıtlar (Son 30 gün)

Format:
📄 PDF
📊 Excel (CSV)

[📥 İndir] [🔙 Geri]
```

### **Premium PDF Raporu**
```
💎 PREMIUM PDF RAPORU

📊 Plan Bazlı Rapor:
🆓 Ücretsiz Kullanıcılar
💎 Temel Plan Kullanıcıları
⭐ Premium Plan Kullanıcıları
👑 VIP Plan Kullanıcıları

📈 Gelir Raporu:
💰 Günlük Gelir
📅 Haftalık Gelir
📊 Aylık Gelir

[📥 İndir] [🔙 Geri]
```

---

## 🔐 **Güvenlik ve Yetkilendirme**

### **Admin Yetki Kontrolü**
```python
# Admin kontrolü
if update.effective_user.id != ADMIN_ID:
    await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
    return
```

### **İşlem Logları**
- Tüm admin işlemleri loglanır
- Kullanıcı değişiklikleri kaydedilir
- Ödeme işlemleri takip edilir

---

## 📊 **Veritabanı Şeması**

### **Admin Panel Tabloları**
```sql
-- Kullanıcı tablosu (genişletilmiş)
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT DEFAULT 'tr',
    premium_plan TEXT DEFAULT 'free',
    premium_expires_at TIMESTAMP,
    total_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Premium abonelikler
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    plan_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP,
    total_paid INTEGER
);

-- Ödeme işlemleri
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    plan_id VARCHAR(20),
    amount INTEGER,
    currency VARCHAR(10) DEFAULT 'XTR',
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚨 **Hata Yönetimi**

### **Yaygın Hatalar ve Çözümleri**

#### **1. "Admin Yetkisi Yok" Hatası**
```
❌ Bu komutu kullanma yetkiniz yok!
```
**Çözüm**: `.env` dosyasında `ADMIN_ID` değerini kontrol edin

#### **2. "Kullanıcı Bulunamadı" Hatası**
```
❌ Kullanıcı bulunamadı: 123456789
```
**Çözüm**: Kullanıcı ID'sinin doğru olduğundan emin olun

#### **3. "PDF Oluşturulamadı" Hatası**
```
❌ PDF raporu oluşturulamadı
```
**Çözüm**: FPDF2 kütüphanesinin yüklü olduğunu kontrol edin

---

## 📈 **Performans Optimizasyonu**

### **Veritabanı İndeksleri**
```sql
-- Performans için gerekli indeksler
CREATE INDEX idx_users_premium_plan ON users(premium_plan);
CREATE INDEX idx_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_payments_created_at ON payment_transactions(created_at);
```

### **Önbellek Stratejisi**
- Kullanıcı listesi önbellekleme
- İstatistik hesaplamaları önbellekleme
- PDF raporları önbellekleme

---

## 🔄 **Güncelleme ve Bakım**

### **Düzenli Bakım İşlemleri**
1. **Günlük**: Log temizleme, istatistik güncelleme
2. **Haftalık**: Premium abonelik kontrolü, süresi dolmuş abonelikler
3. **Aylık**: Veritabanı optimizasyonu, yedekleme

### **Güncelleme Kontrol Listesi**
- [ ] Yeni özellikler test edildi
- [ ] Veritabanı şeması güncellendi
- [ ] Admin panel özellikleri kontrol edildi
- [ ] Güvenlik testleri yapıldı
- [ ] Performans testleri tamamlandı

---

## 📞 **Destek ve İletişim**

### **Teknik Destek**
- **Dokümantasyon**: Bu dosya ve README.md
- **Hata Raporlama**: GitHub Issues
- **Geliştirici**: Bot yöneticisi

### **Acil Durumlar**
- **Sistem Çökmesi**: Logları kontrol edin
- **Veri Kaybı**: Yedeklerden geri yükleme
- **Güvenlik İhlali**: Admin yetkilerini kontrol edin

---

**Son Güncelleme**: 29 Temmuz 2025  
**Versiyon**: 3.1.1  
**Dokümantasyon**: Admin Panel Kullanım Kılavuzu 
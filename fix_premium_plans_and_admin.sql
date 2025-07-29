-- Premium plan fiyatlarını düzelt
UPDATE premium_plans 
SET price_stars = 1000 
WHERE plan_id = 'premium';

UPDATE premium_plans 
SET price_stars = 2000 
WHERE plan_id = 'vip';

-- Premium plan özelliklerini güncelle
UPDATE premium_plans 
SET features = '["♾️ Sınırsız fal (Kahve, Tarot, Rüya)", "📊 Haftalık burç raporu", "🔮 Gelişmiş astroloji analizi", "💫 Doğum haritası yorumu", "🌙 Ay takvimi özellikleri", "💬 Gelişmiş chatbot", "🎯 Kişiselleştirilmiş öneriler", "📈 Detaylı fal geçmişi", "🔔 Özel bildirimler", "📅 Aylık burç yorumu", "🌍 Gezegen geçişleri", "📋 PDF raporları"]',
    features_en = '["♾️ Unlimited readings (Coffee, Tarot, Dream)", "📊 Weekly horoscope report", "🔮 Advanced astrology analysis", "💫 Birth chart interpretation", "🌙 Moon calendar features", "💬 Advanced chatbot", "🎯 Personalized recommendations", "📈 Detailed reading history", "🔔 Special notifications", "📅 Monthly horoscope", "🌍 Planetary transits", "📋 PDF reports"]'
WHERE plan_id = 'premium';

UPDATE premium_plans 
SET features = '["♾️ Sınırsız fal (Kahve, Tarot, Rüya)", "📊 Haftalık burç raporu", "🔮 Gelişmiş astroloji analizi", "💫 Doğum haritası yorumu", "🌙 Ay takvimi özellikleri", "💬 Gelişmiş chatbot", "🎯 Kişiselleştirilmiş öneriler", "📈 Detaylı fal geçmişi", "🔔 Özel bildirimler", "📅 Aylık burç yorumu", "🌍 Gezegen geçişleri", "📋 PDF raporları", "🤖 7/24 Astroloji Chatbot", "👥 Sosyal özellikler", "⭐ Öncelikli destek", "👨‍💼 Kişisel danışman"]',
    features_en = '["♾️ Unlimited readings (Coffee, Tarot, Dream)", "📊 Weekly horoscope report", "🔮 Advanced astrology analysis", "💫 Birth chart interpretation", "🌙 Moon calendar features", "💬 Advanced chatbot", "🎯 Personalized recommendations", "📈 Detailed reading history", "🔔 Special notifications", "📅 Monthly horoscope", "🌍 Planetary transits", "📋 PDF reports", "🤖 24/7 Astrology Chatbot", "👥 Social features", "⭐ Priority support", "👨‍💼 Personal consultant"]'
WHERE plan_id = 'vip';

-- Free plan özelliklerini güncelle (5 ücretsiz fal)
UPDATE premium_plans 
SET features = '["☕ 5 ücretsiz fal (Kahve, Tarot, Rüya)", "♈ Günlük burç yorumu", "🔮 Temel astroloji özellikleri", "📱 Temel chatbot desteği", "🎁 Referral bonusları"]',
    features_en = '["☕ 5 free readings (Coffee, Tarot, Dream)", "♈ Daily horoscope", "🔮 Basic astrology features", "📱 Basic chatbot support", "🎁 Referral bonuses"]'
WHERE plan_id = 'free';

-- Güncel planları kontrol et
SELECT plan_id, name, price, price_stars, features FROM premium_plans ORDER BY price; 
-- Fal Gram Bot - Complete Database Setup
-- Tüm tabloları temizleyip yeniden oluşturur ve varsayılan verileri ekler

-- ====================================
-- 1. MEVCUT TABLOLARI TEMİZLE
-- ====================================
DROP TABLE IF EXISTS weekly_reports CASCADE;
DROP TABLE IF EXISTS user_connections CASCADE;
DROP TABLE IF EXISTS moon_notifications CASCADE;
DROP TABLE IF EXISTS chatbot_history CASCADE;
DROP TABLE IF EXISTS premium_subscriptions CASCADE;
DROP TABLE IF EXISTS prompts CASCADE;
DROP TABLE IF EXISTS config CASCADE;
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ====================================
-- 2. YENİ TABLOLARI OLUŞTUR
-- ====================================

-- USERS TABLOSU (Primary)
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT DEFAULT 'tr',
    readings_count INTEGER DEFAULT 0,
    daily_subscribed BOOLEAN DEFAULT FALSE,
    referred_count INTEGER DEFAULT 0,
    referral_earnings INTEGER DEFAULT 0,
    bonus_readings INTEGER DEFAULT 0,
    state TEXT DEFAULT 'idle',
    premium_plan TEXT DEFAULT 'free',
    premium_expires_at TIMESTAMP,
    astro_subscribed BOOLEAN DEFAULT FALSE,
    moon_notifications BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- LOGS TABLOSU
CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- CONFIG TABLOSU
CREATE TABLE config (
    id BIGSERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PROMPTS TABLOSU
CREATE TABLE prompts (
    id BIGSERIAL PRIMARY KEY,
    prompt_type TEXT NOT NULL,
    language TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prompt_type, language)
);

-- Premium abonelik geçmişi tablosu
CREATE TABLE premium_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    plan_type TEXT NOT NULL,
    stars_paid INTEGER NOT NULL,
    starts_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Astroloji chatbot geçmişi tablosu
CREATE TABLE chatbot_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ay bildirimleri tablosu
CREATE TABLE moon_notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    notification_type TEXT NOT NULL,
    moon_phase TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sosyal özellikler için arkadaşlık tablosu
CREATE TABLE user_connections (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    friend_user_id BIGINT NOT NULL,
    compatibility_score INTEGER,
    connection_type TEXT DEFAULT 'friend',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, friend_user_id)
);

-- Haftalık raporlar tablosu
CREATE TABLE weekly_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    week_start DATE NOT NULL,
    report_content TEXT NOT NULL,
    report_type TEXT DEFAULT 'astrology',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, week_start, report_type)
);

-- ====================================
-- 3. FOREIGN KEY CONSTRAINT'LERİ EKLE
-- ====================================

ALTER TABLE premium_subscriptions 
ADD CONSTRAINT fk_premium_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE chatbot_history 
ADD CONSTRAINT fk_chatbot_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE moon_notifications 
ADD CONSTRAINT fk_moon_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_connections 
ADD CONSTRAINT fk_connection_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_connections 
ADD CONSTRAINT fk_connection_friend_user_id 
FOREIGN KEY (friend_user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE weekly_reports 
ADD CONSTRAINT fk_reports_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ====================================
-- 4. İNDEKSLER OLUŞTUR
-- ====================================

CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_premium_plan ON users(premium_plan);
CREATE INDEX idx_premium_subscriptions_user_id ON premium_subscriptions(user_id);
CREATE INDEX idx_premium_subscriptions_active ON premium_subscriptions(active);
CREATE INDEX idx_chatbot_history_user_id ON chatbot_history(user_id);
CREATE INDEX idx_moon_notifications_user_id ON moon_notifications(user_id);
CREATE INDEX idx_user_connections_user_id ON user_connections(user_id);
CREATE INDEX idx_weekly_reports_user_id ON weekly_reports(user_id);
CREATE INDEX idx_logs_created_at ON logs(created_at);

-- ====================================
-- 5. TRİGGERLAR OLUŞTUR
-- ====================================

-- Trigger fonksiyonu: updated_at otomatik güncellemesi
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggerlar oluştur
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_config_updated_at BEFORE UPDATE ON config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====================================
-- 6. VARSAYILAN VERİLER
-- ====================================

-- Konfigürasyon verileri
INSERT INTO config (key, value) VALUES 
    ('daily_card_hour', '8'),
    ('daily_card_minute', '0'),
    ('premium_discount', '0'),
    ('chatbot_enabled', 'true'),
    ('moon_notifications_enabled', 'true'),
    ('tarot_cards', '["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]')
ON CONFLICT (key) DO NOTHING;

-- PROMPT'LARI EKLE
-- Türkçe prompts
INSERT INTO prompts (prompt_type, language, content) VALUES 
('coffee', 'tr', 'Sen bir profesyonel kahve falcısısın. Kullanıcının gönderdiği kahve fincanı fotoğrafına bakarak Türkçe fal yorumu yapacaksın. Kısa, pozitif ve umut verici bir yorum yaz. 3-4 cümle olsun.'),
('tarot', 'tr', 'Sen bir tarot uzmanısın. Bu kart ile ilgili Türkçe bir yorum yap. Pozitif ve rehberlik edici bir ton kullan. 3-4 cümle olsun.'),
('dream', 'tr', 'Sen bir rüya yorumcususun. Kullanıcının anlattığı rüyayı Türkçe olarak yorumla. Psikolojik ve sembolik anlamları da dahil et. 3-4 cümle olsun.'),
('birth_chart', 'tr', 'Sen bir profesyonel astrologsun. Verilen doğum bilgilerine göre Türkçe doğum haritası analizi yap. Kişilik özellikleri, güçlü yönler ve potansiyeller hakkında bilgi ver. 4-5 cümle olsun.'),
('daily_horoscope', 'tr', 'Sen bir astrologsun. Bu burç için bugünün Türkçe günlük yorumunu yap. Aşk, kariyer ve sağlık konularında kısa tavsiyelerde bulun. 3-4 cümle olsun.'),
('compatibility', 'tr', 'Sen bir astrologsun. Bu iki burç arasındaki uyumluluğu Türkçe olarak analiz et. Güçlü yönler ve dikkat edilmesi gereken noktalar hakkında bilgi ver. 3-4 cümle olsun.')
ON CONFLICT (prompt_type, language) DO NOTHING;

-- İngilizce prompts
INSERT INTO prompts (prompt_type, language, content) VALUES 
('coffee', 'en', 'You are a professional coffee fortune teller. Look at the coffee cup photo sent by the user and make an English fortune interpretation. Write a short, positive and hopeful comment. Make it 3-4 sentences.'),
('tarot', 'en', 'You are a tarot expert. Make an English comment about this card. Use a positive and guiding tone. Make it 3-4 sentences.'),
('dream', 'en', 'You are a dream interpreter. Interpret the dream described by the user in English. Include psychological and symbolic meanings. Make it 3-4 sentences.'),
('birth_chart', 'en', 'You are a professional astrologer. Make an English birth chart analysis based on the given birth information. Provide information about personality traits, strengths and potentials. Make it 4-5 sentences.'),
('daily_horoscope', 'en', 'You are an astrologer. Make todays English daily interpretation for this zodiac sign. Give brief advice on love, career and health topics. Make it 3-4 sentences.'),
('compatibility', 'en', 'You are an astrologer. Analyze the compatibility between these two zodiac signs in English. Provide information about strengths and points to be careful about. Make it 3-4 sentences.')
ON CONFLICT (prompt_type, language) DO NOTHING;

-- Diğer diller için temel prompts
-- Español
INSERT INTO prompts (prompt_type, language, content) VALUES 
('coffee', 'es', 'Eres un adivino profesional del café. Mira la foto de la taza de café enviada por el usuario y haz una interpretación de la fortuna en español. Escribe un comentario corto, positivo y esperanzador. Que sean 3-4 frases.'),
('tarot', 'es', 'Eres un experto en tarot. Haz un comentario en español sobre esta carta. Usa un tono positivo y orientador. Que sean 3-4 frases.'),
('dream', 'es', 'Eres un intérprete de sueños. Interpreta el sueño descrito por el usuario en español. Incluye significados psicológicos y simbólicos. Que sean 3-4 frases.')
ON CONFLICT (prompt_type, language) DO NOTHING;

-- Français
INSERT INTO prompts (prompt_type, language, content) VALUES 
('coffee', 'fr', 'Vous êtes un diseuse de bonne aventure professionnelle du café. Regardez la photo de la tasse de café envoyée par l utilisateur et faites une interprétation de fortune en français. Écrivez un commentaire court, positif et plein d espoir. Que ce soit 3-4 phrases.'),
('tarot', 'fr', 'Vous êtes un expert en tarot. Faites un commentaire en français sur cette carte. Utilisez un ton positif et guide. Que ce soit 3-4 phrases.'),
('dream', 'fr', 'Vous êtes un interprète de rêves. Interprétez le rêve décrit par l utilisateur en français. Incluez les significations psychologiques et symboliques. Que ce soit 3-4 phrases.')
ON CONFLICT (prompt_type, language) DO NOTHING;

-- Русский
INSERT INTO prompts (prompt_type, language, content) VALUES 
('coffee', 'ru', 'Вы профессиональная гадалка на кофе. Посмотрите на фото кофейной чашки, отправленное пользователем, и сделайте русскую интерпретацию удачи. Напишите короткий, позитивный и обнадеживающий комментарий. Пусть это будет 3-4 предложения.'),
('tarot', 'ru', 'Вы эксперт по таро. Сделайте русский комментарий об этой карте. Используйте позитивный и направляющий тон. Пусть это будет 3-4 предложения.'),
('dream', 'ru', 'Вы толкователь снов. Истолкуйте сон, описанный пользователем на русском языке. Включите психологические и символические значения. Пусть это будет 3-4 предложения.')
ON CONFLICT (prompt_type, language) DO NOTHING;

-- BAŞARI MESAJI
SELECT 'Database setup completed successfully!' as status; 
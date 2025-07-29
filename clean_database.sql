-- Fal Gram Bot - Database Cleanup and Recreate
-- Mevcut tabloları sil ve yeniden oluştur

-- Önce mevcut tabloları sil (foreign key constraint'ler nedeniyle ters sırada)
DROP TABLE IF EXISTS weekly_reports CASCADE;
DROP TABLE IF EXISTS user_connections CASCADE;
DROP TABLE IF EXISTS moon_notifications CASCADE;
DROP TABLE IF EXISTS chatbot_history CASCADE;
DROP TABLE IF EXISTS premium_subscriptions CASCADE;
DROP TABLE IF EXISTS prompts CASCADE;
DROP TABLE IF EXISTS config CASCADE;
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Trigger fonksiyonunu da sil
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Şimdi database_setup.sql içeriğini çalıştır
-- USERS TABLOSUNU OLUŞTUR
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

-- FOREIGN KEY CONSTRAINT'LERİ EKLE
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

-- İndeksler oluştur
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_premium_plan ON users(premium_plan);
CREATE INDEX idx_premium_subscriptions_user_id ON premium_subscriptions(user_id);
CREATE INDEX idx_premium_subscriptions_active ON premium_subscriptions(active);
CREATE INDEX idx_chatbot_history_user_id ON chatbot_history(user_id);
CREATE INDEX idx_moon_notifications_user_id ON moon_notifications(user_id);
CREATE INDEX idx_user_connections_user_id ON user_connections(user_id);
CREATE INDEX idx_weekly_reports_user_id ON weekly_reports(user_id);
CREATE INDEX idx_logs_created_at ON logs(created_at);

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

-- Varsayılan konfigürasyon verileri
INSERT INTO config (key, value) VALUES 
    ('daily_card_hour', '8'),
    ('daily_card_minute', '0'),
    ('premium_discount', '0'),
    ('chatbot_enabled', 'true'),
    ('moon_notifications_enabled', 'true')
ON CONFLICT (key) DO NOTHING; 
-- Fix Tarot Cards Configuration
-- Bu script config tablosuna tarot kartları konfigürasyonunu ekler

-- 1. Config tablosunu kontrol et
CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Tarot kartları konfigürasyonunu ekle (JSON formatında)
INSERT INTO config (key, value) VALUES
('tarot_cards', '[
    "The Fool",
    "The Magician", 
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World"
]')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- 3. Diğer gerekli konfigürasyonları da ekle
INSERT INTO config (key, value) VALUES
('daily_card_hour', '9'),
('daily_card_minute', '0')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- 4. Konfigürasyonları kontrol et
SELECT 'Tarot cards configuration added successfully' as status;
SELECT key, value FROM config WHERE key IN ('tarot_cards', 'daily_card_hour', 'daily_card_minute'); 
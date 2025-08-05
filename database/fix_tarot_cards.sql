-- Fix Tarot Cards Table
-- Bu script eksik tarot_cards tablosunu oluşturur

-- 1. Tarot kartları tablosunu oluştur
CREATE TABLE IF NOT EXISTS tarot_cards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Temel tarot kartlarını ekle
INSERT INTO tarot_cards (name, description) VALUES
('The Fool', 'Yeni başlangıçlar, masumiyet, spontanlık'),
('The Magician', 'Yaratıcılık, beceri, güç'),
('The High Priestess', 'Sezgi, gizem, içsel bilgelik'),
('The Empress', 'Bereket, yaratıcılık, doğurganlık'),
('The Emperor', 'Güç, otorite, liderlik'),
('The Hierophant', 'Gelenek, eğitim, manevi rehberlik'),
('The Lovers', 'Aşk, uyum, seçim'),
('The Chariot', 'Zafer, kararlılık, kontrol'),
('Strength', 'Güç, cesaret, sabır'),
('The Hermit', 'Yalnızlık, içsel arayış, rehberlik'),
('Wheel of Fortune', 'Değişim, şans, döngüler'),
('Justice', 'Adalet, denge, hakikat'),
('The Hanged Man', 'Fedakarlık, yeni bakış açısı'),
('Death', 'Dönüşüm, son, yeniden doğuş'),
('Temperance', 'Denge, ılımlılık, sabır'),
('The Devil', 'Bağımlılık, materyalizm, karanlık'),
('The Tower', 'Ani değişim, yıkım, aydınlanma'),
('The Star', 'Umut, ilham, manevi rehberlik'),
('The Moon', 'Sezgi, yanılsama, gizem'),
('The Sun', 'Neşe, başarı, enerji'),
('Judgement', 'Yeniden doğuş, çağrı, dönüşüm'),
('The World', 'Tamamlanma, başarı, bütünlük')
ON CONFLICT (name) DO NOTHING;

-- 3. Tabloyu kontrol et
SELECT 'Tarot cards table created successfully' as status;
SELECT COUNT(*) as card_count FROM tarot_cards;
SELECT name FROM tarot_cards LIMIT 5; 
-- Fix Prompts Table Structure
-- Bu script prompts tablosunu düzeltir ve eksik prompt'ları ekler

-- 1. Mevcut tabloyu kontrol et ve gerekirse yeniden oluştur
DROP TABLE IF EXISTS prompts;

-- 2. Prompts tablosunu doğru yapıda oluştur
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    prompt_type VARCHAR(50) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'tr',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prompt_type, language)
);

-- 3. Temel prompt'ları ekle
INSERT INTO prompts (prompt_type, language, content) VALUES
-- Tarot Prompt (Türkçe)
('tarot', 'tr', 'Sen deneyimli bir tarot yorumcususun. {card} kartını çeken {username} için kapsamlı bir yorum oluştur.

**Kartın Genel Anlamı:** {card} kartının temel sembolizmini ve enerjisini açıkla.
**Kişisel Mesaj:** Bu kartın {username}''in hayatındaki mevcut duruma nasıl yansıdığını yorumla.
**Gelecek Öngörüsü:** Kartın gösterdiği enerjiye dayanarak yakın gelecek için bir öngörüde bulun.
**Pratik Tavsiye:** {username}''e bu kartın enerjisini en iyi nasıl kullanabileceğine dair somut öneriler ver.

**Dil Tonu:** Mistik, bilge ve motive edici.
**Kısıtlamalar:** 120-150 kelime.'),

-- Rüya Prompt (Türkçe)
('dream', 'tr', 'Sen deneyimli bir rüya yorumcususun. {username} için rüya yorumu yap.

Rüyada gördüğü şeyleri başta belirt. Örneğin: "Rüyanda kelebek görmen..."

Sonra bu sembollerin anlamını açıkla ve {username} için kişisel yorum yap.

150-200 kelime arası yaz.'),

-- Kahve Falı Prompt (Türkçe)
('coffee', 'tr', 'Sen deneyimli bir kahve falı yorumcususun. {username}''in gönderdiği fincan fotoğrafını analiz et.

**Görsel Analiz:** Fincandaki şekilleri ve sembolleri detaylandır.
**Kişisel Yorum:** Bu sembollerin {username}''in hayatındaki anlamını açıkla.
**Gelecek Öngörüsü:** Gördüğün şekillere dayanarak gelecek için öngörülerde bulun.
**Pratik Tavsiye:** {username}''e hayatında dikkat etmesi gereken noktaları belirt.

**Dil Tonu:** Samimi, bilge ve motive edici.
**Kısıtlamalar:** 150-200 kelime.'),

-- Günlük Burç Prompt (Türkçe)
('daily_horoscope', 'tr', 'Sen deneyimli bir astrologsun. {sign} burcu için bugünün (tarih: {date}) günlük burç yorumunu yaz.

**Genel Enerji:** Bugünün genel enerjisini ve burç üzerindeki etkisini açıkla.
**Aşk & İlişkiler:** Bugün aşk ve ilişkiler alanında neler olabilir?
**Kariyer & Para:** İş ve finansal konularda dikkat edilmesi gerekenler.
**Sağlık & Enerji:** Fiziksel ve zihinsel sağlık için öneriler.
**Şanslı Sayı:** Bugünün şanslı sayısı ve rengi.

**Dil Tonu:** Pozitif, motive edici ve bilgilendirici.
**Kısıtlamalar:** 100-120 kelime.'),

-- Tarot Prompt (İngilizce)
('tarot', 'en', 'You are an experienced tarot reader. Create a comprehensive interpretation for {username} who drew the {card} card.

**Card''s General Meaning:** Explain the basic symbolism and energy of the {card} card.
**Personal Message:** Interpret how this card reflects in {username}''s current life situation.
**Future Prediction:** Make a prediction for the near future based on the energy shown by the card.
**Practical Advice:** Give {username} concrete suggestions on how to best use this card''s energy.

**Tone:** Mystical, wise and motivating.
**Limitations:** 120-150 words.'),

-- Rüya Prompt (İngilizce)
('dream', 'en', 'You are an experienced dream interpreter. Interpret the dream for {username}.

First mention what they saw in their dream. For example: "Seeing a butterfly in your dream..."

Then explain the meaning of these symbols and make a personal interpretation for {username}.

Write 150-200 words.'),

-- Kahve Falı Prompt (İngilizce)
('coffee', 'en', 'You are an experienced coffee fortune teller. Analyze the cup photo sent by {username}.

**Visual Analysis:** Detail the shapes and symbols in the cup.
**Personal Interpretation:** Explain what these symbols mean in {username}''s life.
**Future Prediction:** Make predictions for the future based on the shapes you see.
**Practical Advice:** Point out what {username} should pay attention to in their life.

**Tone:** Friendly, wise and motivating.
**Limitations:** 150-200 words.'),

-- Günlük Burç Prompt (İngilizce)
('daily_horoscope', 'en', 'You are an experienced astrologer. Write today''s (date: {date}) daily horoscope for {sign}.

**General Energy:** Explain today''s general energy and its effect on the sign.
**Love & Relationships:** What might happen in love and relationships today?
**Career & Money:** Things to pay attention to in work and financial matters.
**Health & Energy:** Suggestions for physical and mental health.
**Lucky Number:** Today''s lucky number and color.

**Tone:** Positive, motivating and informative.
**Limitations:** 100-120 words.');

-- 4. Tarot kartları tablosunu da kontrol et
CREATE TABLE IF NOT EXISTS tarot_cards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Temel tarot kartlarını ekle (eğer yoksa)
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

-- 6. Tabloları kontrol et
SELECT 'Prompts table created successfully' as status;
SELECT COUNT(*) as prompt_count FROM prompts;
SELECT COUNT(*) as tarot_card_count FROM tarot_cards; 
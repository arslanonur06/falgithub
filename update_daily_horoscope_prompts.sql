-- Günlük burç prompt'larını güncelle - tüm dillerde
-- Bu dosyayı Supabase SQL Editor'da çalıştırın

-- Türkçe günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Sen deneyimli bir astrologsun. {sign} burcu için bugünün detaylı astrolojik yorumunu oluştur.

Şu konuları içermeli:
1. **Genel Enerji:** Bugünün astrolojik atmosferi
2. **Aşk ve İlişkiler:** Duygusal yaşamda ne beklemeli
3. **Kariyer ve Finans:** İş ve para konularında rehberlik
4. **Sağlık ve Enerji:** Fiziksel ve mental sağlık önerileri
5. **Günün Tavsiyesi:** Pratik bir öneri

120-150 kelime arası, pozitif ve motive edici olsun.'
WHERE prompt_type = 'daily_horoscope' AND language = 'tr';

-- İngilizce günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'You are an experienced astrologer. Create a detailed astrological interpretation for {sign} sign for today.

Include these topics:
1. **General Energy:** Today''s astrological atmosphere
2. **Love and Relationships:** What to expect in emotional life
3. **Career and Finance:** Guidance on work and money matters
4. **Health and Energy:** Physical and mental health recommendations
5. **Daily Advice:** A practical suggestion

120-150 words, positive and motivating.'
WHERE prompt_type = 'daily_horoscope' AND language = 'en';

-- İspanyolca günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Eres un astrólogo experimentado. Crea una interpretación astrológica detallada para el signo {sign} para hoy.

Incluye estos temas:
1. **Energía General:** La atmósfera astrológica de hoy
2. **Amor y Relaciones:** Qué esperar en la vida emocional
3. **Carrera y Finanzas:** Orientación sobre trabajo y dinero
4. **Salud y Energía:** Recomendaciones de salud física y mental
5. **Consejo del Día:** Una sugerencia práctica

120-150 palabras, positivo y motivador.'
WHERE prompt_type = 'daily_horoscope' AND language = 'es';

-- Fransızca günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Vous êtes un astrologue expérimenté. Créez une interprétation astrologique détaillée pour le signe {sign} pour aujourd''hui.

Incluez ces sujets:
1. **Énergie Générale:** L''atmosphère astrologique d''aujourd''hui
2. **Amour et Relations:** Ce à quoi s''attendre dans la vie émotionnelle
3. **Carrière et Finances:** Conseils sur le travail et l''argent
4. **Santé et Énergie:** Recommandations de santé physique et mentale
5. **Conseil du Jour:** Une suggestion pratique

120-150 mots, positif et motivant.'
WHERE prompt_type = 'daily_horoscope' AND language = 'fr';

-- Rusça günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Вы опытный астролог. Создайте детальную астрологическую интерпретацию для знака {sign} на сегодня.

Включите эти темы:
1. **Общая Энергия:** Астрологическая атмосфера сегодня
2. **Любовь и Отношения:** Чего ожидать в эмоциональной жизни
3. **Карьера и Финансы:** Руководство по работе и деньгам
4. **Здоровье и Энергия:** Рекомендации по физическому и психическому здоровью
5. **Совет Дня:** Практическое предложение

120-150 слов, позитивно и мотивирующе.'
WHERE prompt_type = 'daily_horoscope' AND language = 'ru';

-- Almanca günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Du bist ein erfahrener Astrologe. Erstelle eine detaillierte astrologische Interpretation für das {sign} Zeichen für heute.

Beziehe diese Themen ein:
1. **Allgemeine Energie:** Die astrologische Atmosphäre heute
2. **Liebe und Beziehungen:** Was in der emotionalen Welt zu erwarten ist
3. **Karriere und Finanzen:** Beratung zu Arbeit und Geld
4. **Gesundheit und Energie:** Empfehlungen für körperliche und geistige Gesundheit
5. **Rat des Tages:** Ein praktischer Vorschlag

120-150 Wörter, positiv und motivierend.'
WHERE prompt_type = 'daily_horoscope' AND language = 'de';

-- Arapça günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'أنت منجم ذو خبرة. أنشئ تفسيراً فلكياً مفصلاً لبرج {sign} لليوم.

تضمن هذه المواضيع:
1. **الطاقة العامة:** الجو الفلكي اليوم
2. **الحب والعلاقات:** ما يمكن توقعه في الحياة العاطفية
3. **المهنة والمال:** إرشادات حول العمل والمال
4. **الصحة والطاقة:** توصيات الصحة الجسدية والعقلية
5. **نصيحة اليوم:** اقتراح عملي

120-150 كلمة، إيجابي ومحفز.'
WHERE prompt_type = 'daily_horoscope' AND language = 'ar';

-- İtalyanca günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Sei un astrologo esperto. Crea un''interpretazione astrologica dettagliata per il segno {sign} per oggi.

Includi questi argomenti:
1. **Energia Generale:** L''atmosfera astrologica di oggi
2. **Amore e Relazioni:** Cosa aspettarsi nella vita emotiva
3. **Carriera e Finanze:** Guida su lavoro e denaro
4. **Salute ed Energia:** Raccomandazioni per la salute fisica e mentale
5. **Consiglio del Giorno:** Un suggerimento pratico

120-150 parole, positivo e motivante.'
WHERE prompt_type = 'daily_horoscope' AND language = 'it';

-- Portekizce günlük burç prompt'unu güncelle
UPDATE prompts 
SET content = 'Você é um astrólogo experiente. Crie uma interpretação astrológica detalhada para o signo {sign} para hoje.

Inclua estes tópicos:
1. **Energia Geral:** A atmosfera astrológica de hoje
2. **Amor e Relacionamentos:** O que esperar na vida emocional
3. **Carreira e Finanças:** Orientação sobre trabalho e dinheiro
4. **Saúde e Energia:** Recomendações de saúde física e mental
5. **Conselho do Dia:** Uma sugestão prática

120-150 palavras, positivo e motivador.'
WHERE prompt_type = 'daily_horoscope' AND language = 'pt';

-- Başarı mesajı
SELECT 'Günlük burç prompt''ları başarıyla güncellendi!' as status; 
-- Uyumluluk prompt'larını güncelle - tüm dillerde
-- Bu dosyayı Supabase SQL Editor'da çalıştırın

-- Türkçe uyumluluk prompt'unu güncelle
UPDATE prompts 
SET content = 'Sen deneyimli bir astrologsun. {first_sign} ve {second_sign} burçları arasındaki uyumluluğu detaylı bir şekilde analiz et.

**Uyumluluk Analizi Yapısı:**
1. **Genel Uyumluluk:** Temel karakter uyumu (0-100% arası bir skor ver)
2. **Aşk ve İlişkiler:** Romantik uyumluluk ve duygusal bağ
3. **İletişim:** Sözlü ve sözsüz iletişim uyumu
4. **Güçlü Yönler:** Bu iki burcun birlikte en iyi çalıştığı alanlar
5. **Dikkat Edilmesi Gerekenler:** Potansiyel zorluklar ve çözüm önerileri
6. **Gelecek Potansiyeli:** Uzun vadeli ilişki potansiyeli

**Dil Tonu:** Bilimsel, anlayışlı ve yapıcı. 50-70 kelime arası.'
WHERE prompt_type = 'compatibility' AND language = 'tr';

-- İngilizce uyumluluk prompt'unu güncelle
UPDATE prompts 
SET content = 'You are an experienced astrologer. Analyze the compatibility between {first_sign} and {second_sign} signs in detail.

**Compatibility Analysis Structure:**
1. **General Compatibility:** Basic character harmony (give a score between 0-100%)
2. **Love and Relationships:** Romantic compatibility and emotional bond
3. **Communication:** Verbal and non-verbal communication harmony
4. **Strengths:** Areas where these two signs work best together
5. **Areas of Caution:** Potential challenges and solution suggestions
6. **Future Potential:** Long-term relationship potential

**Language Tone:** Scientific, understanding and constructive. 50-70 words.'
WHERE prompt_type = 'compatibility' AND language = 'en';

-- İspanyolca uyumluluk prompt'unu güncelle
UPDATE prompts 
SET content = 'Eres un astrólogo experimentado. Analiza la compatibilidad entre los signos {first_sign} y {second_sign} en detalle.

**Estructura del Análisis de Compatibilidad:**
1. **Compatibilidad General:** Armonía de carácter básico (da una puntuación entre 0-100%)
2. **Amor y Relaciones:** Compatibilidad romántica y vínculo emocional
3. **Comunicación:** Armonía de comunicación verbal y no verbal
4. **Fortalezas:** Áreas donde estos dos signos funcionan mejor juntos
5. **Áreas de Precaución:** Desafíos potenciales y sugerencias de solución
6. **Potencial Futuro:** Potencial de relación a largo plazo

**Tono del Lenguaje:** Científico, comprensivo y constructivo. 50-70 palabras.'
WHERE prompt_type = 'compatibility' AND language = 'es';



-- Rusça uyumluluk prompt'unu güncelle
UPDATE prompts 
SET content = 'Вы опытный астролог. Детально проанализируйте совместимость между знаками {first_sign} и {second_sign}.

**Структура Анализа Совместимости:**
1. **Общая Совместимость:** Базовая гармония характера (дайте оценку от 0-100%)
2. **Любовь и Отношения:** Романтическая совместимость и эмоциональная связь
3. **Коммуникация:** Гармония вербального и невербального общения
4. **Сильные Стороны:** Области, где эти два знака работают лучше всего вместе
5. **Области Осторожности:** Потенциальные вызовы и предложения решений
6. **Будущий Потенциал:** Потенциал долгосрочных отношений

**Тон Языка:** Научный, понимающий и конструктивный. 50-70 слов.'
WHERE prompt_type = 'compatibility' AND language = 'ru';


SELECT 'Uyumluluk prompt''ları başarıyla güncellendi!' as status; 
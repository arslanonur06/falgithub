#!/usr/bin/env python3
"""
🧪 Test Bot Features - Bot özelliklerini test eder
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_api():
    """Gemini API'sini test eder"""
    print("🔍 Gemini API Test")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY eksik")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with simple text prompt
        print("🔄 Basit metin prompt'u test ediliyor...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Merhaba, nasılsın?")
        
        if response and response.text:
            print(f"✅ Gemini API çalışıyor")
            print(f"   Yanıt: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API boş yanıt verdi")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API hatası: {e}")
        return False

async def test_supabase_prompts():
    """Supabase prompt'larını test eder"""
    print("\n🔍 Supabase Prompts Test")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        # Test specific prompts
        test_prompts = [
            ("tarot", "tr"),
            ("dream", "tr"),
            ("coffee_fortune", "tr")
        ]
        
        for prompt_type, lang in test_prompts:
            try:
                result = supabase.table("prompts").select("*").eq("prompt_type", prompt_type).eq("language", lang).limit(1).execute()
                
                if result.data:
                    prompt = result.data[0]
                    content_length = len(prompt.get('content', ''))
                    print(f"✅ {prompt_type} ({lang}): {content_length} karakter")
                else:
                    print(f"❌ {prompt_type} ({lang}): BULUNAMADI")
                    
            except Exception as e:
                print(f"❌ {prompt_type} ({lang}) hatası: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase test hatası: {e}")
        return False

async def test_tarot_cards():
    """Tarot kartlarını test eder"""
    print("\n🔍 Tarot Cards Test")
    print("=" * 50)
    
    try:
        from supabase import create_client
        import json
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        # Test tarot cards config
        result = supabase.table("config").select("*").eq("key", "tarot_cards").limit(1).execute()
        
        if result.data:
            config = result.data[0]
            tarot_cards_value = config.get('value', '[]')
            
            try:
                tarot_cards = json.loads(tarot_cards_value)
                if isinstance(tarot_cards, list) and len(tarot_cards) > 0:
                    print(f"✅ Tarot kartları mevcut: {len(tarot_cards)} kart")
                    print(f"   Örnek kart: {tarot_cards[0]}")
                    return True
                else:
                    print("❌ Tarot kartları boş")
                    return False
            except json.JSONDecodeError:
                print("❌ Tarot kartları JSON formatında değil")
                return False
        else:
            print("❌ Tarot kartları konfigürasyonu bulunamadı")
            return False
            
    except Exception as e:
        print(f"❌ Tarot kartları test hatası: {e}")
        return False

async def test_bot_simulation():
    """Bot simülasyonu yapar"""
    print("\n🔍 Bot Simülasyonu")
    print("=" * 50)
    
    try:
        from supabase import create_client
        import google.generativeai as genai
        import json
        
        # Setup
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not all([url, key, api_key]):
            print("❌ Gerekli environment variables eksik")
            return False
        
        supabase = create_client(url, key)
        genai.configure(api_key=api_key)
        
        # Simulate tarot card reading
        print("🔄 Tarot kartı çekme simülasyonu...")
        
        # 1. Get tarot cards
        config_result = supabase.table("config").select("*").eq("key", "tarot_cards").limit(1).execute()
        if not config_result.data:
            print("❌ Tarot kartları bulunamadı")
            return False
        
        tarot_cards = json.loads(config_result.data[0]['value'])
        selected_card = tarot_cards[0]  # The Fool
        print(f"   Seçilen kart: {selected_card}")
        
        # 2. Get tarot prompt
        prompt_result = supabase.table("prompts").select("*").eq("prompt_type", "tarot").eq("language", "tr").limit(1).execute()
        if not prompt_result.data:
            print("❌ Tarot prompt'u bulunamadı")
            return False
        
        prompt = prompt_result.data[0]['content']
        prompt = prompt.replace("{card}", selected_card).replace("{username}", "TestUser")
        print(f"   Prompt hazırlandı: {len(prompt)} karakter")
        
        # 3. Test Gemini API
        print("🔄 Gemini API çağrısı test ediliyor...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if response and response.text:
            print(f"✅ Tarot yorumu başarıyla oluşturuldu")
            print(f"   Yanıt uzunluğu: {len(response.text)} karakter")
            return True
        else:
            print("❌ Gemini API boş yanıt verdi")
            return False
            
    except Exception as e:
        print(f"❌ Bot simülasyonu hatası: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("🧪 FAL GRAM BOT TEST")
    print("=" * 60)
    
    tests = [
        ("Gemini API", test_gemini_api),
        ("Supabase Prompts", test_supabase_prompts),
        ("Tarot Cards", test_tarot_cards),
        ("Bot Simulation", test_bot_simulation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test hatası: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST ÖZETİ")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name}: {status}")
    
    print(f"\nToplam: {passed}/{total} test başarılı")
    
    if passed == total:
        print("\n🎉 Tüm testler başarılı! Bot çalışmalı.")
    else:
        print(f"\n⚠️  {total - passed} sorun tespit edildi.")
        print("\n🔧 Çözüm önerileri:")
        
        if not results.get("Gemini API"):
            print("• Gemini API anahtarını kontrol edin")
            print("• API kotanızı kontrol edin")
            print("• Ağ bağlantınızı kontrol edin")
        
        if not results.get("Supabase Prompts"):
            print("• Supabase prompt'larını kontrol edin")
        
        if not results.get("Tarot Cards"):
            print("• Tarot kartları konfigürasyonunu kontrol edin")
        
        if not results.get("Bot Simulation"):
            print("• Bot simülasyonu başarısız oldu")

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
"""
🔍 Quick Test - Fal Gram Components
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_prompts():
    """Supabase prompt'larını test eder"""
    print("🔍 Supabase Prompt Test")
    print("=" * 40)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials eksik")
            return False
        
        supabase = create_client(url, key)
        
        # Test prompts table
        try:
            result = supabase.table("prompts").select("*").limit(1).execute()
            print(f"✅ Prompts table erişilebilir: {len(result.data)} kayıt")
            
            # Test specific prompts
            prompt_types = ["tarot", "dream", "coffee"]
            for prompt_type in prompt_types:
                try:
                    result = supabase.table("prompts").select("*").eq("type", prompt_type).limit(1).execute()
                    if result.data:
                        print(f"✅ {prompt_type} prompt mevcut")
                    else:
                        print(f"❌ {prompt_type} prompt eksik")
                except Exception as e:
                    print(f"❌ {prompt_type} prompt hatası: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Prompts table hatası: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase bağlantı hatası: {e}")
        return False

def test_gemini_api():
    """Gemini API'sini test eder"""
    print("\n🔍 Gemini API Test")
    print("=" * 40)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY eksik")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with simple prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Merhaba")
        
        if response and response.text:
            print("✅ Gemini API çalışıyor")
            print(f"   Yanıt: {response.text[:50]}...")
            return True
        else:
            print("❌ Gemini API boş yanıt verdi")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API hatası: {e}")
        return False

def test_tarot_cards():
    """Tarot kartlarını test eder"""
    print("\n🔍 Tarot Cards Test")
    print("=" * 40)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        # Test tarot_cards table
        result = supabase.table("tarot_cards").select("*").execute()
        
        if result.data:
            print(f"✅ Tarot kartları mevcut: {len(result.data)} kart")
            print(f"   Örnek kartlar: {[card['name'] for card in result.data[:3]]}")
            return True
        else:
            print("❌ Tarot kartları eksik")
            return False
            
    except Exception as e:
        print(f"❌ Tarot kartları hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🔮 FAL GRAM QUICK TEST")
    print("=" * 50)
    
    tests = [
        ("Supabase Prompts", test_supabase_prompts),
        ("Gemini API", test_gemini_api),
        ("Tarot Cards", test_tarot_cards)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test hatası: {e}")
            results[test_name] = False
    
    # Özet
    print("\n" + "=" * 50)
    print("📊 TEST ÖZETİ")
    print("=" * 50)
    
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
        
        if not results.get("Supabase Prompts"):
            print("• Supabase'de prompts tablosunu kontrol edin")
            print("• Gerekli prompt'ları ekleyin (tarot, dream, coffee)")
        
        if not results.get("Gemini API"):
            print("• Gemini API anahtarınızı kontrol edin")
            print("• API kotanızı kontrol edin")
        
        if not results.get("Tarot Cards"):
            print("• Supabase'de tarot_cards tablosunu kontrol edin")
            print("• Tarot kartlarını ekleyin")

if __name__ == "__main__":
    main() 
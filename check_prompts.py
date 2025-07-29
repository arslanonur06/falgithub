#!/usr/bin/env python3
"""
🔍 Check Prompts - Supabase'deki mevcut prompt'ları kontrol eder
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_prompts():
    """Supabase'deki prompt'ları kontrol eder"""
    print("🔍 Supabase Prompts Kontrolü")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials eksik")
            return False
        
        supabase = create_client(url, key)
        
        # Tüm prompt'ları getir
        try:
            result = supabase.table("prompts").select("*").execute()
            
            if result.data:
                print(f"✅ Prompts table'da {len(result.data)} kayıt var")
                print("\n📋 Mevcut prompt'lar:")
                print("-" * 30)
                
                for prompt in result.data:
                    prompt_type = prompt.get('prompt_type', 'N/A')
                    language = prompt.get('language', 'N/A')
                    content_length = len(prompt.get('content', ''))
                    print(f"• {prompt_type} ({language}) - {content_length} karakter")
                
                # Bot'ta kullanılan prompt tiplerini kontrol et
                bot_prompt_types = ["coffee_fortune", "tarot", "dream", "daily_horoscope"]
                print(f"\n🔍 Bot'ta kullanılan prompt tipleri:")
                print("-" * 30)
                
                for prompt_type in bot_prompt_types:
                    matching_prompts = [p for p in result.data if p.get('prompt_type') == prompt_type]
                    if matching_prompts:
                        print(f"✅ {prompt_type}: {len(matching_prompts)} kayıt")
                    else:
                        print(f"❌ {prompt_type}: BULUNAMADI")
                
                return True
                
            else:
                print("❌ Prompts table boş")
                return False
                
        except Exception as e:
            print(f"❌ Prompts table hatası: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase bağlantı hatası: {e}")
        return False

def check_tarot_cards():
    """Tarot kartlarını kontrol eder"""
    print("\n🔍 Tarot Cards Kontrolü")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        result = supabase.table("tarot_cards").select("*").execute()
        
        if result.data:
            print(f"✅ Tarot kartları mevcut: {len(result.data)} kart")
            print("\n🎴 İlk 5 kart:")
            for i, card in enumerate(result.data[:5]):
                print(f"  {i+1}. {card.get('name', 'N/A')}")
        else:
            print("❌ Tarot kartları eksik")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Tarot kartları hatası: {e}")
        return False

def test_prompt_retrieval():
    """Prompt alma işlemini test eder"""
    print("\n🔍 Prompt Alma Testi")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        # Bot'ta kullanılan prompt tiplerini test et
        test_cases = [
            ("coffee_fortune", "tr"),
            ("tarot", "tr"),
            ("dream", "tr"),
            ("daily_horoscope", "tr")
        ]
        
        for prompt_type, lang in test_cases:
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
        print(f"❌ Prompt alma testi hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🔮 FAL GRAM PROMPT KONTROLÜ")
    print("=" * 60)
    
    # Check prompts
    prompts_ok = check_supabase_prompts()
    
    # Check tarot cards
    tarot_ok = check_tarot_cards()
    
    # Test prompt retrieval
    retrieval_ok = test_prompt_retrieval()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ÖZET")
    print("=" * 60)
    
    if prompts_ok and tarot_ok and retrieval_ok:
        print("✅ Tüm prompt'lar mevcut ve erişilebilir!")
        print("🎉 Bot normal çalışmalı.")
    else:
        print("❌ Prompt sorunları tespit edildi.")
        print("\n🔧 Çözüm önerileri:")
        
        if not prompts_ok:
            print("• Supabase'de prompts tablosunu kontrol edin")
            print("• fix_prompts_table.sql dosyasını çalıştırın")
        
        if not tarot_ok:
            print("• Tarot kartlarını ekleyin")
        
        if not retrieval_ok:
            print("• Prompt tiplerini kontrol edin")
            print("• Bot kodundaki prompt tipleri ile Supabase'deki tipler eşleşmiyor olabilir")

if __name__ == "__main__":
    main() 
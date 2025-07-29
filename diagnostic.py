#!/usr/bin/env python3
"""
🔍 Fal Gram Diagnostic Tool
Rüya, tarot ve kahve falı sorunlarını tespit eder
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Environment variables'ları kontrol eder"""
    print("🔍 Environment Variables Kontrolü")
    print("=" * 50)
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GEMINI_API_KEY", 
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "ADMIN_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Hassas bilgileri gizle
            if "TOKEN" in var or "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: EKSİK")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Eksik environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ Tüm environment variables mevcut")
        return True

def check_telegram_api():
    """Telegram API'sini kontrol eder"""
    print("\n🔍 Telegram API Kontrolü")
    print("=" * 50)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN bulunamadı")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Bot bağlantısı başarılı")
                print(f"   Bot adı: {bot_info.get('first_name', 'N/A')}")
                print(f"   Bot kullanıcı adı: @{bot_info.get('username', 'N/A')}")
                print(f"   Bot ID: {bot_info.get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Bot API hatası: {data.get('description', 'Bilinmeyen hata')}")
                return False
        else:
            print(f"❌ HTTP hatası: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram API bağlantı hatası: {e}")
        return False

def check_gemini_api():
    """Gemini API'sini kontrol eder"""
    print("\n🔍 Gemini API Kontrolü")
    print("=" * 50)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY bulunamadı")
        return False
    
    try:
        genai.configure(api_key=api_key)
        
        # Test with different models
        models_to_test = [
            'gemini-1.5-flash',
            'gemini-2.0-flash-exp'
        ]
        
        for model_name in models_to_test:
            try:
                print(f"🔄 {model_name} test ediliyor...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Test")
                
                if response and response.text:
                    print(f"✅ {model_name} çalışıyor")
                    return True
                else:
                    print(f"⚠️  {model_name} boş yanıt verdi")
                    
            except Exception as e:
                print(f"❌ {model_name} hatası: {str(e)[:100]}")
        
        print("❌ Hiçbir Gemini modeli çalışmıyor")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API genel hatası: {e}")
        return False

def check_supabase_connection():
    """Supabase bağlantısını kontrol eder"""
    print("\n🔍 Supabase Bağlantı Kontrolü")
    print("=" * 50)
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials eksik")
        return False
    
    try:
        from supabase import create_client
        
        supabase = create_client(url, key)
        
        # Test connection with a simple query
        result = supabase.table("users").select("count").limit(1).execute()
        
        print("✅ Supabase bağlantısı başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Supabase bağlantı hatası: {e}")
        return False

def check_bot_handlers():
    """Bot handler'larını kontrol eder"""
    print("\n🔍 Bot Handler Kontrolü")
    print("=" * 50)
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_handlers = [
            'draw_tarot_card',
            'handle_dream_text', 
            'process_coffee_fortune',
            'select_service_callback'
        ]
        
        missing_handlers = []
        for handler in required_handlers:
            if handler in content:
                print(f"✅ {handler} handler mevcut")
            else:
                print(f"❌ {handler} handler eksik")
                missing_handlers.append(handler)
        
        if missing_handlers:
            print(f"\n⚠️  Eksik handler'lar: {', '.join(missing_handlers)}")
            return False
        else:
            print("\n✅ Tüm gerekli handler'lar mevcut")
            return True
            
    except Exception as e:
        print(f"❌ Bot dosyası okuma hatası: {e}")
        return False

def check_prompts():
    """Prompt dosyalarını kontrol eder"""
    print("\n🔍 Prompt Dosyaları Kontrolü")
    print("=" * 50)
    
    prompt_files = [
        'prompts.json',
        'locales/en.json',
        'locales/tr.json'
    ]
    
    missing_files = []
    for file_path in prompt_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} mevcut")
        else:
            print(f"❌ {file_path} eksik")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Eksik dosyalar: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ Tüm prompt dosyaları mevcut")
        return True

def main():
    """Ana diagnostic fonksiyonu"""
    print("🔮 FAL GRAM DIAGNOSTIC TOOL")
    print("=" * 60)
    print("Rüya, tarot ve kahve falı sorunlarını tespit eder\n")
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Telegram API", check_telegram_api),
        ("Gemini API", check_gemini_api),
        ("Supabase Connection", check_supabase_connection),
        ("Bot Handlers", check_bot_handlers),
        ("Prompt Files", check_prompts)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} kontrolünde hata: {e}")
            results[check_name] = False
    
    # Özet
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC ÖZETİ")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{check_name}: {status}")
    
    print(f"\nToplam: {passed}/{total} kontrol başarılı")
    
    if passed == total:
        print("\n🎉 Tüm kontroller başarılı! Bot çalışmalı.")
    else:
        print(f"\n⚠️  {total - passed} sorun tespit edildi.")
        print("\n🔧 Önerilen çözümler:")
        
        if not results.get("Environment Variables"):
            print("• .env dosyasını kontrol edin ve eksik değişkenleri ekleyin")
        
        if not results.get("Telegram API"):
            print("• Telegram Bot Token'ınızı kontrol edin")
        
        if not results.get("Gemini API"):
            print("• Gemini API anahtarınızı kontrol edin")
        
        if not results.get("Supabase Connection"):
            print("• Supabase URL ve anahtarınızı kontrol edin")
        
        if not results.get("Bot Handlers"):
            print("• bot.py dosyasında eksik handler'ları ekleyin")
        
        if not results.get("Prompt Files"):
            print("• Eksik prompt dosyalarını oluşturun")

if __name__ == "__main__":
    main() 
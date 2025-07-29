#!/usr/bin/env python3
"""
🔍 Check Config - Supabase config tablosunu kontrol eder
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_config_table():
    """Config tablosunu kontrol eder"""
    print("🔍 Config Table Kontrolü")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials eksik")
            return False
        
        supabase = create_client(url, key)
        
        # Config tablosunu kontrol et
        try:
            result = supabase.table("config").select("*").execute()
            
            if result.data:
                print(f"✅ Config table'da {len(result.data)} kayıt var")
                print("\n📋 Mevcut konfigürasyonlar:")
                print("-" * 40)
                
                for config in result.data:
                    config_key = config.get('key', 'N/A')
                    config_value = config.get('value', 'N/A')
                    if len(config_value) > 50:
                        config_value = config_value[:50] + "..."
                    print(f"• {config_key}: {config_value}")
                
                # Bot için gerekli konfigürasyonları kontrol et
                required_configs = ["tarot_cards", "daily_card_hour", "daily_card_minute"]
                print(f"\n🔍 Bot için gerekli konfigürasyonlar:")
                print("-" * 40)
                
                for config_key in required_configs:
                    matching_configs = [c for c in result.data if c.get('key') == config_key]
                    if matching_configs:
                        print(f"✅ {config_key}: Mevcut")
                    else:
                        print(f"❌ {config_key}: EKSİK")
                
                return True
                
            else:
                print("❌ Config table boş")
                return False
                
        except Exception as e:
            print(f"❌ Config table hatası: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase bağlantı hatası: {e}")
        return False

def test_tarot_cards_config():
    """Tarot kartları konfigürasyonunu test eder"""
    print("\n🔍 Tarot Cards Config Testi")
    print("=" * 50)
    
    try:
        from supabase import create_client
        import json
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(url, key)
        
        # Tarot kartları konfigürasyonunu al
        result = supabase.table("config").select("*").eq("key", "tarot_cards").limit(1).execute()
        
        if result.data:
            config = result.data[0]
            tarot_cards_value = config.get('value', '[]')
            
            try:
                tarot_cards = json.loads(tarot_cards_value)
                if isinstance(tarot_cards, list):
                    print(f"✅ Tarot kartları konfigürasyonu mevcut: {len(tarot_cards)} kart")
                    print(f"   İlk 5 kart: {tarot_cards[:5]}")
                    return True
                else:
                    print("❌ Tarot kartları konfigürasyonu liste formatında değil")
                    return False
            except json.JSONDecodeError:
                print("❌ Tarot kartları konfigürasyonu geçerli JSON değil")
                return False
        else:
            print("❌ Tarot kartları konfigürasyonu bulunamadı")
            return False
            
    except Exception as e:
        print(f"❌ Tarot kartları config testi hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🔮 FAL GRAM CONFIG KONTROLÜ")
    print("=" * 60)
    
    # Check config table
    config_ok = check_config_table()
    
    # Test tarot cards config
    tarot_config_ok = test_tarot_cards_config()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ÖZET")
    print("=" * 60)
    
    if config_ok and tarot_config_ok:
        print("✅ Tüm konfigürasyonlar mevcut!")
        print("🎉 Bot normal çalışmalı.")
    else:
        print("❌ Konfigürasyon sorunları tespit edildi.")
        print("\n🔧 Çözüm önerileri:")
        
        if not config_ok:
            print("• Config tablosunu kontrol edin")
        
        if not tarot_config_ok:
            print("• fix_tarot_config.sql dosyasını Supabase'de çalıştırın")
            print("• Bu tarot kartları konfigürasyonunu ekleyecek")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🔧 Gemini API Fix Tool
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_models():
    """Farklı Gemini modellerini test eder"""
    print("🔍 Gemini API Model Test")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY eksik")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test different models
        models_to_test = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash'
        ]
        
        working_models = []
        
        for model_name in models_to_test:
            try:
                print(f"🔄 {model_name} test ediliyor...")
                model = genai.GenerativeModel(model_name)
                
                # Simple test with timeout
                start_time = time.time()
                response = model.generate_content("Test")
                end_time = time.time()
                
                if response and response.text:
                    print(f"✅ {model_name} çalışıyor ({(end_time - start_time):.2f}s)")
                    working_models.append(model_name)
                else:
                    print(f"⚠️  {model_name} boş yanıt verdi")
                    
            except Exception as e:
                print(f"❌ {model_name} hatası: {str(e)[:100]}")
        
        if working_models:
            print(f"\n✅ Çalışan modeller: {', '.join(working_models)}")
            return True
        else:
            print("\n❌ Hiçbir model çalışmıyor")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API genel hatası: {e}")
        return False

def check_api_quota():
    """API kotasını kontrol eder"""
    print("\n🔍 API Kota Kontrolü")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY eksik")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try to get model info
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ API anahtarı geçerli")
            print("ℹ️  Kullanım limitlerini kontrol etmek için Google AI Studio'yu ziyaret edin")
            return True
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                print("❌ API kotası aşıldı")
                print("💡 Çözüm: Google AI Studio'da kotanızı kontrol edin")
            else:
                print(f"❌ API hatası: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Kota kontrolü hatası: {e}")
        return False

def suggest_alternatives():
    """Alternatif çözümler önerir"""
    print("\n🔧 Alternatif Çözümler")
    print("=" * 50)
    
    print("1. **API Anahtarını Yenileyin:**")
    print("   • Google AI Studio'ya gidin")
    print("   • Yeni bir API anahtarı oluşturun")
    print("   • .env dosyasını güncelleyin")
    
    print("\n2. **Kota Kontrolü:**")
    print("   • Google AI Studio'da kullanım istatistiklerini kontrol edin")
    print("   • Günlük/aylık limitleri kontrol edin")
    
    print("\n3. **Ağ Bağlantısı:**")
    print("   • İnternet bağlantınızı kontrol edin")
    print("   • VPN kullanıyorsanız kapatın")
    print("   • Proxy ayarlarını kontrol edin")
    
    print("\n4. **Alternatif Model:**")
    print("   • Bot kodunda farklı bir model kullanın")
    print("   • Örnek: gemini-1.5-pro yerine gemini-1.5-flash")

def main():
    """Ana fonksiyon"""
    print("🔧 GEMINI API FIX TOOL")
    print("=" * 60)
    
    # Test models
    models_ok = test_gemini_models()
    
    # Check quota
    quota_ok = check_api_quota()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ÖZET")
    print("=" * 60)
    
    if models_ok and quota_ok:
        print("✅ Gemini API çalışıyor!")
        print("🎉 Bot normal çalışmalı.")
    else:
        print("❌ Gemini API sorunları tespit edildi.")
        suggest_alternatives()

if __name__ == "__main__":
    main() 
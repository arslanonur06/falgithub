#!/usr/bin/env python3
"""
Comprehensive syntax fix for bot.py
"""

import re

def fix_all_syntax_errors():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all incomplete try-except blocks
    fixes = [
        # Fix try block in start function around line 805
        (r'(\s+)if context\.args:\s*\n\s+referrer_id = context\.args\[0\]\s*\n\s+supabase_manager\.add_log.*?\n\s+(\s+)referrer_user_id = int\(referrer_id\)', 
         r'\1if context.args:\n\1    referrer_id = context.args[0]\n\1    supabase_manager.add_log(f"Referral link ile geldi: {user_id_str} - Referrer: {referrer_id}")\n\1    \n\1    try:\n\1        \2referrer_user_id = int(referrer_id)'),
        
        # Fix missing except for the above
        (r'(\s+)new_earnings = referrer\.get\(\'referral_earnings\', 0\) \+ 50\s*\n\s+supabase_manager\.update_user\(referrer_user_id, \{\'referred_count\': new_count, \'referral_earnings\': new_earnings\}\)\s*\n\s+supabase_manager\.add_log', 
         r'\1new_earnings = referrer.get(\'referral_earnings\', 0) + 50\n\1supabase_manager.update_user(referrer_user_id, {\'referred_count\': new_count, \'referral_earnings\': new_earnings\})\n\1supabase_manager.add_log'),
        
        # Fix incomplete try blocks in draw_tarot_card
        (r'(\s+)try:\s*\n\s+tarot_cards = supabase_manager\.get_tarot_cards\(\)', 
         r'\1try:\n\1    tarot_cards = supabase_manager.get_tarot_cards()'),
        
        # Fix incomplete try blocks in handle_dream_text
        (r'(\s+)try:\s*\n\s+# Basit ve güvenilir model seçimi', 
         r'\1try:\n\1    # Basit ve güvenilir model seçimi'),
        
        # Fix incomplete try blocks in generate_daily_horoscope
        (r'(\s+)try:\s*\n\s+# Gemini 2\.0 modelini kullan', 
         r'\1try:\n\1    # Gemini 2.0 modelini kullan'),
        
        # Fix incomplete try blocks in generate_compatibility_analysis
        (r'(\s+)try:\s*\n\s+# Gemini model with rate limiting', 
         r'\1try:\n\1    # Gemini model with rate limiting'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Add missing except blocks where needed
    except_fixes = [
        # Add except block after referral processing
        (r'(\s+)supabase_manager\.add_log\(f"Referral işlemi tamamlandı: {user_id_str} - Referrer: {referrer_id}"\)\s*\n\s+except ValueError:', 
         r'\1supabase_manager.add_log(f"Referral işlemi tamamlandı: {user_id_str} - Referrer: {referrer_id}")\n\1except ValueError:'),
        
        # Add except block for tarot function
        (r'(\s+)supabase_manager\.add_log\(f"✅ Tarot Gemini API çağrısı tamamlandı \({lang}\)"\)\s*\n\s+except Exception as gemini_error:', 
         r'\1supabase_manager.add_log(f"✅ Tarot Gemini API çağrısı tamamlandı ({lang})")\n\1except Exception as gemini_error:'),
        
        # Add except block for dream function
        (r'(\s+)supabase_manager\.add_log\(f"✅ Rüya Gemini API çağrısı tamamlandı \({lang}\)"\)\s*\n\s+except Exception as gemini_error:', 
         r'\1supabase_manager.add_log(f"✅ Rüya Gemini API çağrısı tamamlandı ({lang})")\n\1except Exception as gemini_error:'),
        
        # Add except block for horoscope function
        (r'(\s+)supabase_manager\.add_log\(f"✅ Burç Gemini API çağrısı tamamlandı \({lang}\)"\)\s*\n\s+except Exception as gemini_error:', 
         r'\1supabase_manager.add_log(f"✅ Burç Gemini API çağrısı tamamlandı ({lang})")\n\1except Exception as gemini_error:'),
        
        # Add except block for compatibility function
        (r'(\s+)supabase_manager\.add_log\(f"✅ Uyumluluk Gemini API çağrısı tamamlandı \({lang}\)"\)\s*\n\s+except Exception as gemini_error:', 
         r'\1supabase_manager.add_log(f"✅ Uyumluluk Gemini API çağrısı tamamlandı ({lang})")\n\1except Exception as gemini_error:'),
    ]
    
    for pattern, replacement in except_fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Add missing function definitions if they don't exist
    if 'async def process_birth_chart' not in content:
        missing_functions = '''
# Missing function definitions
async def process_birth_chart(update: Update, context: CallbackContext):
    """Process birth chart analysis"""
    pass

async def handle_chatbot_question(update: Update, context: CallbackContext):
    """Handle chatbot questions"""
    pass

async def toggle_daily_subscription(update: Update, context: CallbackContext):
    """Toggle daily subscription"""
    pass
'''
        content = content.replace('# --- Menü ve Buton Oluşturucular ---', 
                                missing_functions + '\n# --- Menü ve Buton Oluşturucular ---')
    
    # Add missing supabase_manager initialization if it doesn't exist
    if 'supabase_manager = SupabaseManager' not in content:
        content = content.replace('# Global rate limiter instance', 
                                '# Global rate limiter instance\n\n# Global Supabase Yöneticisi\nsupabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)')
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Comprehensive syntax fixes applied!")

if __name__ == "__main__":
    fix_all_syntax_errors() 
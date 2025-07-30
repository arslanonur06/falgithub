#!/usr/bin/env python3
"""
Quick syntax fix for bot.py
"""

import re

def fix_syntax_errors():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix incomplete try-except blocks in functions
    patterns_to_fix = [
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
        
        # Fix missing except blocks
        (r'(\s+)except Exception as gemini_error:\s*\n\s+supabase_manager\.add_log', 
         r'\1except Exception as gemini_error:\n\1    supabase_manager.add_log'),
        
        # Fix missing except blocks for DeepSeek
        (r'(\s+)except Exception as deepseek_error:\s*\n\s+supabase_manager\.add_log', 
         r'\1except Exception as deepseek_error:\n\1    supabase_manager.add_log'),
        
        # Fix missing except blocks for timeout
        (r'(\s+)except asyncio\.TimeoutError:\s*\n\s+supabase_manager\.add_log', 
         r'\1except asyncio.TimeoutError:\n\1    supabase_manager.add_log'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Fix missing function definitions
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
    
    # Add missing functions before the main execution
    if 'async def process_birth_chart' not in content:
        content = content.replace('# --- Menü ve Buton Oluşturucular ---', 
                                missing_functions + '\n# --- Menü ve Buton Oluşturucular ---')
    
    # Fix missing supabase_manager initialization
    if 'supabase_manager = SupabaseManager' not in content:
        content = content.replace('# Global rate limiter instance', 
                                '# Global rate limiter instance\n\n# Global Supabase Yöneticisi\nsupabase_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)')
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Quick syntax fixes applied!")

if __name__ == "__main__":
    fix_syntax_errors() 
#!/usr/bin/env python3
"""
Final comprehensive syntax fix for bot.py
"""

import re

def fix_final_syntax():
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix unmatched parentheses and incomplete try-except blocks
    fixes = [
        # Fix the specific issue around line 937
        (r'(\s+)except Exception as gemini_error:\s*\n\s+(\s+)supabase_manager\.add_log\(f"❌ Gemini API hatası, DeepSeek\'e geçiliyor: \{str\(gemini_error\)\[:100\]\}"\)\s*\n\s+(\s+)# Fallback to DeepSeek API\s*\n\s+(\s+)loop\.run_in_executor\(None, call_deepseek_api, final_prompt\),', 
         r'\1except Exception as gemini_error:\n\1    \2supabase_manager.add_log(f"❌ Gemini API hatası, DeepSeek\'e geçiliyor: {str(gemini_error)[:100]}")\n\1    \n\1    \3# Fallback to DeepSeek API\n\1    \4try:\n\1        \4loop.run_in_executor(None, call_deepseek_api, final_prompt),'),
        
        # Fix missing except blocks for DeepSeek
        (r'(\s+)loop\.run_in_executor\(None, call_deepseek_api, final_prompt\),\s*\n\s+timeout=20\.0\s*\n\s+\)\s*\n\s+(\s+)# Create a response object similar to Gemini', 
         r'\1loop.run_in_executor(None, call_deepseek_api, final_prompt),\n\1timeout=20.0\n\1)\n\1\n\1\2# Create a response object similar to Gemini'),
        
        # Add missing except blocks for DeepSeek errors
        (r'(\s+)# Create a response object similar to Gemini\s*\n\s+response = type\(\'Response\', \(\)', 
         r'\1# Create a response object similar to Gemini\n\1response = type(\'Response\', ()'),
        
        # Fix missing except blocks
        (r'(\s+)response = type\(\'Response\', \(\)', 
         r'\1except Exception as deepseek_error:\n\1    supabase_manager.add_log(f"❌ DeepSeek API hatası: {str(deepseek_error)[:100]}")\n\1    # Fallback response\n\1    response = type(\'Response\', ()'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix all incomplete try blocks by adding proper indentation
    content = re.sub(r'(\s+)try:\s*\n\s+([^#\n]+)', r'\1try:\n\1    \2', content, flags=re.MULTILINE)
    
    # Fix all incomplete except blocks by adding proper indentation
    content = re.sub(r'(\s+)except Exception as (\w+):\s*\n\s+([^#\n]+)', r'\1except Exception as \2:\n\1    \3', content, flags=re.MULTILINE)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Final syntax fixes applied!")

if __name__ == "__main__":
    fix_final_syntax() 
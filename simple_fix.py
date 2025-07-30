#!/usr/bin/env python3
"""
Simple fix for the specific syntax issue
"""

def simple_fix():
    with open('bot.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Fix the specific pattern around line 984
        if 'Try Gemini API first, then fallback to DeepSeek' in line:
            # Add missing try block
            fixed_lines.append(line)
            fixed_lines.append('        try:\n')
            i += 1
            continue
        
        # Fix the specific pattern with loop.run_in_executor
        if 'loop.run_in_executor(None, model.generate_content, final_prompt),' in line:
            # Add proper indentation
            fixed_lines.append('            ' + line.lstrip())
            i += 1
            continue
        
        # Fix the specific pattern with timeout
        if 'timeout=15.0  # 15 saniye timeout' in line:
            fixed_lines.append('            ' + line.lstrip())
            i += 1
            continue
        
        # Fix the specific pattern with closing parenthesis
        if line.strip() == ')' and 'timeout' in lines[i-1]:
            fixed_lines.append('            ' + line.lstrip())
            i += 1
            continue
        
        fixed_lines.append(line)
        i += 1
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Simple fix applied!")

if __name__ == "__main__":
    simple_fix() 
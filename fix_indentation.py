#!/usr/bin/env python3
"""
Fix indentation issues in bot.py
"""

def fix_indentation():
    with open('bot.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for i, line in enumerate(lines):
        # Fix the specific indentation issue around line 812
        if i >= 810 and i <= 820:
            # Remove extra spaces at the beginning of the line
            if line.startswith('             '):
                line = '        ' + line.lstrip()
            elif line.startswith('            '):
                line = '        ' + line.lstrip()
        
        fixed_lines.append(line)
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Indentation fixed!")

if __name__ == "__main__":
    fix_indentation() 
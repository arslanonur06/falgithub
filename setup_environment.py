#!/usr/bin/env python3
"""
Environment Setup Script for Fal Gram Bot
This script helps you configure the required environment variables.
"""

import os
import sys

def create_env_file():
    """Create a .env file with user input."""
    
    print("🔧 Fal Gram Bot Environment Setup")
    print("=" * 50)
    print("This script will help you create a .env file with all required variables.")
    print("You can get these values from your bot configuration and services.")
    print()
    
    env_vars = {}
    
    # Telegram Bot Configuration
    print("📱 TELEGRAM BOT CONFIGURATION")
    print("-" * 30)
    env_vars['TELEGRAM_BOT_TOKEN'] = input("Enter your Telegram Bot Token: ").strip()
    env_vars['ADMIN_ID'] = input("Enter your Admin User ID (optional, press Enter to skip): ").strip()
    
    print()
    print("🗄️ DATABASE CONFIGURATION")
    print("-" * 30)
    env_vars['SUPABASE_URL'] = input("Enter your Supabase URL: ").strip()
    env_vars['SUPABASE_KEY'] = input("Enter your Supabase Key: ").strip()
    
    print()
    print("🤖 AI SERVICE CONFIGURATION")
    print("-" * 30)
    env_vars['GEMINI_API_KEY'] = input("Enter your Gemini API Key (optional, press Enter to skip): ").strip()
    env_vars['DEEPSEEK_API_KEY'] = input("Enter your DeepSeek API Key (optional, press Enter to skip): ").strip()
    
    print()
    print("💳 PAYMENT CONFIGURATION")
    print("-" * 30)
    env_vars['PAYMENT_PROVIDER_TOKEN'] = input("Enter your Telegram Stars Token (optional, press Enter to skip): ").strip()
    
    # Create .env file
    env_content = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={}
ADMIN_ID={}

# Database Configuration
SUPABASE_URL={}
SUPABASE_KEY={}

# AI Service Configuration
GEMINI_API_KEY={}
DEEPSEEK_API_KEY={}

# Payment Configuration
PAYMENT_PROVIDER_TOKEN={}

# Optional Configuration
# FREE_READING_LIMIT=5
# PAID_READING_STARS=250
""".format(
        env_vars['TELEGRAM_BOT_TOKEN'],
        env_vars['ADMIN_ID'],
        env_vars['SUPABASE_URL'],
        env_vars['SUPABASE_KEY'],
        env_vars['GEMINI_API_KEY'],
        env_vars['DEEPSEEK_API_KEY'],
        env_vars['PAYMENT_PROVIDER_TOKEN']
    )
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print()
        print("✅ .env file created successfully!")
        print("📁 Location: {}/.env".format(os.getcwd()))
        print()
        print("🔒 IMPORTANT: Keep your .env file secure and never commit it to version control!")
        print("📝 You can now run your bot with: python bot.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("Please create the .env file manually with the following content:")
        print()
        print(env_content)

def check_requirements():
    """Check if required packages are installed."""
    print("🔍 Checking required packages...")
    
    required_packages = [
        'python-telegram-bot',
        'python-dotenv',
        'requests',
        'google-generativeai',
        'supabase',
        'apscheduler',
        'fpdf2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-telegram-bot':
                import telegram
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'google-generativeai':
                import google.generativeai
            elif package == 'fpdf2':
                import fpdf
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print()
        print("⚠️ Missing packages detected!")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed!")
    return True

def main():
    """Main function."""
    print("🚀 Fal Gram Bot Setup")
    print("=" * 50)
    
    # Check requirements first
    if not check_requirements():
        print()
        print("Please install missing packages and run this script again.")
        return
    
    print()
    
    # Ask user what they want to do
    print("What would you like to do?")
    print("1. Create .env file")
    print("2. Check requirements only")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        create_env_file()
    elif choice == '2':
        print("✅ Requirements check completed!")
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main() 
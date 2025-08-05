#!/usr/bin/env python3
"""
Environment setup script for Fal Gram Bot.
This script helps you configure your .env file with the required environment variables.
"""

import os
import sys
from pathlib import Path

def get_user_input(prompt: str, default: str = "", required: bool = True) -> str:
    """Get user input with validation."""
    while True:
        value = input(f"{prompt} {f'(default: {default})' if default else ''}: ").strip()
        if not value and default:
            value = default
        if required and not value:
            print("❌ This field is required. Please enter a value.")
            continue
        return value

def setup_environment():
    """Interactive environment setup."""
    print("🔧 Fal Gram Bot Environment Setup")
    print("=" * 50)
    print("This script will help you configure your .env file.")
    print("You can press Enter to use default values where available.\n")
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Collect environment variables
    env_vars = {}
    
    print("\n🤖 Bot Configuration:")
    env_vars['TELEGRAM_BOT_TOKEN'] = get_user_input(
        "Enter your Telegram Bot Token (from @BotFather):",
        required=True
    )
    
    print("\n👤 Admin Configuration:")
    env_vars['ADMIN_ID'] = get_user_input(
        "Enter your Telegram User ID (for admin access):",
        required=False
    )
    
    print("\n💳 Payment Configuration:")
    env_vars['PAYMENT_PROVIDER_TOKEN'] = get_user_input(
        "Enter your Telegram Stars Provider Token:",
        required=True
    )
    
    print("\n🔑 API Keys:")
    env_vars['GEMINI_API_KEY'] = get_user_input(
        "Enter your Google Gemini API Key:",
        required=True
    )
    env_vars['DEEPSEEK_API_KEY'] = get_user_input(
        "Enter your DeepSeek API Key:",
        required=False
    )
    
    print("\n🗄️ Database Configuration:")
    env_vars['SUPABASE_URL'] = get_user_input(
        "Enter your Supabase URL:",
        required=True
    )
    env_vars['SUPABASE_KEY'] = get_user_input(
        "Enter your Supabase Anon Key:",
        required=True
    )
    
    print("\n⚙️ Environment Settings:")
    env_vars['ENVIRONMENT'] = get_user_input(
        "Environment (development/production):",
        "development",
        required=False
    )
    env_vars['DEBUG'] = get_user_input(
        "Enable debug mode (true/false):",
        "true",
        required=False
    )
    env_vars['LOG_LEVEL'] = get_user_input(
        "Log level (DEBUG/INFO/WARNING/ERROR):",
        "INFO",
        required=False
    )
    
    print("\n🚦 Rate Limiting:")
    env_vars['RATE_LIMIT_ENABLED'] = get_user_input(
        "Enable rate limiting (true/false):",
        "true",
        required=False
    )
    env_vars['RATE_LIMIT_REQUESTS'] = get_user_input(
        "Rate limit requests per window:",
        "10",
        required=False
    )
    env_vars['RATE_LIMIT_WINDOW'] = get_user_input(
        "Rate limit window in seconds:",
        "60",
        required=False
    )
    
    print("\n🌐 Webhook Configuration (optional):")
    env_vars['WEBHOOK_URL'] = get_user_input(
        "Webhook URL (leave empty for polling):",
        "",
        required=False
    )
    env_vars['WEBHOOK_PORT'] = get_user_input(
        "Webhook port:",
        "8443",
        required=False
    )
    
    # Create .env file
    try:
        with open(env_file, 'w') as f:
            f.write("# Bot Configuration\n")
            f.write(f"TELEGRAM_BOT_TOKEN={env_vars['TELEGRAM_BOT_TOKEN']}\n\n")
            
            f.write("# Admin Configuration\n")
            f.write(f"ADMIN_ID={env_vars['ADMIN_ID']}\n\n")
            
            f.write("# Payment Configuration\n")
            f.write(f"PAYMENT_PROVIDER_TOKEN={env_vars['PAYMENT_PROVIDER_TOKEN']}\n\n")
            
            f.write("# API Keys\n")
            f.write(f"GEMINI_API_KEY={env_vars['GEMINI_API_KEY']}\n")
            f.write(f"DEEPSEEK_API_KEY={env_vars['DEEPSEEK_API_KEY']}\n\n")
            
            f.write("# Database Configuration\n")
            f.write(f"SUPABASE_URL={env_vars['SUPABASE_URL']}\n")
            f.write(f"SUPABASE_KEY={env_vars['SUPABASE_KEY']}\n\n")
            
            f.write("# Environment\n")
            f.write(f"ENVIRONMENT={env_vars['ENVIRONMENT']}\n")
            f.write(f"DEBUG={env_vars['DEBUG']}\n")
            f.write(f"LOG_LEVEL={env_vars['LOG_LEVEL']}\n\n")
            
            f.write("# Rate Limiting\n")
            f.write(f"RATE_LIMIT_ENABLED={env_vars['RATE_LIMIT_ENABLED']}\n")
            f.write(f"RATE_LIMIT_REQUESTS={env_vars['RATE_LIMIT_REQUESTS']}\n")
            f.write(f"RATE_LIMIT_WINDOW={env_vars['RATE_LIMIT_WINDOW']}\n\n")
            
            f.write("# Webhook Configuration (optional - for production)\n")
            f.write(f"WEBHOOK_URL={env_vars['WEBHOOK_URL']}\n")
            f.write(f"WEBHOOK_PORT={env_vars['WEBHOOK_PORT']}\n")
        
        print(f"\n✅ Environment file created successfully: {env_file}")
        print("\n📋 Next steps:")
        print("1. Review the .env file to ensure all values are correct")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the bot: python main_new.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def validate_environment():
    """Validate the current environment configuration."""
    print("🔍 Validating Environment Configuration")
    print("=" * 50)
    
    # Load settings
    try:
        from config.settings import settings
        
        # Check required variables
        required_vars = [
            ("TELEGRAM_BOT_TOKEN", settings.BOT_TOKEN),
            ("GEMINI_API_KEY", settings.GEMINI_API_KEY),
            ("SUPABASE_URL", settings.SUPABASE_URL),
            ("SUPABASE_KEY", settings.SUPABASE_KEY),
            ("PAYMENT_PROVIDER_TOKEN", settings.PAYMENT_PROVIDER_TOKEN),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
            else:
                print(f"✅ {var_name}: {'*' * len(var_value)}")
        
        if missing_vars:
            print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
            return False
        
        # Check optional variables
        if not settings.ADMIN_ID:
            print("⚠️  ADMIN_ID not set - admin features will be disabled")
        else:
            print(f"✅ ADMIN_ID: {settings.ADMIN_ID}")
        
        print("\n✅ Environment validation completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing settings: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        return validate_environment()
    else:
        return setup_environment()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
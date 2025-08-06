#!/usr/bin/env python3
"""
Project Setup Script
Helps developers set up the project with the new organized structure.
"""

import os
import sys
import json
import shutil
from pathlib import Path

def create_config_example():
    """Create example configuration files"""
    print("📝 Creating example configuration files...")
    
    # Example config.json
    example_config = {
        "bot_token": "YOUR_BOT_TOKEN_HERE",
        "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
        "supabase_url": "YOUR_SUPABASE_URL_HERE",
        "supabase_key": "YOUR_SUPABASE_KEY_HERE",
        "environment": "development",
        "debug": True,
        "log_level": "INFO"
    }
    
    config_path = Path("config/config.json.example")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {config_path}")

def check_structure():
    """Check if the project structure is correct"""
    print("🔍 Checking project structure...")
    
    required_dirs = [
        "src",
        "config", 
        "scripts",
        "tests",
        "database",
        "docs",
        "pydosyalar",
        "locales"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ Project structure is correct")
        return True

def check_required_files():
    """Check if required files exist"""
    print("📋 Checking required files...")
    
    required_files = [
        "src/app.py",
        "src/bot.py",
        "config/config.json",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Missing files: {', '.join(missing_files)}")
        print("   Some files may need to be created manually")
        return False
    else:
        print("✅ All required files present")
        return True

def create_env_example():
    """Create .env.example file"""
    print("🌍 Creating .env.example file...")
    
    env_example = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Environment
ENVIRONMENT=development
DEBUG=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
"""
    
    with open(".env.example", 'w', encoding='utf-8') as f:
        f.write(env_example)
    
    print("✅ Created .env.example")

def main():
    """Main setup function"""
    print("🚀 FAL GRAM BOT PROJECT SETUP")
    print("=" * 50)
    
    # Check structure
    if not check_structure():
        print("\n❌ Project structure is incomplete. Please run the organization script first.")
        sys.exit(1)
    
    # Check files
    check_required_files()
    
    # Create example files
    create_config_example()
    create_env_example()
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE!")
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env and fill in your credentials")
    print("2. Copy config/config.json.example to config/config.json")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Set up database: psql -f database/COMPLETE_DATABASE_SETUP.sql")
    print("5. Run the bot: python src/app.py")
    print("\n📚 Check docs/ directory for detailed documentation")

if __name__ == "__main__":
    main()
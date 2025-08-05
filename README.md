# Telegram Bot Project

This is a Telegram bot project with organized file structure for better maintainability and development workflow.

## 📁 Project Structure

```
├── src/                    # Main source code
│   ├── app.py             # Main application entry point
│   └── bot.py             # Core bot implementation
│
├── config/                 # Configuration files
│   ├── config.json        # Main configuration
│   ├── user_data.json     # User data storage
│   └── prompts.json       # Bot prompts configuration
│
├── scripts/               # Utility and maintenance scripts
│   ├── add_deepseek_api.py
│   ├── add_rate_limiting.py
│   ├── complete_deepseek_fix.py
│   ├── fix_compatibility_and_rate_limit.py
│   └── fix_gemini_models.py
│
├── tests/                 # Test files
│   ├── test_bot_fix.py
│   ├── test_get_text.py
│   └── debug_test.py
│
├── database/              # Database scripts and migrations
│   ├── COMPLETE_DATABASE_SETUP.sql
│   ├── database_setup.sql
│   ├── premium_plans_setup.sql
│   └── [various update scripts]
│
├── docs/                  # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── CHANGELOG.md
│   ├── DEPLOYMENT.md
│   ├── PREMIUM_PLANS.md
│   ├── README.md
│   ├── RENDER_DEPLOYMENT.md
│   ├── ADMIN_PANEL.md
│   └── [version update summaries]
│
├── pydosyalar/           # Python utility modules
│   ├── check_prompts.py
│   ├── diagnostic.py
│   └── prompts.py
│
├── locales/              # Internationalization files
│   ├── en.json          # English
│   ├── es.json          # Spanish
│   ├── tr.json          # Turkish
│   └── pt.json.backup   # Portuguese (backup)
│
├── requirements.txt      # Python dependencies
├── .render.yaml         # Render deployment configuration
├── .gitattributes       # Git attributes
└── README.md           # This file
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the bot:**
   - Copy `config/config.json.example` to `config/config.json`
   - Update the configuration with your bot token and settings

3. **Set up the database:**
   ```bash
   # Run the complete database setup
   psql -f database/COMPLETE_DATABASE_SETUP.sql
   ```

4. **Run the bot:**
   ```bash
   python src/app.py
   ```

## 📚 Documentation

- **API Documentation:** `docs/API_DOCUMENTATION.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **Admin Panel:** `docs/ADMIN_PANEL.md`
- **Premium Plans:** `docs/PREMIUM_PLANS.md`
- **Changelog:** `docs/CHANGELOG.md`

## 🛠 Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Migrations
All database scripts are located in the `database/` directory. Run them in order:
1. `database_setup.sql` - Basic setup
2. `premium_plans_setup.sql` - Premium features
3. Various update scripts as needed

### Scripts
Utility scripts in the `scripts/` directory can be used for:
- Adding new API integrations
- Fixing compatibility issues
- Rate limiting configuration

## 🌍 Internationalization

The bot supports multiple languages through the `locales/` directory:
- English (`en.json`)
- Spanish (`es.json`)
- Turkish (`tr.json`)
- Portuguese (`pt.json.backup`)

## 📝 Notes

- The `pydosyalar/` directory contains Python utility modules for bot functionality
- Configuration files are centralized in the `config/` directory
- All documentation is organized in the `docs/` directory
- Database scripts are separated for easy maintenance and deployment

## 🔧 Maintenance

For regular maintenance tasks:
1. Check `docs/CHANGELOG.md` for recent updates
2. Review `docs/activity_log.md` for ongoing activities
3. Use scripts in `scripts/` directory for automated fixes
4. Run tests before deploying changes 
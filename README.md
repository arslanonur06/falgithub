# Telegram Bot Project

A comprehensive Telegram bot project with organized file structure.

## Project Structure

```
├── src/                    # Main source code
│   ├── app.py             # Main application entry point
│   ├── bot/               # Bot implementation
│   │   ├── __init__.py
│   │   └── bot.py         # Main bot logic
│   ├── config/            # Configuration files
│   │   ├── __init__.py
│   │   ├── config.json    # Main configuration
│   │   ├── prompts.json   # Bot prompts
│   │   └── user_data.json # User data configuration
│   └── utils/             # Utility modules
│       └── __init__.py
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_bot_fix.py
│   ├── test_get_text.py
│   └── debug_test.py
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── deployment/       # Deployment guides
│   ├── README.md         # Main documentation
│   ├── CHANGELOG.md      # Version history
│   ├── DEPLOYMENT.md     # Deployment instructions
│   ├── API_DOCUMENTATION.md
│   ├── ADMIN_PANEL.md
│   ├── PREMIUM_PLANS.md
│   └── ...               # Other documentation files
├── database/             # Database scripts
│   ├── COMPLETE_DATABASE_SETUP.sql
│   ├── database_setup.sql
│   ├── premium_plans_setup.sql
│   └── ...               # Other SQL files
├── scripts/              # Utility scripts
│   ├── add_deepseek_api.py
│   ├── add_rate_limiting.py
│   ├── complete_deepseek_fix.py
│   ├── fix_compatibility_and_rate_limit.py
│   └── fix_gemini_models.py
├── locales/              # Localization files
│   ├── en.json
│   ├── es.json
│   ├── tr.json
│   └── pt.json.backup
├── requirements.txt      # Python dependencies
├── .gitattributes       # Git configuration
└── README.md           # This file
```

## Directory Descriptions

### `src/` - Main Source Code
- **`app.py`**: Main application entry point
- **`bot/`**: Contains the main bot implementation
- **`config/`**: Configuration files and settings
- **`utils/`**: Utility functions and helper modules

### `tests/` - Test Files
Contains all test files for the project, including unit tests and debugging scripts.

### `docs/` - Documentation
- **`api/`**: API documentation
- **`deployment/`**: Deployment guides and configuration
- Various markdown files with project documentation

### `database/` - Database Scripts
Contains all SQL files for database setup, migrations, and updates.

### `scripts/` - Utility Scripts
Contains various utility scripts for adding features, fixing issues, and maintenance tasks.

### `locales/` - Localization
Contains JSON files for different language localizations.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the bot:
   - Edit `src/config/config.json` with your bot settings
   - Update `src/config/prompts.json` if needed

3. Set up the database:
   - Run the appropriate SQL scripts from the `database/` directory

4. Run the application:
   ```bash
   python src/app.py
   ```

## Development

- Add new bot features in `src/bot/`
- Configuration changes go in `src/config/`
- Utility functions belong in `src/utils/`
- Tests should be added to `tests/`
- Documentation updates go in `docs/`

## Contributing

1. Follow the established directory structure
2. Add tests for new features
3. Update documentation as needed
4. Use the appropriate directories for different types of files 
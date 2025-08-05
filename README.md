# Project Organization

This project has been organized into a clear, logical structure for better maintainability and development workflow.

## Directory Structure

```
├── src/                    # Main application source code
│   ├── app.py             # Main application entry point
│   ├── bot.py             # Core bot functionality
│   ├── check_prompts.py   # Prompt validation utilities
│   ├── diagnostic.py      # Diagnostic and debugging tools
│   └── prompts.py         # Prompt management utilities
│
├── tests/                 # Test files
│   ├── test_bot_fix.py    # Bot functionality tests
│   └── test_get_text.py   # Text processing tests
│
├── scripts/               # Utility and maintenance scripts
│   ├── add_deepseek_api.py
│   ├── add_rate_limiting.py
│   ├── complete_deepseek_fix.py
│   ├── debug_test.py
│   ├── fix_compatibility_and_rate_limit.py
│   └── fix_gemini_models.py
│
├── docs/                  # Documentation
│   ├── ADMIN_PANEL.md
│   ├── API_DOCUMENTATION.md
│   ├── CHANGELOG.md
│   ├── DEPLOYMENT.md
│   ├── PREMIUM_PLANS.md
│   ├── README.md
│   ├── RENDER_DEPLOYMENT.md
│   ├── V3.1.0_UPDATE_SUMMARY.md
│   ├── V3.1.1_UPDATE_SUMMARY.md
│   └── activity_log.md
│
├── data/                  # Data files and configuration
│   ├── config.json        # Application configuration
│   ├── prompts.json       # Bot prompts data
│   └── user_data.json     # User data storage
│
├── config/                # Deployment and environment configs
│   └── .render.yaml       # Render deployment configuration
│
├── locales/               # Internationalization files
│   ├── en.json           # English translations
│   ├── es.json           # Spanish translations
│   ├── tr.json           # Turkish translations
│   └── pt.json.backup    # Portuguese backup
│
├── sql/                   # Database scripts and migrations
│   ├── COMPLETE_DATABASE_SETUP.sql
│   ├── database_setup.sql
│   ├── premium_plans_setup.sql
│   └── [various update scripts]
│
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitattributes        # Git configuration
```

## Development Workflow

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python src/app.py
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_bot_fix.py
```

### Using Scripts
```bash
# Run utility scripts
python scripts/debug_test.py
python scripts/add_rate_limiting.py
```

### Database Management
```bash
# Execute database scripts
# (Use your preferred database client)
```

## Key Files

- **`src/app.py`**: Main application entry point
- **`src/bot.py`**: Core bot functionality and logic
- **`data/config.json`**: Application configuration
- **`requirements.txt`**: Python package dependencies
- **`config/.render.yaml`**: Deployment configuration for Render

## Contributing

1. Place new source code in the `src/` directory
2. Add tests to the `tests/` directory
3. Create utility scripts in the `scripts/` directory
4. Update documentation in the `docs/` directory
5. Store data files in the `data/` directory

## Notes

- The `locales/` directory contains internationalization files for multi-language support
- The `sql/` directory contains all database-related scripts and migrations
- Configuration files are separated between `data/` (application config) and `config/` (deployment config)
- All documentation has been moved to the `docs/` directory for better organization 
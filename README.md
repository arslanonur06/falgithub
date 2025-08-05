# 🔮 Fal Gram Bot

A comprehensive Telegram bot for astrology, fortune telling, and mystical services with a modern, modular architecture.

## 📁 Project Structure

```
fal-gram-bot/
├── 📁 src/
│   ├── 📁 handlers/          # Bot command and callback handlers
│   │   ├── __init__.py
│   │   ├── admin.py          # Admin command handlers
│   │   ├── astrology.py      # Astrology feature handlers
│   │   ├── fortune.py        # Fortune telling handlers
│   │   ├── payment.py        # Payment handlers
│   │   ├── referral.py       # Referral system handlers
│   │   └── user.py           # User management handlers
│   ├── 📁 keyboards/         # Inline and reply keyboard layouts
│   │   ├── __init__.py
│   │   ├── admin.py          # Admin keyboard layouts
│   │   ├── astrology.py      # Astrology keyboards
│   │   ├── fortune.py        # Fortune telling keyboards
│   │   ├── main.py           # Main menu keyboards
│   │   ├── payment.py        # Payment keyboards
│   │   └── referral.py       # Referral keyboards
│   ├── 📁 models/            # Data models and schemas
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   ├── referral.py       # Referral model
│   │   └── payment.py        # Payment model
│   ├── 📁 services/          # Business logic and external services
│   │   ├── __init__.py
│   │   ├── database.py       # Database service
│   │   ├── ai_service.py     # AI integration service
│   │   ├── payment_service.py # Payment processing
│   │   └── notification_service.py # Notification service
│   └── 📁 utils/             # Utility functions and helpers
│       ├── __init__.py
│       ├── i18n.py           # Internationalization
│       ├── helpers.py        # Helper functions
│       ├── validators.py     # Input validation
│       └── logger.py         # Logging utilities
├── 📁 config/                # Configuration files
│   ├── __init__.py
│   ├── settings.py           # Main configuration
│   ├── database.py           # Database configuration
│   └── logging.py            # Logging configuration
├── 📁 locales/               # Internationalization files
│   ├── en.json               # English translations
│   ├── tr.json               # Turkish translations
│   └── es.json               # Spanish translations
├── 📁 tests/                 # Test files
│   ├── __init__.py
│   ├── test_handlers.py
│   ├── test_services.py
│   └── test_utils.py
├── 📁 docs/                  # Documentation
│   ├── API.md                # API documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── CONTRIBUTING.md       # Contributing guide
├── 📁 scripts/               # Utility scripts
│   ├── setup_database.py     # Database setup script
│   ├── validate_translations.py # Translation validation
│   └── backup_data.py        # Data backup script
├── 📁 database/              # Database scripts and migrations
│   ├── COMPLETE_DATABASE_SETUP.sql
│   ├── database_setup.sql
│   └── [various update scripts]
├── main.py                   # Main bot entry point
├── app.py                    # Web service for health checks
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore file
└── README.md               # This file
```

## 🚀 Features

### 🌟 Core Features
- **Astrology Services**: Birth charts, daily/weekly/monthly horoscopes, compatibility analysis
- **Fortune Telling**: Tarot readings, coffee cup readings, dream interpretation
- **Multi-language Support**: English, Turkish, Spanish
- **Premium System**: Subscription-based premium features
- **Referral System**: User referral tracking and rewards

### 🛠 Technical Features
- **Modular Architecture**: Clean separation of concerns
- **Database Integration**: Supabase PostgreSQL backend
- **AI Integration**: Gemini and DeepSeek API support
- **Rate Limiting**: Built-in request throttling
- **Logging**: Comprehensive logging system
- **Testing**: Unit and integration tests
- **Internationalization**: Full i18n support

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database (Supabase recommended)
- Telegram Bot Token
- Gemini API Key
- Supabase credentials

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd fal-gram-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

Required environment variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
ENVIRONMENT=development
```

### 4. Database Setup

```bash
# Run database setup script
python scripts/setup_database.py
```

### 5. Run the Bot

```bash
# Start the bot
python main.py
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_utils.py
```

## 📚 Documentation

- **API Documentation**: `docs/API.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Contributing Guide**: `docs/CONTRIBUTING.md`

## 🏗 Architecture

### Core Components

#### Handlers (`src/handlers/`)
- **user.py**: User management, profile, settings
- **astrology.py**: Birth charts, horoscopes, compatibility
- **fortune.py**: Tarot, coffee readings, dream interpretation
- **payment.py**: Premium subscriptions, payment processing
- **referral.py**: Referral system management
- **admin.py**: Admin commands and moderation

#### Services (`src/services/`)
- **database.py**: Database operations and queries
- **ai_service.py**: AI API integrations (Gemini, DeepSeek)
- **payment_service.py**: Payment gateway integration
- **notification_service.py**: Push notifications and alerts

#### Models (`src/models/`)
- **user.py**: User data model and methods
- **referral.py**: Referral tracking model
- **payment.py**: Payment and subscription models

#### Utils (`src/utils/`)
- **i18n.py**: Internationalization and translations
- **helpers.py**: Common utility functions
- **validators.py**: Input validation and sanitization
- **logger.py**: Logging configuration and utilities

### Configuration (`config/`)
- **settings.py**: Main application settings
- **database.py**: Database connection settings
- **logging.py**: Logging configuration

## 🔧 Development

### Code Style
- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Adding New Features

1. **Create Handler**: Add new handler in `src/handlers/`
2. **Add Service**: Create service in `src/services/` if needed
3. **Update Models**: Add data models in `src/models/`
4. **Add Keyboards**: Create keyboard layouts in `src/keyboards/`
5. **Write Tests**: Add tests in `tests/`
6. **Update Translations**: Add new strings to locale files

### Database Migrations

```bash
# Create new migration
python scripts/create_migration.py

# Apply migrations
python scripts/apply_migrations.py
```

## 🌍 Internationalization

The bot supports multiple languages through the `locales/` directory:

```json
{
  "welcome": {
    "message": "Welcome to Fal Gram Bot! 🔮",
    "premium_user": "You are a premium user! ✨"
  },
  "menu": {
    "astrology": "🔮 Astrology",
    "fortune": "🔮 Fortune Telling"
  }
}
```

## 📊 Monitoring

### Health Checks
- **Web Service**: `http://localhost:5000/health`
- **Metrics**: `http://localhost:5000/metrics`
- **Status**: `http://localhost:5000/status`

### Logging
- **Development**: Console output
- **Production**: File logging in `logs/` directory
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚀 Deployment

### Render.com
```yaml
# .render.yaml
services:
  - type: web
    name: fal-gram-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

See `docs/CONTRIBUTING.md` for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check `docs/` directory
- **Discussions**: Use GitHub Discussions

## 🔮 Roadmap

- [ ] Advanced AI features
- [ ] More fortune telling methods
- [ ] Mobile app companion
- [ ] Advanced analytics
- [ ] API for third-party integrations
- [ ] More language support

---

**Made with ❤️ for the mystical community** 
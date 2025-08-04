# 🔮 Fal Gram Bot

A comprehensive Telegram bot for fortune telling, astrology, and mystical readings with premium features and referral system.

## ✨ Features

### 🔮 Core Features
- **☕ Coffee Fortune Reading** - Analyze coffee cup patterns
- **🎴 Tarot Card Reading** - Personal tarot card interpretations
- **💭 Dream Analysis** - Decode your subconscious messages
- **⭐ Astrology Center** - Daily, weekly, monthly horoscopes
- **🌙 Moon Calendar** - Lunar phase guidance and energy advice
- **💕 Compatibility Analysis** - Zodiac sign compatibility
- **🌟 Birth Chart Analysis** - Personal astrological map

### 💎 Premium Features
- **Unlimited Readings** - No daily limits
- **Advanced Astrology** - Detailed planetary analysis
- **VIP Chatbot** - 24/7 astrology assistant
- **Priority Support** - Faster response times
- **Exclusive Content** - Special readings and features

### 👥 Referral System
- **Earn Rewards** - Get free readings for referrals
- **Level System** - Progress through referral levels
- **Leaderboard** - Compete with other users
- **Special Perks** - Unlock exclusive features

### 🌐 Multi-Language Support
- **English** 🇺🇸
- **Turkish** 🇹🇷
- **Spanish** 🇪🇸

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fal-gram-bot
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional
ADMIN_ID=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 5. Run the Bot
```bash
python bot.py
```

## 🔧 Configuration

### Required Services

#### 1. Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token to your `.env` file

#### 2. Supabase Database
1. Create a [Supabase](https://supabase.com) account
2. Create a new project
3. Copy the project URL and anon key to your `.env` file
4. Set up the required database tables (see Database Schema below)

### Optional Services

#### AI APIs (for advanced features)
- **Google Gemini** - For AI-powered readings
- **DeepSeek** - Alternative AI provider

## 📊 Database Schema

The bot requires the following Supabase tables:

### Users Table
```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  last_name TEXT,
  language TEXT DEFAULT 'en',
  premium_plan TEXT DEFAULT 'free',
  premium_expires TIMESTAMP,
  referred_by BIGINT,
  referral_code TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Referrals Table
```sql
CREATE TABLE referrals (
  id SERIAL PRIMARY KEY,
  referrer_id BIGINT REFERENCES users(id),
  referred_id BIGINT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Logs Table
```sql
CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Usage

### Basic Commands
- `/start` - Start the bot and show main menu
- `/admin` - Admin panel (admin users only)
- `/gift` - Gift subscription (admin only)
- `/cancel` - Cancel subscription (admin only)

### User Flow
1. **Start** - User sends `/start` to begin
2. **Language** - Bot detects or user selects language
3. **Main Menu** - User chooses from available features
4. **Readings** - User gets personalized readings
5. **Premium** - User can upgrade for unlimited access
6. **Referrals** - User can invite friends for rewards

## 🔒 Security Features

- **Environment Variables** - Secure configuration management
- **Input Validation** - All user inputs are validated
- **Rate Limiting** - API call limits to prevent abuse
- **Error Handling** - Graceful error handling and logging
- **Admin Controls** - Restricted admin functions

## 🛠️ Development

### Project Structure
```
fal-gram-bot/
├── bot.py              # Main bot file
├── app.py              # Web service for health checks
├── locales/            # Translation files
│   ├── en.json         # English translations
│   ├── tr.json         # Turkish translations
│   └── es.json         # Spanish translations
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md          # This file
```

### Adding New Features
1. Add handler function in `bot.py`
2. Add callback data to keyboard creation
3. Add handler mapping in `handle_callback_query`
4. Add translations to all language files
5. Test thoroughly

### Adding New Languages
1. Create new JSON file in `locales/`
2. Add language detection in `detect_user_language()`
3. Add language button in `create_language_keyboard()`
4. Test translations

## 📈 Monitoring

The bot includes comprehensive logging:
- **User Actions** - All user interactions are logged
- **Errors** - Detailed error logging with context
- **Performance** - API response times and usage
- **Payments** - Payment success/failure tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Updates

The bot automatically updates:
- **Daily Cards** - New tarot cards every day
- **Moon Phases** - Real-time lunar information
- **Horoscopes** - Daily astrological updates

---

**Made with ❤️ for the mystical community**
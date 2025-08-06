# Fal Gram Bot - Deployment Guide

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in your project root with the following variables:

```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_admin_user_id

# AI API Keys
GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Payment (Telegram Stars)
TELEGRAM_PAYMENT_TOKEN=your_payment_provider_token

# Optional: Logging
LOG_LEVEL=INFO
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Ensure your Supabase database has the following tables:

```sql
-- Users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    language TEXT DEFAULT 'tr',
    premium_plan TEXT DEFAULT 'free',
    premium_expires_at TIMESTAMP,
    readings_count INTEGER DEFAULT 0,
    referred_count INTEGER DEFAULT 0,
    referral_earnings INTEGER DEFAULT 0,
    free_readings_earned INTEGER DEFAULT 0,
    stars_earned INTEGER DEFAULT 0,
    astro_subscribed BOOLEAN DEFAULT FALSE,
    state TEXT DEFAULT 'idle',
    payment_state TEXT,
    payment_amount INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prompts table
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    prompt_type TEXT NOT NULL,
    language TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prompt_type, language)
);

-- Tarot cards table
CREATE TABLE tarot_cards (
    id SERIAL PRIMARY KEY,
    card_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Logs table
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Run the Bot

```bash
python bot.py
```

## 🔧 Configuration

### Payment Provider Setup

1. **Telegram Stars**: Contact @BotFather to set up payment provider
2. **Get Payment Token**: Use the token provided by Telegram
3. **Test Payments**: Use test mode first

### AI API Setup

1. **Gemini API**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **DeepSeek API**: Get API key from [DeepSeek](https://platform.deepseek.com/)

### Database Configuration

1. **Supabase**: Create a new project at [supabase.com](https://supabase.com)
2. **API Keys**: Get URL and anon key from project settings
3. **Tables**: Run the SQL scripts above

## 🧪 Testing

Run the test script to verify all fixes:

```bash
python3 test_fixes.py
```

Expected output:
```
🎉 All tests passed! The fixes are working correctly.
```

## 📊 Monitoring

### Key Metrics to Monitor

1. **API Response Times**
   - Gemini API: Target < 6 seconds
   - DeepSeek API: Target < 8 seconds
   - Fallback usage: Should be < 10%

2. **User Engagement**
   - Daily active users
   - Feature usage (tarot, dreams, astrology)
   - Payment conversion rate

3. **Error Rates**
   - API failures
   - Payment failures
   - Language detection accuracy

### Logging

The bot includes comprehensive logging:

```python
# Check logs in Supabase
SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;
```

## 🛠️ Troubleshooting

### Common Issues

1. **Astrology Buttons Not Working**
   - Check callback data consistency
   - Verify locale files are complete
   - Test language detection

2. **Payment Not Working**
   - Verify TELEGRAM_PAYMENT_TOKEN is set
   - Check payment provider configuration
   - Test with small amounts first

3. **Slow Tarot Responses**
   - Monitor API response times
   - Check rate limiting
   - Verify fallback mechanisms

4. **Language Detection Issues**
   - Test with different languages
   - Check locale file completeness
   - Verify language switching logic

### Debug Commands

```bash
# Check environment variables
python -c "import os; print([k for k in os.environ if 'TELEGRAM' in k or 'API' in k])"

# Test locale files
python3 test_fixes.py

# Check bot status
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

## 🔄 Updates and Maintenance

### Regular Maintenance

1. **Weekly**
   - Check API usage and costs
   - Monitor error rates
   - Review user feedback

2. **Monthly**
   - Update AI prompts
   - Review performance metrics
   - Backup database

3. **Quarterly**
   - Update dependencies
   - Review security settings
   - Plan new features

### Performance Optimization

1. **Caching**: Implement response caching for common queries
2. **Rate Limiting**: Monitor and adjust rate limits
3. **API Optimization**: Use fastest available models
4. **Database**: Optimize queries and indexes

## 📈 Scaling

### Horizontal Scaling

1. **Multiple Instances**: Run multiple bot instances
2. **Load Balancing**: Use reverse proxy
3. **Database**: Consider read replicas

### Vertical Scaling

1. **Resources**: Increase CPU/memory
2. **Concurrency**: Adjust worker threads
3. **Caching**: Add Redis for caching

## 🔒 Security

### Best Practices

1. **API Keys**: Rotate regularly
2. **Access Control**: Limit admin access
3. **Data Privacy**: Follow GDPR guidelines
4. **Monitoring**: Set up security alerts

### Security Checklist

- [ ] Environment variables secured
- [ ] API keys rotated
- [ ] Database access limited
- [ ] Payment security verified
- [ ] Logs don't contain sensitive data
- [ ] Admin access restricted

## 📞 Support

### Getting Help

1. **Documentation**: Check this guide first
2. **Logs**: Review error logs
3. **Testing**: Run test script
4. **Community**: Check Telegram groups

### Emergency Contacts

- **Bot Issues**: Check @BotFather
- **Payment Issues**: Contact payment provider
- **API Issues**: Check API provider status pages

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] Database tables created
- [ ] API keys obtained
- [ ] Payment provider set up
- [ ] Locale files verified
- [ ] Test script passed
- [ ] Bot token configured
- [ ] Admin ID set
- [ ] Monitoring configured
- [ ] Security measures implemented

**Status**: Ready for deployment! 🚀
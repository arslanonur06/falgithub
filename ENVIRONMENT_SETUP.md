# 🔧 Environment Setup Guide

This guide will help you set up all the required environment variables for the Fal Gram Bot.

## 📋 Required Environment Variables

### 🤖 Bot Configuration

#### `TELEGRAM_BOT_TOKEN`
**Required**: Your Telegram Bot Token from @BotFather

**How to get it:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 👤 Admin Configuration

#### `ADMIN_ID`
**Optional but recommended**: Your Telegram User ID for admin access

**How to get it:**
1. Send a message to `@userinfobot` on Telegram
2. It will reply with your User ID (a number like `123456789`)
3. Copy this number

**Alternative methods:**
- Send a message to `@RawDataBot` and look for `"id":` in the response
- Use `@getidsbot` to get your User ID

### 💳 Payment Configuration

#### `PAYMENT_PROVIDER_TOKEN`
**Required**: Telegram Stars Provider Token for payments

**How to get it:**
1. Contact Telegram Support for Stars integration
2. Request a Provider Token for your bot
3. This token allows your bot to accept Telegram Stars payments

**Note**: This is required for premium features and payments to work.

### 🔑 API Keys

#### `GEMINI_API_KEY`
**Required**: Google Gemini AI API Key

**How to get it:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

#### `DEEPSEEK_API_KEY`
**Optional**: DeepSeek AI API Key (alternative AI provider)

**How to get it:**
1. Go to [DeepSeek AI](https://platform.deepseek.com/)
2. Sign up and create an account
3. Navigate to API Keys section
4. Generate a new API key

### 🗄️ Database Configuration

#### `SUPABASE_URL`
**Required**: Your Supabase project URL

**How to get it:**
1. Go to [Supabase](https://supabase.com/)
2. Create a new project or use existing one
3. Go to Settings → API
4. Copy the "Project URL"

#### `SUPABASE_KEY`
**Required**: Your Supabase anonymous key

**How to get it:**
1. In your Supabase project, go to Settings → API
2. Copy the "anon public" key (starts with `eyJ...`)

## 🚀 Quick Setup

### Option 1: Interactive Setup (Recommended)

Run the interactive setup script:

```bash
python setup_env.py
```

This will guide you through setting up all environment variables step by step.

### Option 2: Manual Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and replace the placeholder values with your actual tokens and keys.

### Option 3: Environment Variables

Set the variables directly in your environment:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export ADMIN_ID="your_user_id"
export PAYMENT_PROVIDER_TOKEN="your_provider_token"
export GEMINI_API_KEY="your_gemini_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

## ✅ Validation

After setting up your environment variables, validate the configuration:

```bash
python setup_env.py validate
```

This will check if all required variables are set correctly.

## 🔒 Security Notes

- **Never commit your `.env` file** to version control
- **Keep your tokens secure** and don't share them
- **Use different tokens** for development and production
- **Rotate your API keys** regularly for security

## 📁 File Structure

```
fal-gram-bot/
├── .env                    # Your environment variables (create this)
├── .env.example           # Template file
├── setup_env.py           # Interactive setup script
└── config/
    └── settings.py        # Settings configuration
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Make sure all required variables are set in your `.env` file
   - Check that the file is in the correct location (project root)

2. **"Payment provider token not configured"**
   - Ensure `PAYMENT_PROVIDER_TOKEN` is set correctly
   - Contact Telegram Support if you don't have a provider token

3. **"Admin features disabled"**
   - Set `ADMIN_ID` to your Telegram User ID
   - Make sure the User ID is correct (numeric value)

4. **"Invalid bot token"**
   - Verify your bot token from @BotFather
   - Make sure there are no extra spaces or characters

### Getting Help

If you encounter issues:

1. Run the validation script: `python setup_env.py validate`
2. Check the error messages for specific missing variables
3. Ensure all tokens and keys are valid and active
4. Contact support if you need help with specific services

## 🎯 Next Steps

After setting up your environment variables:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your database** (if using Supabase):
   - Create the required tables
   - Set up authentication if needed

3. **Test the bot**:
   ```bash
   python main_new.py
   ```

4. **Deploy to production** (optional):
   - Set up webhooks for production
   - Configure production environment variables

---

**✅ Your environment is now ready for the Fal Gram Bot!**
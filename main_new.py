"""
Main entry point for the Fal Gram Bot with modular structure.
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    PreCheckoutQueryHandler, filters, ContextTypes
)

# Load environment variables
load_dotenv()

# Import configuration
from config.settings import settings
from config.logging import setup_logging

# Import services
from src.services.database import db_service
from src.services.ai_service import ai_service
from src.services.payment_service import payment_service

# Import handlers
from src.handlers.user import UserHandlers
from src.handlers.astrology import astrology_handlers
from src.handlers.fortune import fortune_handlers
from src.handlers.payment import payment_handlers
from src.handlers.admin import admin_handlers
from src.handlers.referral import referral_handlers

# Import utilities
from src.utils.i18n import i18n
from src.utils.logger import get_logger

# Setup logging
setup_logging()
logger = get_logger("main")

# Initialize services
async def initialize_services():
    """Initialize all services."""
    try:
        # Initialize database service
        await db_service.initialize()
        logger.info("Database service initialized")
        
        # Test AI service connections
        ai_connections = await ai_service.test_connection()
        logger.info(f"AI service connections: {ai_connections}")
        
        # Load translations
        i18n.load_translations()
        logger.info("Translations loaded")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

async def post_init(application: Application):
    """Post initialization tasks."""
    logger.info("Bot initialized successfully")
    
    # Initialize services
    await initialize_services()

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query handler that routes to specific handlers."""
    query = update.callback_query
    data = query.data
    
    try:
        # Route to appropriate handler based on callback data
        if data.startswith("main_menu"):
            await UserHandlers.show_main_menu(update, context)
        
        # Astrology handlers
        elif data.startswith("astrology"):
            await astrology_handlers.show_astrology_menu(update, context)
        elif data.startswith("birth_chart"):
            await astrology_handlers.handle_birth_chart(update, context)
        elif data.startswith("daily_horoscope"):
            await astrology_handlers.handle_daily_horoscope(update, context)
        elif data.startswith("weekly_horoscope"):
            await astrology_handlers.handle_weekly_horoscope(update, context)
        elif data.startswith("monthly_horoscope"):
            await astrology_handlers.handle_monthly_horoscope(update, context)
        elif data.startswith("compatibility"):
            await astrology_handlers.handle_compatibility(update, context)
        elif data.startswith("moon_calendar"):
            await astrology_handlers.handle_moon_calendar(update, context)
        elif data.startswith("zodiac_") or data.startswith("daily_horoscope_") or data.startswith("weekly_horoscope_") or data.startswith("monthly_horoscope_"):
            await astrology_handlers.handle_zodiac_selection(update, context)
        elif data.startswith("compat_"):
            await astrology_handlers.handle_compatibility_selection(update, context)
        
        # Fortune handlers
        elif data.startswith("fortune"):
            await fortune_handlers.show_fortune_menu(update, context)
        elif data.startswith("tarot_reading"):
            await fortune_handlers.handle_tarot_reading(update, context)
        elif data.startswith("coffee_reading"):
            await fortune_handlers.handle_coffee_reading(update, context)
        elif data.startswith("dream_interpretation"):
            await fortune_handlers.handle_dream_interpretation(update, context)
        elif data.startswith("palm_reading"):
            await fortune_handlers.handle_palm_reading(update, context)
        
        # Payment handlers
        elif data.startswith("premium"):
            await payment_handlers.show_premium_menu(update, context)
        elif data.startswith("plan_details_"):
            await payment_handlers.show_plan_details(update, context)
        elif data.startswith("buy_plan_"):
            await payment_handlers.initiate_purchase(update, context)
        elif data.startswith("subscription_management"):
            await payment_handlers.show_subscription_management(update, context)
        elif data.startswith("cancel_subscription"):
            await payment_handlers.cancel_subscription(update, context)
        elif data.startswith("confirm_cancellation"):
            await payment_handlers.confirm_cancellation(update, context)
        
        # Admin handlers
        elif data.startswith("admin_"):
            await admin_handlers.handle_admin_callback(update, context)
        
        # Referral handlers
        elif data.startswith("referral"):
            await referral_handlers.show_referral_menu(update, context)
        elif data.startswith("referral_info"):
            await referral_handlers.show_referral_info(update, context)
        elif data.startswith("referral_stats"):
            await referral_handlers.show_referral_stats(update, context)
        elif data.startswith("referral_leaderboard"):
            await referral_handlers.show_referral_leaderboard(update, context)
        elif data.startswith("referral_rewards"):
            await referral_handlers.show_referral_rewards(update, context)
        elif data.startswith("share_referral"):
            await referral_handlers.share_referral_link(update, context)
        elif data.startswith("copy_referral_link"):
            await UserHandlers.handle_copy_referral_link(update, context)
        
        # User handlers
        elif data.startswith("profile"):
            await UserHandlers.show_profile(update, context)
        elif data.startswith("language"):
            await UserHandlers.show_language_menu(update, context)
        elif data.startswith("set_lang_"):
            await UserHandlers.handle_language_change(update, context)
        elif data.startswith("help"):
            await UserHandlers.show_help(update, context)
        
        # Back buttons
        elif data.startswith("back_to_"):
            await UserHandlers.handle_back_button(update, context)
        
        else:
            # Default to user handler
            await UserHandlers.handle_callback_query(update, context)
    
    except Exception as e:
        logger.error(f"Error handling callback query {data}: {e}")
        await UserHandlers.error_handler(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    try:
        # Check if user is waiting for input
        user_data = context.user_data
        waiting_for = user_data.get('waiting_for')
        
        if waiting_for:
            # Route to appropriate handler based on what we're waiting for
            if waiting_for in ['coffee_photo', 'palm_photo']:
                await fortune_handlers.handle_photo_input(update, context)
            elif waiting_for == 'dream_text':
                await fortune_handlers.handle_text_input(update, context)
            else:
                # Default message handling
                await UserHandlers.handle_message(update, context)
        else:
            # Default message handling
            await UserHandlers.handle_message(update, context)
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await UserHandlers.error_handler(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages."""
    try:
        # Route to fortune handlers for photo processing
        await fortune_handlers.handle_photo_input(update, context)
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await UserHandlers.error_handler(update, context)

async def handle_pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout queries."""
    try:
        await payment_handlers.handle_pre_checkout(update, context)
    except Exception as e:
        logger.error(f"Error handling pre-checkout: {e}")

async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payments."""
    try:
        await payment_handlers.handle_successful_payment(update, context)
    except Exception as e:
        logger.error(f"Error handling successful payment: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler."""
    try:
        await UserHandlers.error_handler(update, context)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def main():
    """Main function to start the bot."""
    try:
        # Create application
        application = Application.builder().token(settings.BOT_TOKEN).post_init(post_init).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", UserHandlers.start_command))
        application.add_handler(CommandHandler("help", UserHandlers.help_command))
        application.add_handler(CommandHandler("profile", UserHandlers.profile_command))
        application.add_handler(CommandHandler("language", UserHandlers.language_command))
        
        # Admin command handlers
        application.add_handler(CommandHandler("admin", admin_handlers.admin_command))
        application.add_handler(CommandHandler("gift", admin_handlers.gift_command))
        application.add_handler(CommandHandler("cancel", admin_handlers.cancel_command))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Payment handlers
        application.add_handler(PreCheckoutQueryHandler(handle_pre_checkout))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Run bot
        logger.info("Bot starting...")
        
        if settings.ENVIRONMENT == 'production':
            # Production mode with webhook
            if settings.WEBHOOK_URL:
                application.run_webhook(
                    listen="0.0.0.0",
                    port=int(os.environ.get('PORT', 8080)),
                    url_path=settings.BOT_TOKEN,
                    webhook_url=f"{settings.WEBHOOK_URL}/{settings.BOT_TOKEN}"
                )
            else:
                logger.error("WEBHOOK_URL not set for production!")
        else:
            # Development mode with polling
            application.run_polling(drop_pending_updates=True)
    
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    # Start web service in separate thread if needed
    try:
        from app import start_web_service
        start_web_service()
    except ImportError:
        logger.info("Web service not available")
    
    # Run the bot
    main()
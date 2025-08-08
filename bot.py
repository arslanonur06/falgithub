import os
import logging
from typing import Callable, Awaitable, Dict

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, PreCheckoutQueryHandler, filters
)

# Use centralized settings and i18n
from config.settings import settings
from src.utils.i18n import i18n
from src.utils.logger import setup_logger

# Handlers (modularized)
from src.handlers.user import UserHandlers
from src.handlers.payment import PaymentHandlers
from src.handlers.referral import ReferralHandlers
from src.handlers.astrology import AstrologyHandlers
from src.handlers.admin import AdminHandlers

# Keyboards (for thin compat wrappers)
from src.keyboards.main import MainKeyboards
from src.keyboards.admin import AdminKeyboards


# --- Logging & Config ---
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = setup_logger(__name__)


# --- Backwards-compatible wrappers (kept for tests/tools expecting old API) ---
# Expose loaded locales and a simple get_text function compatible with old calls
LOCALES: Dict[str, Dict] = i18n.translations

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    text = i18n.get_text(key, lang)
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text

# Old helpers expected by some scripts

def create_main_menu_keyboard(lang: str = "en"):
    return MainKeyboards.get_main_menu_keyboard(lang)

def create_admin_panel_keyboard(lang: str = "en"):
    # Old name → new keyboard provider
    return AdminKeyboards.get_admin_menu_keyboard(lang)


# --- Router utilities ---
async def route_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route text messages based on lightweight state in context."""
    # Fortune flow waits for user input via context.user_data['waiting_for']
    waiting_for = context.user_data.get("waiting_for") if context and context.user_data else None
    if waiting_for:
        # Delegate to fortune handler text processing
        from src.handlers.fortune import FortuneHandlers
        await FortuneHandlers.handle_text_input(update, context)
        return
    # Default user message handler
    await UserHandlers.handle_message(update, context)


async def route_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.handlers.fortune import FortuneHandlers
    await FortuneHandlers.handle_photo_input(update, context)


async def route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all callback queries to their respective modular handlers."""
    query = update.callback_query
    if not query:
        return
    data = query.data or ""

    # Admin callbacks (delegate to admin router)
    if data.startswith("admin_") or data in {"back_to_admin"}:
        await AdminHandlers.handle_admin_callback(update, context)
        return

    # Language change
    if data.startswith("set_lang_"):
        await UserHandlers.handle_language_change(update, context)
        return

    # Main navigation mapping
    mapping: Dict[str, Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]] = {
        # User
        "main_menu": UserHandlers.show_main_menu,
        "profile": UserHandlers.show_profile,
        "help": UserHandlers.show_help,
        "language": UserHandlers.show_language_menu,
        # Profile actions
        "edit_profile": UserHandlers.show_edit_profile,
        "usage_stats": UserHandlers.show_usage_stats,
        # Sections
        "astrology": AstrologyHandlers.show_astrology_menu,
        "fortune": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.show_fortune_menu,
        "referral": ReferralHandlers.show_referral_menu,
        "premium": PaymentHandlers.show_premium_menu,
        "premium_info": PaymentHandlers.show_premium_info,
        # Referral
        "referral_info": ReferralHandlers.show_referral_info,
        "referral_stats": ReferralHandlers.show_referral_stats,
        "referral_leaderboard": ReferralHandlers.show_referral_leaderboard,
        "referral_rewards": ReferralHandlers.show_referral_rewards,
        "referral_share": ReferralHandlers.show_referral_share,
        "copy_referral_link": UserHandlers.handle_copy_referral_link,
        "share_telegram": ReferralHandlers.handle_share_telegram,
        "share_whatsapp": ReferralHandlers.handle_share_whatsapp,
        "share_twitter": ReferralHandlers.handle_share_twitter,
        # Premium
        "premium_plans": PaymentHandlers.show_premium_plans,
        "plan_details_basic": PaymentHandlers.show_plan_details,
        "plan_details_premium": PaymentHandlers.show_plan_details,
        "plan_details_vip": PaymentHandlers.show_plan_details,
        "subscription_management": PaymentHandlers.show_subscription_management,
        "subscription_status": PaymentHandlers.show_subscription_management,
        "usage_statistics": PaymentHandlers.show_usage_statistics,
        "toggle_auto_renew": PaymentHandlers.toggle_auto_renew,
        "cancel_subscription": PaymentHandlers.handle_cancel_subscription,
        # Fortune
        "tarot_fortune": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_tarot_reading,
        "tarot_rider_waite": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_tarot_option,
        "tarot_celtic_cross": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_tarot_option,
        "tarot_three_card": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_tarot_option,
        "tarot_daily_card": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_tarot_option,
        "coffee_fortune": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_coffee_reading,
        "dream_fortune": __import__("src.handlers.fortune", fromlist=["FortuneHandlers"]).FortuneHandlers.handle_dream_interpretation,
        # Astrology
        "daily_horoscope": AstrologyHandlers.handle_daily_horoscope,
        "weekly_horoscope": AstrologyHandlers.handle_weekly_horoscope,
        "monthly_horoscope": AstrologyHandlers.handle_monthly_horoscope,
        "birth_chart": AstrologyHandlers.handle_birth_chart,
        "moon_calendar": AstrologyHandlers.handle_moon_calendar,
        # Horoscope period quick picks
        "horoscope_daily": AstrologyHandlers.handle_daily_horoscope,
        "horoscope_weekly": AstrologyHandlers.handle_weekly_horoscope,
        "horoscope_monthly": AstrologyHandlers.handle_monthly_horoscope,
        # Generic
        "cancel": UserHandlers.show_main_menu,
    }

    if data in mapping:
        await mapping[data](update, context)
        return

    # Pattern routes
    if data.startswith("plan_"):
        await PaymentHandlers.handle_plan_selection(update, context)
        return

    if data.startswith("pay_"):
        await PaymentHandlers.handle_payment(update, context)
        return

    if data.startswith("daily_horoscope_") or data.startswith("weekly_horoscope_") or data.startswith("monthly_horoscope_"):
        await AstrologyHandlers.handle_zodiac_selection(update, context)
        return

    if data.startswith("compat_"):
        await AstrologyHandlers.handle_compatibility_selection(update, context)
        return

    # Fallback to main menu
    await UserHandlers.show_main_menu(update, context)


# --- Payment webhooks (minimal stubs using Telegram payments) ---
async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.pre_checkout_query:
        await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # For now, simply confirm payment and show premium menu
    await PaymentHandlers.show_subscription_management(update, context)


def main() -> None:
    """Application entrypoint."""
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured. Check your environment variables.")
        raise SystemExit(1)

    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", UserHandlers.start_command))
    application.add_handler(CommandHandler("admin", AdminHandlers.admin_command))
    application.add_handler(CommandHandler("gift", AdminHandlers.gift_command))
    application.add_handler(CommandHandler("cancel", AdminHandlers.cancel_command))

    # Callbacks
    application.add_handler(CallbackQueryHandler(route_callback))

    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, route_photo_message))

    # Payments
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    logger.info("Starting Fal Gram bot (%s)...", settings.BOT_VERSION)

    if settings.ENVIRONMENT == "production" and settings.WEBHOOK_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", settings.WEBHOOK_PORT)),
            url_path=settings.BOT_TOKEN,
            webhook_url=f"{settings.WEBHOOK_URL}/{settings.BOT_TOKEN}"
        )
    else:
        application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

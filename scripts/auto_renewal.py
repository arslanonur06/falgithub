"""
Daily auto-renewal helper.

Run this script daily (e.g., via cron) to:
- Find users with auto_renew_enabled
- Send renewal reminders 3 days and 1 day before expiry
- On expiry, send a renewal prompt with Pay button

This does NOT auto-charge Stars (Telegram does not support background charging).
It provides one-tap renewal via inline callback to the existing payment handler.
"""

from datetime import datetime, timedelta
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot

from config.settings import settings
from src.services.database import db_service
from src.services.payment_service import payment_service
from src.utils.i18n import i18n
from src.utils.logger import get_logger

logger = get_logger("auto_renewal")


def _parse_iso(dt: Optional[str]) -> Optional[datetime]:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt)
    except Exception:
        return None


async def run() -> None:
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN not configured; cannot send reminders.")
        return

    bot = Bot(token=settings.BOT_TOKEN)
    users = await db_service.get_all_users() or []
    now = datetime.now()

    for user in users:
        try:
            if not user.get("auto_renew_enabled"):
                continue

            user_id = user.get("user_id") or user.get("id")
            if not user_id:
                continue

            plan = (user.get("premium_plan") or "").lower()
            if plan not in {"basic", "premium", "vip"}:
                continue

            expires_at = _parse_iso(user.get("premium_expires_at"))
            if not expires_at:
                continue

            days_left = (expires_at.date() - now.date()).days
            # Trigger on 3, 1, 0, -1 days
            if days_left not in {3, 1, 0, -1}:
                continue

            language = user.get("language", "en")
            # Build message
            if days_left > 0:
                msg = (
                    f"💎 {i18n.get_text('premium_plans.title', language)}\n\n"
                    f"⏰ Expires in {days_left} day(s). Renew now to keep premium features."
                )
            elif days_left == 0:
                msg = (
                    f"💎 {i18n.get_text('premium_plans.title', language)}\n\n"
                    f"⏰ Expires today. Renew now to avoid interruption."
                )
            else:
                msg = (
                    f"💎 {i18n.get_text('premium_plans.title', language)}\n\n"
                    f"❌ Subscription expired. Renew to regain access."
                )

            # Build pay button
            pay_label = i18n.get_text("premium.telegram_stars_payment", language)
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(pay_label, callback_data=f"pay_{plan}")]]
            )

            await bot.send_message(chat_id=user_id, text=msg, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Auto-renew notification failed for user {user.get('user_id')}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())



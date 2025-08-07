"""
Payment keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for premium and payment features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class PaymentKeyboards:
    """Payment keyboard layouts."""
    
    @staticmethod
    def get_premium_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("premium_compare", language),
                    callback_data="premium_compare"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("premium_menu", language),
                    callback_data="premium_plans"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("subscription_management", language),
                    callback_data="subscription_management"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_premium_plans_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium plans keyboard."""
        basic_label = f"{i18n.get_text('premium_plans.plans.basic.name', language)} - {i18n.get_text('premium_plans.plans.basic.price', language)}"
        premium_label = f"{i18n.get_text('premium_plans.plans.premium.name', language)} - {i18n.get_text('premium_plans.plans.premium.price', language)}"
        vip_label = f"{i18n.get_text('premium_plans.plans.vip.name', language)} - {i18n.get_text('premium_plans.plans.vip.price', language)}"
        keyboard = [
            [
                InlineKeyboardButton(
                    basic_label,
                    callback_data="plan_basic"
                )
            ],
            [
                InlineKeyboardButton(
                    premium_label,
                    callback_data="plan_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    vip_label,
                    callback_data="plan_vip"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.compare_plans", language),
                    callback_data="premium_compare"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.back_to_menu", language),
                    callback_data="premium"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_subscription_management_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get subscription management keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("subscription_management", language),
                    callback_data="subscription_status"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("cancel_subscription", language),
                    callback_data="cancel_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("statistics", language),
                    callback_data="usage_statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.back_to_premium", language),
                    callback_data="premium"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_confirmation_keyboard(plan_name: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get payment confirmation keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.telegram_stars_payment", language),
                    callback_data=f"pay_{plan_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.back_to_plans", language),
                    callback_data="premium_plans"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get payment back keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("buttons.back_to_premium", language),
                    callback_data="premium"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
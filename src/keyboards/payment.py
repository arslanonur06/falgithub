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
                    i18n.get_text("payment.premium_plans", language),
                    callback_data="premium_plans"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.subscription_management", language),
                    callback_data="subscription_management"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_premium_plans_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium plans keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "💎 Basic Plan - 500 TRY",
                    callback_data="plan_basic"
                )
            ],
            [
                InlineKeyboardButton(
                    "💎 Premium Plan - 1000 TRY",
                    callback_data="plan_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    "💎 VIP Plan - 2000 TRY",
                    callback_data="plan_vip"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
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
                    "📊 Subscription Status",
                    callback_data="subscription_status"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel Subscription",
                    callback_data="cancel_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    "📈 Usage Statistics",
                    callback_data="usage_statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
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
                    "💳 Pay with Telegram Stars",
                    callback_data=f"pay_{plan_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.cancel", language),
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
                    i18n.get_text("common.back", language),
                    callback_data="premium"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
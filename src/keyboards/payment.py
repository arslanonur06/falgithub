"""
Payment keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n

class PaymentKeyboards:
    """Payment keyboard layouts."""
    
    @staticmethod
    def get_premium_plans_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium plans keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.plans.basic.name", language),
                    callback_data="plan_details_basic"
                ),
                InlineKeyboardButton(
                    i18n.get_text("premium.plans.premium.name", language),
                    callback_data="plan_details_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.plans.vip.name", language),
                    callback_data="plan_details_vip"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.compare_plans", language),
                    callback_data="compare_plans"
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
    def get_plan_details_keyboard(language: str = "en", plan_name: str = "premium") -> InlineKeyboardMarkup:
        """Get plan details keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.buy_now", language),
                    callback_data=f"buy_plan_{plan_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.compare_plans", language),
                    callback_data="compare_plans"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="premium_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_premium_user_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium user keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.manage_subscription", language),
                    callback_data="subscription_management"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.view_usage", language),
                    callback_data="view_usage"
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
    def get_subscription_management_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get subscription management keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.cancel_subscription", language),
                    callback_data="cancel_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.change_plan", language),
                    callback_data="change_plan"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.billing_history", language),
                    callback_data="billing_history"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="premium_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_cancel_confirmation_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get cancellation confirmation keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("payment.confirm_cancellation", language),
                    callback_data="confirm_cancellation"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.cancel", language),
                    callback_data="subscription_management"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_premium_upgrade_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get premium upgrade keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("premium.upgrade_now", language),
                    callback_data="premium_menu"
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
    def get_support_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get support keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("support.contact", language),
                    callback_data="contact_support"
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
    def get_main_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.main", language),
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button(language: str = "en", callback_data: str = "premium_menu") -> InlineKeyboardMarkup:
        """Get back button keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data=callback_data
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
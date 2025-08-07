"""
Referral keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for referral system features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class ReferralKeyboards:
    """Referral keyboard layouts."""
    
    @staticmethod
    def get_referral_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.stats", language),
                    callback_data="referral_stats"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.rewards", language),
                    callback_data="referral_rewards"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.copy", language),
                    callback_data="copy_referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.telegram", language),
                    callback_data="share_telegram"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.whatsapp", language),
                    callback_data="share_whatsapp"
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
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_referral_share_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral share keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.copy", language),
                    callback_data="copy_referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.telegram", language),
                    callback_data="share_telegram"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral_system.main_panel.buttons.whatsapp", language),
                    callback_data="share_whatsapp"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.stats_panel.back_button", language),
                    callback_data="referral"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_referral_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral back keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.stats_panel.back_button", language),
                    callback_data="referral"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
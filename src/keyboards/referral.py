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
                    i18n.get_text("referral.my_info", language),
                    callback_data="referral_info"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral.stats", language),
                    callback_data="referral_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.leaderboard", language),
                    callback_data="referral_leaderboard"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral.rewards", language),
                    callback_data="referral_rewards"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.share", language),
                    callback_data="referral_share"
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
    def get_referral_share_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral share keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.copy_link", language),
                    callback_data="copy_referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.share_telegram", language),
                    callback_data="share_telegram"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral.share_whatsapp", language),
                    callback_data="share_whatsapp"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
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
                    i18n.get_text("common.back", language),
                    callback_data="referral"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
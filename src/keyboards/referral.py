"""
Referral keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n

class ReferralKeyboards:
    """Referral keyboard layouts."""
    
    @staticmethod
    def get_referral_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral menu keyboard."""
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
                    callback_data="share_referral"
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
    def get_referral_info_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral info keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.copy_link", language),
                    callback_data="copy_referral_link"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral.share", language),
                    callback_data="share_referral"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.stats", language),
                    callback_data="referral_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="referral_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_share_keyboard(language: str = "en", referral_link: str = "") -> InlineKeyboardMarkup:
        """Get share keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.share_telegram", language),
                    url=f"https://t.me/share/url?url={referral_link}&text={i18n.get_text('referral.share_text', language)}"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.share_whatsapp", language),
                    url=f"https://wa.me/?text={i18n.get_text('referral.share_text', language)}%20{referral_link}"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral.copy_link", language),
                    callback_data="copy_referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="referral_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button(language: str = "en", callback_data: str = "referral_menu") -> InlineKeyboardMarkup:
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
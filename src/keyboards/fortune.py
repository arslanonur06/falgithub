"""
Fortune telling keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n

class FortuneKeyboards:
    """Fortune telling keyboard layouts."""
    
    @staticmethod
    def get_fortune_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get fortune telling menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("fortune.tarot", language),
                    callback_data="tarot_reading"
                ),
                InlineKeyboardButton(
                    i18n.get_text("fortune.coffee", language),
                    callback_data="coffee_reading"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("fortune.dream", language),
                    callback_data="dream_interpretation"
                ),
                InlineKeyboardButton(
                    i18n.get_text("fortune.palm", language),
                    callback_data="palm_reading"
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
                    callback_data="fortune_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button(language: str = "en", callback_data: str = "fortune_menu") -> InlineKeyboardMarkup:
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
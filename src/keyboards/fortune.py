"""
Fortune keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for fortune-telling features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class FortuneKeyboards:
    """Fortune keyboard layouts."""
    
    @staticmethod
    def get_fortune_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get fortune main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("fortune.coffee_reading", language),
                    callback_data="coffee_fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("fortune.tarot_reading", language),
                    callback_data="tarot_fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("fortune.dream_interpretation", language),
                    callback_data="dream_fortune"
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
    def get_tarot_deck_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get tarot deck selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "🃏 Rider-Waite",
                    callback_data="tarot_rider_waite"
                ),
                InlineKeyboardButton(
                    "🃏 Celtic Cross",
                    callback_data="tarot_celtic_cross"
                )
            ],
            [
                InlineKeyboardButton(
                    "🃏 Three Card Spread",
                    callback_data="tarot_three_card"
                ),
                InlineKeyboardButton(
                    "🃏 Daily Card",
                    callback_data="tarot_daily_card"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="fortune"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_fortune_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get fortune back keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="fortune"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
"""
Main keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, List
from src.utils.i18n import i18n

class MainKeyboards:
    """Main keyboard layouts."""
    
    @staticmethod
    def get_main_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.astrology", language),
                    callback_data="astrology_menu"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.fortune", language),
                    callback_data="fortune_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.profile", language),
                    callback_data="profile_menu"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.settings", language),
                    callback_data="settings_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.premium", language),
                    callback_data="premium_menu"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.referral", language),
                    callback_data="referral_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.help", language),
                    callback_data="help_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_astrology_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get astrology menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.birth_chart", language),
                    callback_data="birth_chart"
                ),
                InlineKeyboardButton(
                    i18n.get_text("astrology.daily_horoscope", language),
                    callback_data="daily_horoscope"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.weekly_horoscope", language),
                    callback_data="weekly_horoscope"
                ),
                InlineKeyboardButton(
                    i18n.get_text("astrology.monthly_horoscope", language),
                    callback_data="monthly_horoscope"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.compatibility", language),
                    callback_data="compatibility"
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
    def get_profile_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get profile menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("profile.edit_info", language),
                    callback_data="edit_profile"
                ),
                InlineKeyboardButton(
                    i18n.get_text("profile.usage_stats", language),
                    callback_data="usage_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("profile.language", language),
                    callback_data="change_language"
                ),
                InlineKeyboardButton(
                    i18n.get_text("profile.notifications", language),
                    callback_data="notifications"
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
    def get_language_selection(language: str = "en") -> InlineKeyboardMarkup:
        """Get language selection keyboard."""
        keyboard = []
        
        for lang_code, lang_name in i18n.get_supported_languages().items():
            keyboard.append([
                InlineKeyboardButton(
                    lang_name,
                    callback_data=f"set_lang_{lang_code}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                i18n.get_text("common.back", language),
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_yes_no(language: str = "en") -> InlineKeyboardMarkup:
        """Get yes/no keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.yes", language),
                    callback_data="yes"
                ),
                InlineKeyboardButton(
                    i18n.get_text("common.no", language),
                    callback_data="no"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_cancel(language: str = "en") -> InlineKeyboardMarkup:
        """Get cancel keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.cancel", language),
                    callback_data="cancel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button(language: str = "en", callback_data: str = "main_menu") -> InlineKeyboardMarkup:
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
    
    @staticmethod
    def get_reply_keyboard(language: str = "en") -> ReplyKeyboardMarkup:
        """Get reply keyboard for text input."""
        keyboard = [
            [
                KeyboardButton(i18n.get_text("common.cancel", language))
            ]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
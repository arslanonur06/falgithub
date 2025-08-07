"""
Main keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for general bot menus.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class MainKeyboards:
    """Main keyboard layouts."""
    
    @staticmethod
    def get_main_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get main menu keyboard using existing locale keys."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("coffee_fortune", language),
                    callback_data="coffee_fortune"
                ),
                InlineKeyboardButton(
                    i18n.get_text("tarot_fortune", language),
                    callback_data="tarot_fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("dream_analysis", language),
                    callback_data="dream_analysis"
                ),
                InlineKeyboardButton(
                    i18n.get_text("astrology", language),
                    callback_data="astrology"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_button", language),
                    callback_data="referral"
                ),
                InlineKeyboardButton(
                    i18n.get_text("premium_menu", language),
                    callback_data="premium"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("language_button", language),
                    callback_data="change_language"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_language_selection_keyboard() -> InlineKeyboardMarkup:
        """Get language selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🇹🇷 Türkçe", callback_data="set_lang_tr"),
                InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
            ],
            [
                InlineKeyboardButton("🇪🇸 Español", callback_data="set_lang_es")
            ],
            [
                InlineKeyboardButton(i18n.get_text("language_system.back_to_menu", "en"), callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get back button keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_yes_no_keyboard(language: str = "en", yes_callback: str = "yes", no_callback: str = "no") -> InlineKeyboardMarkup:
        """Get yes/no keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.yes", language),
                    callback_data=yes_callback
                ),
                InlineKeyboardButton(
                    i18n.get_text("common.no", language),
                    callback_data=no_callback
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_cancel_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get cancel button keyboard."""
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
    def get_profile_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get profile keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("profile.edit_info", language),
                    callback_data="edit_profile"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("profile.usage_stats", language),
                    callback_data="usage_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_help_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get help keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_referral_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get referral keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.copy_link", language),
                    callback_data="copy_referral_link"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.share_telegram", language),
                    callback_data="share_telegram"
                ),
                InlineKeyboardButton(
                    i18n.get_text("referral_system.share_whatsapp", language),
                    callback_data="share_whatsapp"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("referral_system.back_to_referral", language),
                    callback_data="referral"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_zodiac_signs_keyboard(callback_prefix: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get zodiac signs keyboard."""
        signs = [
            (i18n.get_text("aries", language), "aries"),
            (i18n.get_text("taurus", language), "taurus"),
            (i18n.get_text("gemini", language), "gemini"),
            (i18n.get_text("cancer", language), "cancer"),
            (i18n.get_text("leo", language), "leo"),
            (i18n.get_text("virgo", language), "virgo"),
            (i18n.get_text("libra", language), "libra"),
            (i18n.get_text("scorpio", language), "scorpio"),
            (i18n.get_text("sagittarius", language), "sagittarius"),
            (i18n.get_text("capricorn", language), "capricorn"),
            (i18n.get_text("aquarius", language), "aquarius"),
            (i18n.get_text("pisces", language), "pisces")
        ]
        
        keyboard = []
        for i in range(0, len(signs), 2):
            row = []
            row.append(InlineKeyboardButton(signs[i][0], callback_data=f"{callback_prefix}_{signs[i][1]}"))
            if i + 1 < len(signs):
                row.append(InlineKeyboardButton(signs[i + 1][0], callback_data=f"{callback_prefix}_{signs[i + 1][1]}"))
            keyboard.append(row)
        
        keyboard.append([
            InlineKeyboardButton(
                i18n.get_text("navigation.back", language),
                callback_data="astrology"
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_fortune_types_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get fortune types keyboard using existing keys."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("coffee_fortune", language),
                    callback_data="coffee_fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("tarot_fortune", language),
                    callback_data="tarot_fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("dream_analysis", language),
                    callback_data="dream_analysis"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_astrology_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get astrology menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("daily_horoscope", language),
                    callback_data="daily_horoscope"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("birth_chart", language),
                    callback_data="birth_chart"
                ),
                InlineKeyboardButton(
                    i18n.get_text("compatibility", language),
                    callback_data="compatibility"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("moon_calendar.title", language),
                    callback_data="moon_calendar"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("navigation.back", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
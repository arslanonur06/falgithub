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
        """Get main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.astrology", language),
                    callback_data="astrology"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.fortune", language),
                    callback_data="fortune"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.profile", language),
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.premium", language),
                    callback_data="premium"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("menu.referral", language),
                    callback_data="referral"
                ),
                InlineKeyboardButton(
                    i18n.get_text("menu.help", language),
                    callback_data="help"
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
                InlineKeyboardButton(i18n.get_text("common.back", "en"), callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get back button keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
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
                    i18n.get_text("common.back", language),
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
                    i18n.get_text("common.back", language),
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
                    i18n.get_text("referral.my_info", language),
                    callback_data="referral_info"
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
    def get_zodiac_signs_keyboard(callback_prefix: str, language: str = "en") -> InlineKeyboardMarkup:
        """Get zodiac signs keyboard."""
        signs = [
            ("♈ Aries", "aries"),
            ("♉ Taurus", "taurus"),
            ("♊ Gemini", "gemini"),
            ("♋ Cancer", "cancer"),
            ("♌ Leo", "leo"),
            ("♍ Virgo", "virgo"),
            ("♎ Libra", "libra"),
            ("♏ Scorpio", "scorpio"),
            ("♐ Sagittarius", "sagittarius"),
            ("♑ Capricorn", "capricorn"),
            ("♒ Aquarius", "aquarius"),
            ("♓ Pisces", "pisces")
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
                i18n.get_text("common.back", language),
                callback_data="astrology"
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_fortune_types_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get fortune types keyboard."""
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
    def get_astrology_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get astrology menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.daily_horoscope", language),
                    callback_data="daily_horoscope"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.birth_chart", language),
                    callback_data="birth_chart"
                ),
                InlineKeyboardButton(
                    i18n.get_text("astrology.compatibility", language),
                    callback_data="compatibility"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.moon_calendar", language),
                    callback_data="moon_calendar"
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
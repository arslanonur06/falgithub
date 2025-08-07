"""
Astrology keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for astrology features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class AstrologyKeyboards:
    """Astrology keyboard layouts."""
    
    @staticmethod
    def get_astrology_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get astrology main menu keyboard."""
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
    
    @staticmethod
    def get_horoscope_period_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get horoscope period selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "📅 Daily",
                    callback_data="horoscope_daily"
                ),
                InlineKeyboardButton(
                    "📅 Weekly",
                    callback_data="horoscope_weekly"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 Monthly",
                    callback_data="horoscope_monthly"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology"
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
    def get_compatibility_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get compatibility selection keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "💕 Love Compatibility",
                    callback_data="compatibility_love"
                )
            ],
            [
                InlineKeyboardButton(
                    "🤝 Friendship Compatibility",
                    callback_data="compatibility_friendship"
                )
            ],
            [
                InlineKeyboardButton(
                    "💼 Business Compatibility",
                    callback_data="compatibility_business"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_birth_chart_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get birth chart keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "🌟 Sun Sign Analysis",
                    callback_data="birth_chart_sun"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌙 Moon Sign Analysis",
                    callback_data="birth_chart_moon"
                )
            ],
            [
                InlineKeyboardButton(
                    "⭐ Rising Sign Analysis",
                    callback_data="birth_chart_rising"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔮 Full Birth Chart",
                    callback_data="birth_chart_full"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_moon_calendar_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get moon calendar keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "🌑 New Moon",
                    callback_data="moon_new"
                ),
                InlineKeyboardButton(
                    "🌕 Full Moon",
                    callback_data="moon_full"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌓 First Quarter",
                    callback_data="moon_first_quarter"
                ),
                InlineKeyboardButton(
                    "🌗 Last Quarter",
                    callback_data="moon_last_quarter"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 Current Moon Phase",
                    callback_data="moon_current"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_astrology_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get astrology back keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 

    # --- Compatibility helpers required by verification script ---
    @staticmethod
    def get_zodiac_selection(callback_prefix: str = "zodiac", language: str = "en") -> InlineKeyboardMarkup:
        return AstrologyKeyboards.get_zodiac_signs_keyboard(callback_prefix, language)

    @staticmethod
    def get_compatibility_menu(language: str = "en") -> InlineKeyboardMarkup:
        return AstrologyKeyboards.get_compatibility_keyboard(language)

    @staticmethod
    def get_premium_upgrade_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        # Minimal upgrade keyboard directing to premium menu
        from src.keyboards.payment import PaymentKeyboards
        return PaymentKeyboards.get_premium_menu_keyboard(language)

    @staticmethod
    def get_back_button(language: str = "en") -> InlineKeyboardMarkup:
        return AstrologyKeyboards.get_astrology_back_keyboard(language)
"""
Astrology keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n

class AstrologyKeyboards:
    """Astrology keyboard layouts."""
    
    @staticmethod
    def get_astrology_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get main astrology menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.daily_horoscope", language),
                    callback_data="daily_horoscope"
                ),
                InlineKeyboardButton(
                    i18n.get_text("astrology.birth_chart", language),
                    callback_data="birth_chart"
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
                ),
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
    def get_zodiac_selection(language: str = "en", callback_prefix: str = "zodiac") -> InlineKeyboardMarkup:
        """Get zodiac sign selection keyboard."""
        zodiac_signs = [
            ("aries", "♈ Koç"),
            ("taurus", "♉ Boğa"),
            ("gemini", "♊ İkizler"),
            ("cancer", "♋ Yengeç"),
            ("leo", "♌ Aslan"),
            ("virgo", "♍ Başak"),
            ("libra", "♎ Terazi"),
            ("scorpio", "♏ Akrep"),
            ("sagittarius", "♐ Yay"),
            ("capricorn", "♑ Oğlak"),
            ("aquarius", "♒ Kova"),
            ("pisces", "♓ Balık")
        ]
        
        keyboard = []
        row = []
        
        for i, (sign, display_name) in enumerate(zodiac_signs):
            row.append(InlineKeyboardButton(
                display_name,
                callback_data=f"{callback_prefix}_{i}"
            ))
            
            if len(row) == 3:  # 3 buttons per row
                keyboard.append(row)
                row = []
        
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Add back button
        keyboard.append([
            InlineKeyboardButton(
                i18n.get_text("common.back", language),
                callback_data="astrology_menu"
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_compatibility_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get compatibility menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("astrology.select_first_sign", language),
                    callback_data="compat_first"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="astrology_menu"
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
                    callback_data="astrology_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_button(language: str = "en", callback_data: str = "astrology_menu") -> InlineKeyboardMarkup:
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
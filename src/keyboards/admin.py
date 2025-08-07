"""
Admin keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for admin panel features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class AdminKeyboards:
    """Admin keyboard layouts."""
    
    @staticmethod
    def get_admin_menu_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        """Get localized admin main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.stats", language),
                    callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.users", language),
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.premium", language),
                    callback_data="admin_premium"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.logs", language),
                    callback_data="admin_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.settings", language),
                    callback_data="admin_settings"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.pdf", language),
                    callback_data="admin_download_pdf"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin_panel.buttons.main_menu", language),
                    callback_data="main_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_to_admin_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        """Back to admin main keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin_panel_back", language),
                    callback_data="back_to_admin"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    # Keep other admin keyboards; they can be localized later as needed
    @staticmethod
    def get_admin_users_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        return AdminKeyboards.get_back_to_admin_keyboard(language)

    @staticmethod
    def get_admin_premium_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        return AdminKeyboards.get_back_to_admin_keyboard(language)

    @staticmethod
    def get_admin_settings_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        return AdminKeyboards.get_back_to_admin_keyboard(language)

    @staticmethod
    def get_admin_logs_keyboard(language: str = "tr") -> InlineKeyboardMarkup:
        return AdminKeyboards.get_back_to_admin_keyboard(language) 
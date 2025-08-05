"""
Admin keyboard layouts for the Fal Gram Bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n

class AdminKeyboards:
    """Admin keyboard layouts."""
    
    @staticmethod
    def get_admin_main_menu(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin main menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.stats", language),
                    callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.users", language),
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.premium", language),
                    callback_data="admin_premium"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.logs", language),
                    callback_data="admin_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.settings", language),
                    callback_data="admin_settings"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.download_pdf", language),
                    callback_data="admin_download_pdf"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_users_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin users keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.view_all_users", language),
                    callback_data="admin_view_all_users"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.search_user", language),
                    callback_data="admin_search_user"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.download_users_pdf", language),
                    callback_data="admin_download_users_pdf"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="back_to_admin"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_premium_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin premium management keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.premium_users", language),
                    callback_data="admin_premium_users"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.premium_stats", language),
                    callback_data="admin_premium_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.gift_subscription", language),
                    callback_data="admin_gift_subscription"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.cancel_subscription", language),
                    callback_data="admin_cancel_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.premium_pdf", language),
                    callback_data="admin_premium_pdf"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="back_to_admin"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_settings_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin settings keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.bot_settings", language),
                    callback_data="admin_bot_settings"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.prompt_management", language),
                    callback_data="admin_prompt_management"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("admin.database_management", language),
                    callback_data="admin_database_management"
                ),
                InlineKeyboardButton(
                    i18n.get_text("admin.system_health", language),
                    callback_data="admin_system_health"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="back_to_admin"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_to_admin_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get back to admin keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="back_to_admin"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
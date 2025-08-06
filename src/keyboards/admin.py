"""
Admin keyboard layouts for the Fal Gram Bot.
Contains keyboard layouts for admin panel features.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.utils.i18n import i18n


class AdminKeyboards:
    """Admin keyboard layouts."""
    
    @staticmethod
    def get_admin_menu_keyboard(language: str = "en") -> InlineKeyboardMarkup:
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
    def get_admin_stats_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin stats keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 User Statistics",
                    callback_data="admin_stats_users"
                ),
                InlineKeyboardButton(
                    "📈 Usage Statistics",
                    callback_data="admin_stats_usage"
                )
            ],
            [
                InlineKeyboardButton(
                    "💰 Revenue Statistics",
                    callback_data="admin_stats_revenue"
                ),
                InlineKeyboardButton(
                    "🎯 Referral Statistics",
                    callback_data="admin_stats_referrals"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
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
                    "👥 All Users",
                    callback_data="admin_users_all"
                ),
                InlineKeyboardButton(
                    "💎 Premium Users",
                    callback_data="admin_users_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    "🆕 New Users (Today)",
                    callback_data="admin_users_new"
                ),
                InlineKeyboardButton(
                    "📊 Active Users",
                    callback_data="admin_users_active"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔍 Search User",
                    callback_data="admin_users_search"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_premium_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin premium keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 Subscription Stats",
                    callback_data="admin_premium_stats"
                ),
                InlineKeyboardButton(
                    "💰 Revenue Stats",
                    callback_data="admin_premium_revenue"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎁 Gift Subscription",
                    callback_data="admin_premium_gift"
                ),
                InlineKeyboardButton(
                    "❌ Cancel Subscription",
                    callback_data="admin_premium_cancel"
                )
            ],
            [
                InlineKeyboardButton(
                    "📈 Plan Analytics",
                    callback_data="admin_premium_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_logs_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin logs keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "📝 Recent Logs",
                    callback_data="admin_logs_recent"
                ),
                InlineKeyboardButton(
                    "❌ Error Logs",
                    callback_data="admin_logs_errors"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔍 Search Logs",
                    callback_data="admin_logs_search"
                ),
                InlineKeyboardButton(
                    "📊 Log Statistics",
                    callback_data="admin_logs_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    "🧹 Clear Logs",
                    callback_data="admin_logs_clear"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
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
                    "⚙️ Bot Settings",
                    callback_data="admin_settings_bot"
                ),
                InlineKeyboardButton(
                    "🔧 System Settings",
                    callback_data="admin_settings_system"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌐 Language Settings",
                    callback_data="admin_settings_language"
                ),
                InlineKeyboardButton(
                    "💰 Payment Settings",
                    callback_data="admin_settings_payment"
                )
            ],
            [
                InlineKeyboardButton(
                    "🤖 AI Settings",
                    callback_data="admin_settings_ai"
                ),
                InlineKeyboardButton(
                    "📊 Rate Limits",
                    callback_data="admin_settings_ratelimit"
                )
            ],
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_back_keyboard(language: str = "en") -> InlineKeyboardMarkup:
        """Get admin back keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    i18n.get_text("common.back", language),
                    callback_data="admin_menu"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 
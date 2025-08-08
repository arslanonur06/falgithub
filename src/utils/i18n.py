"""
Internationalization (i18n) utility for the Fal Gram Bot.
Handles multi-language support with JSON locale files.
"""

import json
import os
from typing import Dict, Any
from config.settings import settings


class I18n:
    """Internationalization handler."""
    
    def __init__(self):
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all translation files."""
        locales_dir = settings.LOCALES_DIR
        
        if not os.path.exists(locales_dir):
            print(f"⚠️  Warning: Locales directory '{locales_dir}' not found")
            return
        
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                lang = filename.replace('.json', '')
                filepath = os.path.join(locales_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    print(f"✅ Loaded translations for {lang}")
                except Exception as e:
                    print(f"❌ Error loading {lang} translations: {e}")
    
    def get_text(self, key: str, lang: str = None) -> str:
        """
        Get translated text for a key.
        
        Args:
            key: Translation key (can be nested like "menu.main_title")
            lang: Language code (defaults to settings.DEFAULT_LANGUAGE)
        
        Returns:
            Translated text or the key itself if not found
        """
        if not lang:
            lang = settings.DEFAULT_LANGUAGE
        
        # Handle nested keys (e.g., "menu.main_title")
        keys = key.split('.')
        translation = self.translations.get(lang, {})
        
        # Navigate through nested dictionary
        for k in keys:
            if isinstance(translation, dict) and k in translation:
                translation = translation[k]
            else:
                translation = None
                break
        
        # Fallback to default language if translation not found
        if not translation and lang != settings.DEFAULT_LANGUAGE:
            translation = self.translations.get(settings.DEFAULT_LANGUAGE, {})
            for k in keys:
                if isinstance(translation, dict) and k in translation:
                    translation = translation[k]
                else:
                    translation = None
                    break
        
        # Fallback to key itself if no translation found
        if not translation:
            translation = key
        
        # Ensure translation is a string for text API
        if not isinstance(translation, str):
            translation = str(translation) if translation is not None else key
        
        return translation

    def get_raw(self, key: str, lang: str = None):
        """Get raw translation value (can be dict/list/string) without coercion."""
        if not lang:
            lang = settings.DEFAULT_LANGUAGE
        keys = key.split('.')
        translation = self.translations.get(lang, {})
        for k in keys:
            if isinstance(translation, dict) and k in translation:
                translation = translation[k]
            else:
                translation = None
                break
        if translation is None and lang != settings.DEFAULT_LANGUAGE:
            translation = self.translations.get(settings.DEFAULT_LANGUAGE, {})
            for k in keys:
                if isinstance(translation, dict) and k in translation:
                    translation = translation[k]
                else:
                    translation = None
                    break
        return translation
    
    def get_available_languages(self) -> list:
        """Get list of available language codes."""
        return list(self.translations.keys())
    
    def format_text(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Get translated text and format it with provided arguments.
        
        Args:
            key: Translation key
            lang: Language code
            **kwargs: Format arguments
        
        Returns:
            Formatted translated text
        """
        text = self.get_text(key, lang)
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the text as is
            return text


# Global i18n instance
i18n = I18n() 
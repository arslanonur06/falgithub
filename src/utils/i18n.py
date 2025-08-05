"""
Internationalization utilities for the Fal Gram Bot.
"""

import json
import os
from typing import Dict, Any, Optional
from config.settings import settings

class I18n:
    """Internationalization handler."""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language: str = settings.DEFAULT_LANGUAGE
        self.load_translations()
    
    def load_translations(self) -> None:
        """Load all translation files."""
        locales_dir = settings.LOCALES_DIR
        
        for lang in settings.SUPPORTED_LANGUAGES:
            file_path = os.path.join(locales_dir, f"{lang}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                print(f"⚠️  Translation file not found: {file_path}")
                self.translations[lang] = {}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing translation file {file_path}: {e}")
                self.translations[lang] = {}
    
    def set_language(self, language: str) -> None:
        """Set the current language."""
        if language in settings.SUPPORTED_LANGUAGES:
            self.current_language = language
        else:
            self.current_language = settings.DEFAULT_LANGUAGE
    
    def get_text(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Get translated text for a key."""
        lang = language or self.current_language
        
        # Get translation
        translation = self.translations.get(lang, {}).get(key)
        
        # Fallback to default language if translation not found
        if not translation and lang != settings.DEFAULT_LANGUAGE:
            translation = self.translations.get(settings.DEFAULT_LANGUAGE, {}).get(key)
        
        # Fallback to key itself if no translation found
        if not translation:
            translation = key
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                # If formatting fails, return the translation as is
                pass
        
        return translation
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code."""
        language_names = {
            "en": "English",
            "tr": "Türkçe", 
            "es": "Español"
        }
        return language_names.get(language_code, language_code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages with their display names."""
        return {
            lang: self.get_language_name(lang)
            for lang in settings.SUPPORTED_LANGUAGES
        }
    
    def validate_translations(self) -> Dict[str, list]:
        """Validate that all translation files have the same keys."""
        all_keys = set()
        missing_keys = {}
        
        # Collect all keys from all languages
        for lang, translations in self.translations.items():
            all_keys.update(translations.keys())
        
        # Check for missing keys in each language
        for lang in settings.SUPPORTED_LANGUAGES:
            lang_keys = set(self.translations.get(lang, {}).keys())
            missing = all_keys - lang_keys
            if missing:
                missing_keys[lang] = list(missing)
        
        return missing_keys

# Global i18n instance
i18n = I18n()
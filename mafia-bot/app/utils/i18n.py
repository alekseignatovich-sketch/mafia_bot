"""Internationalization module for Mafia Bot."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import LOCALES_DIR, settings


class I18n:
    """Internationalization manager."""
    
    _instance = None
    _translations: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations()
        return cls._instance
    
    def _load_translations(self) -> None:
        """Load all translation files."""
        for lang_file in LOCALES_DIR.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self._translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translation {lang_code}: {e}")
    
    def get(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """Get translated string by key.
        
        Args:
            key: Dot-separated key (e.g., "menu.city")
            lang: Language code (defaults to settings.DEFAULT_LANGUAGE)
            **kwargs: Format arguments
            
        Returns:
            Translated string
        """
        lang = lang or settings.DEFAULT_LANGUAGE
        
        # Fallback to default language if translation not found
        if lang not in self._translations:
            lang = settings.DEFAULT_LANGUAGE
        
        # Navigate through nested keys
        keys = key.split(".")
        value = self._translations.get(lang, {})
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Return key if translation not found
                return key
        
        # Format if string
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return str(value)
    
    def get_role_name(self, role_key: str, lang: Optional[str] = None) -> str:
        """Get role name translation."""
        return self.get(f"roles.{role_key}.name", lang)
    
    def get_role_description(self, role_key: str, lang: Optional[str] = None) -> str:
        """Get role description translation."""
        return self.get(f"roles.{role_key}.description", lang)
    
    def get_role_team(self, role_key: str, lang: Optional[str] = None) -> str:
        """Get role team info translation."""
        return self.get(f"roles.{role_key}.team", lang)
    
    def get_event_text(self, event_type: str, lang: Optional[str] = None, **kwargs) -> str:
        """Get event text translation."""
        return self.get(f"events.{event_type}", lang, **kwargs)
    
    def get_achievement_name(self, achievement_key: str, lang: Optional[str] = None) -> str:
        """Get achievement name translation."""
        return self.get(f"achievements.{achievement_key}.name", lang)
    
    def get_achievement_description(self, achievement_key: str, lang: Optional[str] = None) -> str:
        """Get achievement description translation."""
        return self.get(f"achievements.{achievement_key}.description", lang)
    
    def get_game_status(self, status: str, lang: Optional[str] = None) -> str:
        """Get game status translation."""
        return self.get(f"game.status.{status}", lang)
    
    def is_supported_language(self, lang: str) -> bool:
        """Check if language is supported."""
        return lang in settings.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages with their native names."""
        language_names = {
            "ru": "🇷🇺 Русский",
            "en": "🇬🇧 English",
            "be": "🇧🇾 Беларуская",
            "de": "🇩🇪 Deutsch",
            "es": "🇪🇸 Español",
        }
        return {
            lang: language_names.get(lang, lang)
            for lang in settings.SUPPORTED_LANGUAGES
        }


# Global i18n instance
i18n = I18n()


def _(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """Shortcut for i18n.get()."""
    return i18n.get(key, lang, **kwargs)

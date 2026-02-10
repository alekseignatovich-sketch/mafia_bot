"""Main menu keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.i18n import i18n


def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("menu.city", lang),
            callback_data="menu:city"
        ),
        InlineKeyboardButton(
            text=i18n.get("menu.profile", lang),
            callback_data="menu:profile"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("menu.journal", lang),
            callback_data="menu:journal"
        ),
        InlineKeyboardButton(
            text=i18n.get("menu.settings", lang),
            callback_data="menu:settings"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("menu.language", lang),
            callback_data="menu:language"
        ),
        InlineKeyboardButton(
            text=i18n.get("menu.help", lang),
            callback_data="menu:help"
        )
    )
    
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    languages = i18n.get_supported_languages()
    
    # Create rows of 2 buttons each
    lang_items = list(languages.items())
    for i in range(0, len(lang_items), 2):
        row = []
        for lang_code, lang_name in lang_items[i:i+2]:
            row.append(
                InlineKeyboardButton(
                    text=lang_name,
                    callback_data=f"lang:{lang_code}"
                )
            )
        builder.row(*row)
    
    return builder.as_markup()


def get_cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_confirm_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get confirm/cancel keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.yes", lang),
            callback_data="action:confirm"
        ),
        InlineKeyboardButton(
            text=i18n.get("general.no", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get back keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="action:back"
        )
    )
    
    return builder.as_markup()


def get_registration_keyboard(name: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get registration keyboard with Telegram name option."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("registration.use_telegram_name", lang, name=name),
            callback_data="reg:use_telegram_name"
        )
    )
    
    return builder.as_markup()

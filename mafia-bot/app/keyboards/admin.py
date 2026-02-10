"""Admin panel keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.event import EventType
from app.utils.i18n import i18n


def get_admin_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get admin panel keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("admin.new_city", lang),
            callback_data="admin:new_city"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("admin.start_event", lang),
            callback_data="admin:start_event"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("admin.stats", lang),
            callback_data="admin:stats"
        ),
        InlineKeyboardButton(
            text=i18n.get("admin.broadcast", lang),
            callback_data="admin:broadcast"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="menu:main"
        )
    )
    
    return builder.as_markup()


def get_event_selection_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get event type selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    events = [
        (EventType.INQUISITOR, "👁️ Инквизитор"),
        (EventType.MAYOR_ELECTION, "🗳️ Выборы мэра"),
        (EventType.PLAGUE, "☣️ Чума"),
        (EventType.FULL_MOON, "🌕 Полнолуние"),
        (EventType.CURFEW, "🚫 Комендантский час"),
        (EventType.DOUBLE_TROUBLE, "⚡ Двойной удар"),
        (EventType.REVELATION, "📢 Откровение"),
    ]
    
    for event_type, display_name in events:
        builder.row(
            InlineKeyboardButton(
                text=display_name,
                callback_data=f"admin:event:{event_type.value}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="menu:admin"
        )
    )
    
    return builder.as_markup()

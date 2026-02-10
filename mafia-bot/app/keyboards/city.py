"""City-related keyboards."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.city import City
from app.utils.i18n import i18n


def get_city_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get city menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("city.create_new", lang),
            callback_data="city:create"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("city.join", lang),
            callback_data="city:join"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("city.list", lang),
            callback_data="city:list"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="menu:main"
        )
    )
    
    return builder.as_markup()


def get_city_list_keyboard(cities: List[City], lang: str = "ru") -> InlineKeyboardMarkup:
    """Get city list keyboard."""
    builder = InlineKeyboardBuilder()
    
    for city in cities:
        builder.row(
            InlineKeyboardButton(
                text=f"{city.name} ({city.player_count}/{city.max_players})",
                callback_data=f"city:view:{city.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="menu:city"
        )
    )
    
    return builder.as_markup()


def get_city_actions_keyboard(city: City, is_member: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get city actions keyboard."""
    builder = InlineKeyboardBuilder()
    
    if is_member:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get("city.leave", lang),
                callback_data=f"city:leave:{city.id}"
            )
        )
        
        # Show start game button if enough players and not in game
        if city.can_start and (not city.games or city.games[-1].status.value == "ended"):
            builder.row(
                InlineKeyboardButton(
                    text="🎮 Начать игру",
                    callback_data=f"game:start:{city.id}"
                )
            )
    else:
        if not city.is_full:
            builder.row(
                InlineKeyboardButton(
                    text=i18n.get("city.join", lang),
                    callback_data=f"city:join:{city.id}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="city:list"
        )
    )
    
    return builder.as_markup()


def get_city_join_confirmation_keyboard(city_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get city join confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.confirm", lang),
            callback_data=f"city:join:confirm:{city_id}"
        ),
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data=f"city:view:{city_id}"
        )
    )
    
    return builder.as_markup()

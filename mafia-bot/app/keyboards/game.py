"""Game-related keyboards."""

from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.role import PlayerRole
from app.models.role import Role
from app.utils.i18n import i18n


def get_game_menu_keyboard(game_status: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get game menu keyboard based on game status."""
    builder = InlineKeyboardBuilder()
    
    if game_status == "night":
        builder.row(
            InlineKeyboardButton(
                text="🌑 Ночные действия",
                callback_data="game:night_actions"
            )
        )
    elif game_status in ["day", "voting"]:
        builder.row(
            InlineKeyboardButton(
                text="🗳️ Голосовать",
                callback_data="game:vote"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="📜 Журнал",
            callback_data="game:journal"
        ),
        InlineKeyboardButton(
            text="👥 Игроки",
            callback_data="game:players"
        )
    )
    
    return builder.as_markup()


def get_target_selection_keyboard(
    targets: List[PlayerRole],
    action: str,
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Get target selection keyboard for night actions."""
    builder = InlineKeyboardBuilder()
    
    for target in targets:
        display_name = target.player.display_name
        builder.row(
            InlineKeyboardButton(
                text=f"👤 {display_name}",
                callback_data=f"action:{action}:{target.player_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_vote_keyboard(
    candidates: List[PlayerRole],
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Get voting keyboard."""
    builder = InlineKeyboardBuilder()
    
    for candidate in candidates:
        display_name = candidate.player.display_name
        builder.row(
            InlineKeyboardButton(
                text=f"👤 {display_name}",
                callback_data=f"vote:{candidate.player_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_action_keyboard(role_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get action keyboard based on role."""
    builder = InlineKeyboardBuilder()
    
    action_buttons = {
        "mafia": ("actions.kill", "action:kill"),
        "don": ("actions.kill", "action:kill"),
        "doctor": ("actions.heal", "action:heal"),
        "sheriff": ("actions.investigate", "action:investigate"),
        "maniac": ("actions.kill", "action:maniac_kill"),
        "cupid": ("actions.matchmake", "action:matchmake"),
        "prostitute": ("actions.block", "action:block"),
        "bodyguard": ("actions.protect", "action:protect"),
    }
    
    if role_key in action_buttons:
        text_key, callback = action_buttons[role_key]
        builder.row(
            InlineKeyboardButton(
                text=i18n.get(text_key, lang),
                callback_data=callback
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_night_action_confirmation_keyboard(
    action: str,
    target_id: int,
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Get night action confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.confirm", lang),
            callback_data=f"action:{action}:confirm:{target_id}"
        ),
        InlineKeyboardButton(
            text=i18n.get("general.cancel", lang),
            callback_data="action:cancel"
        )
    )
    
    return builder.as_markup()


def get_skip_action_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Get skip action keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⏭️ Пропустить",
            callback_data="action:skip"
        )
    )
    
    return builder.as_markup()

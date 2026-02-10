"""Keyboards for Mafia Bot."""

from app.keyboards.main import (
    get_main_menu_keyboard,
    get_language_keyboard,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_back_keyboard,
)
from app.keyboards.city import (
    get_city_menu_keyboard,
    get_city_list_keyboard,
    get_city_actions_keyboard,
)
from app.keyboards.game import (
    get_game_menu_keyboard,
    get_target_selection_keyboard,
    get_vote_keyboard,
    get_action_keyboard,
)
from app.keyboards.admin import get_admin_keyboard
from app.keyboards.event import get_event_selection_keyboard  # ← добавлено

__all__ = [
    "get_main_menu_keyboard",
    "get_language_keyboard",
    "get_cancel_keyboard",
    "get_confirm_keyboard",
    "get_back_keyboard",
    "get_city_menu_keyboard",
    "get_city_list_keyboard",
    "get_city_actions_keyboard",
    "get_game_menu_keyboard",
    "get_target_selection_keyboard",
    "get_vote_keyboard",
    "get_action_keyboard",
    "get_admin_keyboard",
    "get_event_selection_keyboard",  # ← добавлено
]

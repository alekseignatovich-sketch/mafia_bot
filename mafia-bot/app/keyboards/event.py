from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_event_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Мафия", callback_data="event_mafia")],
            [InlineKeyboardButton(text="🎲 Другая игра", callback_data="event_other")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )

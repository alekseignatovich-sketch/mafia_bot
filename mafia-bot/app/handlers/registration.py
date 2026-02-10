"""Registration handlers."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_language_keyboard, get_main_menu_keyboard, get_registration_keyboard
from app.models.player import Player
from app.utils.i18n import i18n

router = Router()


class RegistrationStates(StatesGroup):
    """Registration FSM states."""
    
    choosing_language = State()
    entering_name = State()
    confirming_name = State()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Handle /start command."""
    # Check if user is already registered
    result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if player:
        # User is already registered
        await message.answer(
            i18n.get("registration.welcome_back", lang, name=player.first_name),
            reply_markup=get_main_menu_keyboard(lang),
        )
        return
    
    # New user - show language selection
    await state.set_state(RegistrationStates.choosing_language)
    await message.answer(
        i18n.get("general.choose_language"),
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"), RegistrationStates.choosing_language)
async def process_language_selection(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Process language selection."""
    lang_code = callback.data.split(":")[1]
    await state.update_data(language=lang_code)
    
    # Update user's language preference if they exist
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if player:
        player.language = lang_code
        await callback.message.edit_text(
            i18n.get("general.language_changed", lang_code)
        )
        await callback.message.answer(
            i18n.get("registration.welcome_back", lang_code, name=player.first_name),
            reply_markup=get_main_menu_keyboard(lang_code),
        )
        await state.clear()
        return
    
    # New user - proceed to name entry
    await state.set_state(RegistrationStates.entering_name)
    await callback.message.edit_text(
        i18n.get("registration.enter_name", lang_code),
        reply_markup=get_registration_keyboard(callback.from_user.first_name, lang_code),
    )


@router.callback_query(F.data == "reg:use_telegram_name", RegistrationStates.entering_name)
async def process_telegram_name(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Process using Telegram name."""
    data = await state.get_data()
    lang = data.get("language", "ru")
    
    # Create new player
    player = Player(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        language=lang,
    )
    
    session.add(player)
    await session.commit()
    
    await state.clear()
    await callback.message.edit_text(
        i18n.get("registration.registration_complete", lang, name=player.first_name)
    )
    await callback.message.answer(
        i18n.get("menu.main_title", lang),
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.message(RegistrationStates.entering_name)
async def process_custom_name(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Process custom name entry."""
    data = await state.get_data()
    lang = data.get("language", "ru")
    
    custom_name = message.text.strip()
    
    if len(custom_name) < 2 or len(custom_name) > 32:
        await message.answer(
            i18n.get("registration.invalid_name", lang, default="Имя должно быть от 2 до 32 символов")
        )
        return
    
    # Create new player with custom name
    player = Player(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=custom_name,
        last_name=message.from_user.last_name,
        language=lang,
    )
    
    session.add(player)
    await session.commit()
    
    await state.clear()
    await message.answer(
        i18n.get("registration.registration_complete", lang, name=player.first_name),
        reply_markup=get_main_menu_keyboard(lang),
    )

"""City handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import (
    get_back_keyboard,
    get_city_actions_keyboard,
    get_city_list_keyboard,
    get_city_menu_keyboard,
    get_main_menu_keyboard,
)
from app.models.city import City
from app.models.player import Player
from app.utils.i18n import i18n

router = Router()


class CityStates(StatesGroup):
    """City FSM states."""
    
    entering_name = State()
    entering_description = State()
    entering_id = State()


@router.message(Command("city"))
async def cmd_city(
    message: Message,
    session: AsyncSession,
    lang: str,
) -> None:
    """Handle /city command."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await message.answer(i18n.get("errors.not_registered", lang))
        return
    
    await message.answer(
        i18n.get("city.title", player.language),
        reply_markup=get_city_menu_keyboard(player.language),
    )


@router.callback_query(F.data == "menu:city")
async def show_city_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show city menu."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("city.title", player.language),
        reply_markup=get_city_menu_keyboard(player.language),
    )


@router.callback_query(F.data == "city:list")
async def list_cities(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """List available cities."""
    result = await session.execute(
        select(City).where(City.is_active == True).order_by(City.created_at.desc())
    )
    cities = result.scalars().all()
    
    if not cities:
        await callback.message.edit_text(
            i18n.get("city.no_cities", lang),
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    await callback.message.edit_text(
        i18n.get("city.list", lang),
        reply_markup=get_city_list_keyboard(cities, lang),
    )


@router.callback_query(F.data.startswith("city:view:"))
async def view_city(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """View city details."""
    city_id = int(callback.data.split(":")[2])
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await callback.answer(i18n.get("city.invalid_id", lang))
        return
    
    # Check if user is a member
    player_result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = player_result.scalar_one_or_none()
    
    is_member = player in city.players if player else False
    
    city_text = format_city_info(city, lang)
    
    await callback.message.edit_text(
        city_text,
        reply_markup=get_city_actions_keyboard(city, is_member, lang),
    )


def format_city_info(city: City, lang: str) -> str:
    """Format city information text."""
    from app.models.game import GameStatus
    
    # Get current game status
    game_status = i18n.get("game.status.waiting", lang)
    if city.games:
        latest_game = city.games[-1]
        game_status = i18n.get(f"game.status.{latest_game.status.value}", lang)
    
    info_text = f"""
🏙️ <b>{city.name}</b>

{city.description or ""}

{i18n.get("city.players", lang, current=city.player_count, max=city.max_players)}
{i18n.get("city.status", lang, status=game_status)}
{i18n.get("city.creator", lang, name=city.creator.display_name if city.creator else "Unknown")}
{i18n.get("city.created", lang, date=city.created_at.strftime("%d.%m.%Y"))}
"""
    return info_text


@router.callback_query(F.data == "city:create")
async def start_city_creation(
    callback: CallbackQuery,
    state: FSMContext,
    lang: str,
) -> None:
    """Start city creation process."""
    await state.set_state(CityStates.entering_name)
    await callback.message.edit_text(
        i18n.get("city.enter_name", lang),
        reply_markup=get_back_keyboard(lang),
    )


@router.message(CityStates.entering_name)
async def process_city_name(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process city name."""
    city_name = message.text.strip()
    
    if len(city_name) < 3 or len(city_name) > 64:
        await message.answer(
            "Название города должно быть от 3 до 64 символов.",
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    await state.update_data(city_name=city_name)
    await state.set_state(CityStates.entering_description)
    await message.answer(
        i18n.get("city.enter_description", lang),
        reply_markup=get_back_keyboard(lang),
    )


@router.message(CityStates.entering_description)
async def process_city_description(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process city description and create city."""
    data = await state.get_data()
    city_name = data.get("city_name")
    description = message.text.strip()
    
    # Skip if user sends "skip" or similar
    if description.lower() in ["skip", "пропустить", "-", "none"]:
        description = None
    
    # Get player
    result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await message.answer(i18n.get("errors.not_registered", lang))
        await state.clear()
        return
    
    # Create city
    city = City(
        name=city_name,
        description=description,
        creator_id=player.id,
    )
    
    session.add(city)
    await session.flush()  # Get city ID
    
    # Add creator to city
    city.players.append(player)
    
    await session.commit()
    
    await state.clear()
    await message.answer(
        i18n.get("city.created_success", lang, name=city.name, id=city.id),
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.callback_query(F.data == "city:join")
async def start_city_join(
    callback: CallbackQuery,
    state: FSMContext,
    lang: str,
) -> None:
    """Start city join process."""
    await state.set_state(CityStates.entering_id)
    await callback.message.edit_text(
        i18n.get("city.enter_id", lang),
        reply_markup=get_back_keyboard(lang),
    )


@router.message(CityStates.entering_id)
async def process_city_join(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process city ID and join."""
    try:
        city_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            i18n.get("city.invalid_id", lang),
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await message.answer(
            i18n.get("city.invalid_id", lang),
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    # Get player
    player_result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = player_result.scalar_one_or_none()
    
    if not player:
        await message.answer(i18n.get("errors.not_registered", lang))
        await state.clear()
        return
    
    # Check if already member
    if player in city.players:
        await message.answer(
            i18n.get("city.already_member", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )
        await state.clear()
        return
    
    # Check if city is full
    if city.is_full:
        await message.answer(
            i18n.get("city.full", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )
        await state.clear()
        return
    
    # Add player to city
    city.players.append(player)
    await session.commit()
    
    await state.clear()
    await message.answer(
        i18n.get("city.joined", lang, name=city.name),
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.callback_query(F.data.startswith("city:join:"))
async def join_city_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Join city from callback."""
    city_id = int(callback.data.split(":")[2])
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await callback.answer(i18n.get("city.invalid_id", lang))
        return
    
    # Get player
    player_result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = player_result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    # Check if already member
    if player in city.players:
        await callback.answer(i18n.get("city.already_member", lang))
        return
    
    # Check if city is full
    if city.is_full:
        await callback.answer(i18n.get("city.full", lang))
        return
    
    # Add player to city
    city.players.append(player)
    await session.commit()
    
    await callback.message.edit_text(
        i18n.get("city.joined", lang, name=city.name),
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.callback_query(F.data.startswith("city:leave:"))
async def leave_city(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Leave city."""
    city_id = int(callback.data.split(":")[2])
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await callback.answer(i18n.get("city.invalid_id", lang))
        return
    
    # Get player
    player_result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = player_result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    # Check if member
    if player not in city.players:
        await callback.answer(i18n.get("city.not_member", lang))
        return
    
    # Remove player from city
    city.players.remove(player)
    await session.commit()
    
    await callback.message.edit_text(
        i18n.get("city.left", lang, name=city.name),
        reply_markup=get_main_menu_keyboard(lang),
    )

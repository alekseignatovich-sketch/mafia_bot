"""Admin handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import (
    get_admin_keyboard,
    get_back_keyboard,
    get_event_selection_keyboard,
    get_main_menu_keyboard,
)
from app.models.city import City
from app.models.event import Event, EventType
from app.models.game import Game, GameStatus
from app.models.player import Player
from app.utils.i18n import i18n
from app.config import settings

router = Router()


class AdminStates(StatesGroup):
    """Admin FSM states."""
    
    entering_city_name = State()
    entering_broadcast = State()
    selecting_city_for_event = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(
    message: Message,
    session: AsyncSession,
    lang: str,
) -> None:
    """Handle /admin command."""
    if not is_admin(message.from_user.id):
        await message.answer(i18n.get("errors.no_permission", lang))
        return
    
    await message.answer(
        i18n.get("admin.title", lang),
        reply_markup=get_admin_keyboard(lang),
    )


@router.callback_query(F.data == "menu:admin")
async def show_admin_menu(
    callback: CallbackQuery,
    lang: str,
) -> None:
    """Show admin menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("admin.title", lang),
        reply_markup=get_admin_keyboard(lang),
    )


@router.callback_query(F.data == "admin:new_city")
async def start_new_city(
    callback: CallbackQuery,
    state: FSMContext,
    lang: str,
) -> None:
    """Start creating new city as admin."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    await state.set_state(AdminStates.entering_city_name)
    await callback.message.edit_text(
        i18n.get("admin.enter_city_name", lang),
        reply_markup=get_back_keyboard(lang),
    )


@router.message(AdminStates.entering_city_name)
async def process_new_city_name(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process new city name and create city."""
    if not is_admin(message.from_user.id):
        await message.answer(i18n.get("errors.no_permission", lang))
        await state.clear()
        return
    
    city_name = message.text.strip()
    
    if len(city_name) < 3 or len(city_name) > 64:
        await message.answer(
            "Название города должно быть от 3 до 64 символов.",
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    # Get admin player
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
        creator_id=player.id,
    )
    
    session.add(city)
    await session.flush()
    
    # Add creator to city
    city.players.append(player)
    await session.commit()
    
    await state.clear()
    await message.answer(
        i18n.get("admin.city_created", lang, id=city.id),
        reply_markup=get_admin_keyboard(lang),
    )


@router.callback_query(F.data == "admin:stats")
async def show_stats(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show bot statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    # Get statistics
    players_count = await session.scalar(select(func.count(Player.id)))
    cities_count = await session.scalar(select(func.count(City.id)))
    active_games_count = await session.scalar(
        select(func.count(Game.id)).where(Game.status != GameStatus.ENDED)
    )
    
    stats_text = f"""
{i18n.get("admin.stats_title", lang)}

{i18n.get("admin.total_players", lang, count=players_count)}
{i18n.get("admin.total_cities", lang, count=cities_count)}
{i18n.get("admin.active_games", lang, count=active_games_count)}
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_keyboard(lang),
    )


@router.callback_query(F.data == "admin:start_event")
async def start_event_selection(
    callback: CallbackQuery,
    lang: str,
) -> None:
    """Show event selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("admin.select_event", lang),
        reply_markup=get_event_selection_keyboard(lang),
    )


@router.callback_query(F.data.startswith("admin:event:"))
async def process_event_selection(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process event selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    event_type_str = callback.data.split(":")[2]
    event_type = EventType(event_type_str)
    
    # Store selected event type
    await state.update_data(event_type=event_type_str)
    await state.set_state(AdminStates.selecting_city_for_event)
    
    # Show list of active cities
    result = await session.execute(
        select(City).where(City.is_active == True)
    )
    cities = result.scalars().all()
    
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    for city in cities:
        builder.row(
            InlineKeyboardButton(
                text=f"{city.name} ({city.player_count} игроков)",
                callback_data=f"admin:event:city:{city.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("general.back", lang),
            callback_data="menu:admin"
        )
    )
    
    await callback.message.edit_text(
        "Выберите город для события:",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data.startswith("admin:event:city:"))
async def start_event_in_city(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Start event in selected city."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    city_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    event_type_str = data.get("event_type")
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await callback.answer(i18n.get("city.invalid_id", lang))
        await state.clear()
        return
    
    # Get active game in city
    active_game = None
    for game in city.games:
        if game.status not in [GameStatus.ENDED, GameStatus.WAITING]:
            active_game = game
            break
    
    if not active_game:
        await callback.message.edit_text(
            "В городе нет активной игры.",
            reply_markup=get_admin_keyboard(lang),
        )
        await state.clear()
        return
    
    # Create event
    event = Event(
        game_id=active_game.id,
        event_type=EventType(event_type_str),
        day_number=active_game.day_number,
    )
    
    session.add(event)
    await session.commit()
    
    await state.clear()
    await callback.message.edit_text(
        i18n.get("admin.event_started", lang, event=event_type_str, city=city.name),
        reply_markup=get_admin_keyboard(lang),
    )


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
    lang: str,
) -> None:
    """Start broadcast message."""
    if not is_admin(callback.from_user.id):
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    await state.set_state(AdminStates.entering_broadcast)
    await callback.message.edit_text(
        i18n.get("admin.enter_message", lang),
        reply_markup=get_back_keyboard(lang),
    )


@router.message(AdminStates.entering_broadcast)
async def process_broadcast(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    lang: str,
) -> None:
    """Process and send broadcast message."""
    if not is_admin(message.from_user.id):
        await message.answer(i18n.get("errors.no_permission", lang))
        await state.clear()
        return
    
    broadcast_text = message.text
    
    # Get all players
    result = await session.execute(select(Player))
    players = result.scalars().all()
    
    sent_count = 0
    for player in players:
        try:
            await message.bot.send_message(
                player.telegram_id,
                f"📢 <b>Сообщение от администрации:</b>\n\n{broadcast_text}",
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send broadcast to {player.id}: {e}")
    
    await state.clear()
    await message.answer(
        i18n.get("admin.broadcast_sent", lang, count=sent_count),
        reply_markup=get_admin_keyboard(lang),
    )

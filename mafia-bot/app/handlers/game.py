"""Game handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_back_keyboard, get_main_menu_keyboard
from app.models.city import City
from app.models.game import Game, GameStatus
from app.models.player import Player
from app.models.role import PlayerRole, Role
from app.utils.i18n import i18n

router = Router()


@router.callback_query(F.data.startswith("game:start:"))
async def start_game(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Start a new game in the city."""
    city_id = int(callback.data.split(":")[2])
    
    result = await session.execute(
        select(City).where(City.id == city_id)
    )
    city = result.scalar_one_or_none()
    
    if not city:
        await callback.answer(i18n.get("city.invalid_id", lang))
        return
    
    # Check if there's already an active game
    if city.games:
        latest_game = city.games[-1]
        if latest_game.status not in [GameStatus.ENDED, GameStatus.WAITING]:
            await callback.answer(i18n.get("city.game_in_progress", lang))
            return
    
    # Check minimum players
    if not city.can_start:
        await callback.answer(
            i18n.get("city.min_players", lang, current=city.player_count, min=city.min_players)
        )
        return
    
    # Create new game
    game = Game(
        city_id=city.id,
        status=GameStatus.STARTING,
    )
    session.add(game)
    await session.flush()
    
    # Add all city players to game
    for player in city.players:
        game.players.append(player)
    
    # Assign roles
    await assign_roles(session, game)
    
    # Start the game
    game.status = GameStatus.NIGHT
    game.day_number = 1
    await session.commit()
    
    # Notify all players
    await notify_game_start(callback.bot, game, lang)
    
    await callback.message.edit_text(
        i18n.get("game.started", lang),
        reply_markup=get_main_menu_keyboard(lang),
    )


async def assign_roles(session: AsyncSession, game: Game) -> None:
    """Assign roles to players."""
    import random
    
    # Get available roles
    result = await session.execute(
        select(Role).where(Role.is_special == False)
    )
    all_roles = result.scalars().all()
    
    # Separate roles by type
    mafia_roles = [r for r in all_roles if r.role_type.value == "mafia"]
    civilian_roles = [r for r in all_roles if r.role_type.value == "civilian"]
    
    players = list(game.players)
    random.shuffle(players)
    
    player_count = len(players)
    
    # Calculate role distribution
    mafia_count = max(1, player_count // 3)
    
    assigned_roles = []
    
    # Assign mafia roles
    for i in range(mafia_count):
        if mafia_roles and i < len(players):
            role = random.choice(mafia_roles)
            player_role = PlayerRole(
                player_id=players[i].id,
                game_id=game.id,
                role_id=role.id,
            )
            assigned_roles.append((players[i], role))
            session.add(player_role)
    
    # Assign civilian roles
    for i in range(mafia_count, player_count):
        if civilian_roles and i < len(players):
            role = random.choice(civilian_roles)
            player_role = PlayerRole(
                player_id=players[i].id,
                game_id=game.id,
                role_id=role.id,
            )
            assigned_roles.append((players[i], role))
            session.add(player_role)
    
    await session.flush()


async def notify_game_start(bot, game: Game, lang: str) -> None:
    """Notify all players about game start and their roles."""
    for player_role in game.roles:
        player = player_role.player
        role = player_role.role
        
        role_text = i18n.get(
            "game.your_role",
            player.language,
            role=i18n.get_role_name(role.name_key, player.language),
            description=i18n.get_role_description(role.name_key, player.language),
            team_info=i18n.get_role_team(role.name_key, player.language),
        )
        
        try:
            await bot.send_message(
                player.telegram_id,
                role_text,
            )
        except Exception as e:
            print(f"Failed to notify player {player.id}: {e}")


@router.callback_query(F.data == "menu:journal")
async def show_journal(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show game journal."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    # Get player's active game
    active_game = None
    for game in player.games:
        if game.status not in [GameStatus.ENDED, GameStatus.WAITING]:
            active_game = game
            break
    
    if not active_game:
        await callback.message.edit_text(
            "У вас нет активных игр.",
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    # Build journal text
    journal_text = f"📜 <b>Журнал ночей - День {active_game.day_number}</b>\n\n"
    
    # Add actions from this game
    for action in active_game.actions:
        if action.result:
            journal_text += f"🌑 Ночь {action.day_number}: {action.result}\n"
    
    if not active_game.actions:
        journal_text += "Пока нет записей в журнале."
    
    await callback.message.edit_text(
        journal_text,
        reply_markup=get_back_keyboard(lang),
    )


@router.callback_query(F.data == "game:players")
async def show_players(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show list of players in current game."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    # Get player's active game
    active_game = None
    for game in player.games:
        if game.status not in [GameStatus.ENDED, GameStatus.WAITING]:
            active_game = game
            break
    
    if not active_game:
        await callback.message.edit_text(
            "У вас нет активных игр.",
            reply_markup=get_back_keyboard(lang),
        )
        return
    
    # Build players list
    players_text = f"👥 <b>Игроки - {active_game.city.name}</b>\n\n"
    
    for player_role in active_game.roles:
        status = "🩸" if player_role.is_alive else "💀"
        players_text += f"{status} {player_role.player.display_name}\n"
    
    await callback.message.edit_text(
        players_text,
        reply_markup=get_back_keyboard(lang),
    )

"""Profile handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_back_keyboard, get_main_menu_keyboard
from app.models.player import Player
from app.utils.i18n import i18n

router = Router()


@router.message(Command("profile"))
async def cmd_profile(
    message: Message,
    session: AsyncSession,
    lang: str,
) -> None:
    """Handle /profile command."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await message.answer(i18n.get("errors.not_registered", lang))
        return
    
    profile_text = format_profile_text(player, lang)
    
    await message.answer(
        profile_text,
        reply_markup=get_back_keyboard(player.language),
    )


@router.callback_query(F.data == "menu:profile")
async def show_profile(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show player profile."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    profile_text = format_profile_text(player, player.language)
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_back_keyboard(player.language),
    )


def format_profile_text(player: Player, lang: str) -> str:
    """Format player profile text."""
    # Get reputation title based on reputation score
    reputation_titles = {
        (-100, -10): "Преступник 🦹",
        (-9, -1): "Подозреваемый 🕵️",
        (0, 9): "Новичок 🌱",
        (10, 24): "Уважаемый житель 🏘️",
        (25, 49): "Защитник города 🛡️",
        (50, 99): "Герой города 🦸",
        (100, 1000): "Легенда города 👑",
    }
    
    title = "Новичок 🌱"
    for (min_rep, max_rep), rep_title in reputation_titles.items():
        if min_rep <= player.reputation <= max_rep:
            title = rep_title
            break
    
    # Calculate required XP for next level
    from app.config import settings
    required_xp = player.level * settings.XP_LEVEL_MULTIPLIER
    
    profile_text = f"""
👤 <b>{i18n.get("profile.title", lang)}</b>

<b>{i18n.get("profile.name", lang, name=player.display_name)}</b>

{i18n.get("profile.status_alive" if player.is_active else "profile.status_dead", lang)}

{i18n.get("profile.level", lang, level=player.level, xp=player.experience, required_xp=required_xp)}

{i18n.get("profile.reputation", lang, reputation=player.reputation)} {title}

{i18n.get("profile.stats", lang, 
    games=player.games_played, 
    wins=player.games_won, 
    losses=player.games_lost, 
    winrate=f"{player.win_rate:.1f}")}

{i18n.get("profile.achievements", lang, count=len(player.achievements))}
"""
    
    return profile_text

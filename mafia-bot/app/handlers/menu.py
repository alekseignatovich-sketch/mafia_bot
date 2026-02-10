"""Main menu handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import (
    get_admin_keyboard,
    get_city_menu_keyboard,
    get_language_keyboard,
    get_main_menu_keyboard,
)
from app.models.player import Player
from app.utils.i18n import i18n
from app.config import settings

router = Router()


@router.message(Command("menu"))
async def cmd_menu(
    message: Message,
    session: AsyncSession,
    lang: str,
) -> None:
    """Handle /menu command."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == message.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await message.answer(i18n.get("errors.not_registered", lang))
        return
    
    await message.answer(
        i18n.get("menu.main_title", player.language),
        reply_markup=get_main_menu_keyboard(player.language),
    )


@router.callback_query(F.data == "menu:main")
async def show_main_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show main menu."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("menu.main_title", player.language),
        reply_markup=get_main_menu_keyboard(player.language),
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


@router.callback_query(F.data == "menu:language")
async def show_language_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show language selection menu."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("general.choose_language"),
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def change_language(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Change user language."""
    new_lang = callback.data.split(":")[1]
    
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    player.language = new_lang
    await session.commit()
    
    await callback.message.edit_text(
        i18n.get("general.language_changed", new_lang)
    )
    await callback.message.answer(
        i18n.get("menu.main_title", new_lang),
        reply_markup=get_main_menu_keyboard(new_lang),
    )


@router.callback_query(F.data == "menu:help")
async def show_help(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show help message."""
    result = await session.execute(
        select(Player).where(Player.telegram_id == callback.from_user.id)
    )
    player = result.scalar_one_or_none()
    
    if not player:
        await callback.answer(i18n.get("errors.not_registered", lang))
        return
    
    help_text = f"""
🎭 <b>{i18n.get("general.bot_name", player.language)}</b>

<b>Основные команды:</b>
/start - Начать игру / зарегистрироваться
/menu - Главное меню
/profile - Ваш профиль
/city - Управление городами
/language - Сменить язык

<b>Как играть:</b>
1. Создайте или присоединитесь к городу
2. Дождитесь начала игры
3. Получите роль в личном сообщении
4. Действуйте ночью (если есть способность)
5. Голосуйте днём за подозреваемых

<b>Роли:</b>
• Мирный житель - ищите мафию
• Мафия - устраняйте горожан
• Доктор - лечите игроков
• Шериф - проверяйте подозреваемых
• И другие...

<b>Игра асинхронная:</b>
У вас есть время до дедлайна для действий.
"""
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_menu_keyboard(player.language),
    )


@router.callback_query(F.data == "menu:admin")
async def show_admin_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
) -> None:
    """Show admin menu."""
    # Check if user is admin
    if callback.from_user.id not in settings.ADMIN_IDS:
        await callback.answer(i18n.get("errors.no_permission", lang))
        return
    
    await callback.message.edit_text(
        i18n.get("admin.title", lang),
        reply_markup=get_admin_keyboard(lang),
    )

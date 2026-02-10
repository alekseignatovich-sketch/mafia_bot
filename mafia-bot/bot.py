# /app/bot.py

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.handlers import get_routers
from app.middlewares import DatabaseMiddleware, I18nMiddleware, ThrottlingMiddleware
from app.services.game_scheduler import GameScheduler
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def on_startup(bot: Bot) -> None:
    """Initialize bot on startup."""
    # Устанавливаем команды меню
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать игру / Start game"),
        BotCommand(command="menu", description="Главное меню / Main menu"),
        BotCommand(command="profile", description="Профиль / Profile"),
        BotCommand(command="city", description="Управление городами / City management"),
        BotCommand(command="language", description="Сменить язык / Change language"),
        BotCommand(command="help", description="Помощь / Help"),
    ])

    # Инициализация БД и данных
    from app.models.database import init_db
    from app.services.role_manager import RoleManager
    from app.services.achievement_manager import AchievementManager

    await init_db()
    role_manager = RoleManager()
    await role_manager.initialize_default_roles()
    achievement_manager = AchievementManager()
    await achievement_manager.initialize_default_achievements()

    logger.info("Database initialized")
    logger.info("Default roles initialized")
    logger.info("Achievements initialized")


async def on_shutdown(bot: Bot) -> None:
    """Cleanup on shutdown."""
    logger.info("Bot shutting down...")


async def main() -> None:
    """Main entry point."""
    # Создаём бота с правильными настройками
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Регистрируем обработчики
    for router in get_routers():
        dp.include_router(router)

    # Регистрируем middleware
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Регистрируем события жизненного цикла
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запускаем планировщик задач
    game_scheduler = GameScheduler(scheduler)
    game_scheduler.start()
    logger.info("Scheduler started")

    logger.info("Bot starting up...")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Error running bot: {e}")
        sys.exit(1)

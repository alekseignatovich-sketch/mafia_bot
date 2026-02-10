# mafia-bot/bot.py

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импорты из вашего пакета
from app.config import settings
from app.handlers import get_routers
from app.middlewares import DatabaseMiddleware, I18nMiddleware, ThrottlingMiddleware
from app.services.game_scheduler import GameScheduler

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Инициализация при запуске бота."""
    # Устанавливаем команды меню
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать игру / Start game"),
        BotCommand(command="menu", description="Главное меню / Main menu"),
        BotCommand(command="profile", description="Профиль / Profile"),
        BotCommand(command="city", description="Управление городами / City management"),
        BotCommand(command="language", description="Сменить язык / Change language"),
        BotCommand(command="help", description="Помощь / Help"),
    ])

    # Инициализация базы данных
    from app.models.database import init_db, AsyncSessionLocal
    await init_db()

    # Инициализация ролей
    from app.services.role_manager import RoleManager
    async with AsyncSessionLocal() as session:
        role_manager = RoleManager(session)
        await role_manager.initialize_default_roles()

    logger.info("Database initialized")
    logger.info("Default roles initialized")


async def on_shutdown(bot: Bot) -> None:
    """Очистка при завершении работы."""
    logger.info("Bot shutting down...")


async def main() -> None:
    """Основная точка входа."""
    # Создаём бота с правильными настройками
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Подключаем все роутеры
    for router in get_routers():
        dp.include_router(router)

    # Middleware
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # События жизненного цикла
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Планировщик игровых событий
    game_scheduler = GameScheduler(scheduler)
    game_scheduler.start()
    logger.info("Scheduler started")

    logger.info("Bot starting up...")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

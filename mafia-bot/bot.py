"""Main bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import get_routers
from app.middlewares import DatabaseMiddleware, I18nMiddleware, ThrottlingMiddleware
from app.models.database import init_db
from app.services.role_manager import RoleManager
from app.services.scheduler import scheduler
from app.services.xp_manager import XPManager

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Actions to perform on bot startup."""
    logger.info("Bot starting up...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize roles and achievements
    from app.models.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        role_manager = RoleManager(session)
        await role_manager.initialize_default_roles()
        logger.info("Default roles initialized")
        
        xp_manager = XPManager(session)
        await xp_manager.initialize_achievements()
        logger.info("Achievements initialized")
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Set bot commands
    await bot.set_my_commands([
        ("start", "Начать игру / Start game"),
        ("menu", "Главное меню / Main menu"),
        ("profile", "Профиль / Profile"),
        ("city", "Управление городами / City management"),
        ("language", "Сменить язык / Change language"),
        ("help", "Помощь / Help"),
    ])
    
    logger.info("Bot startup complete!")


async def on_shutdown(bot: Bot) -> None:
    """Actions to perform on bot shutdown."""
    logger.info("Bot shutting down...")
    
    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Scheduler stopped")
    
    # Close bot session
    await bot.session.close()
    logger.info("Bot shutdown complete!")


async def main() -> None:
    """Main entry point."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(I18nMiddleware())
    
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    
    # Register routers
    routers = get_routers()
    for router in routers:
        dp.include_router(router)
    
    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    try:
        if settings.is_webhook_mode:
            # Use webhook mode
            from aiogram.webhook.aiohttp_server import (
                SimpleRequestHandler,
                setup_application,
            )
            from aiohttp import web
            
            app = web.Application()
            webhook_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
            )
            webhook_handler.register(app, path=settings.WEBHOOK_PATH)
            setup_application(app, dp, bot=bot)
            
            # Set webhook
            await bot.set_webhook(settings.webhook_url)
            
            # Run web server
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", 8080)
            await site.start()
            
            logger.info(f"Webhook server started on {settings.webhook_url}")
            
            # Keep running
            while True:
                await asyncio.sleep(3600)
        else:
            # Use polling mode
            await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

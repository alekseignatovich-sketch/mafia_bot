"""Internationalization middleware."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player


class I18nMiddleware(BaseMiddleware):
    """Middleware to detect and set user language."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Detect user language and pass it to handler."""
        # Get user from event
        user: User = data.get("event_from_user")
        session: AsyncSession = data.get("session")
        
        lang = "ru"  # Default language
        
        if user and session:
            # Try to get player language from database
            result = await session.execute(
                select(Player).where(Player.telegram_id == user.id)
            )
            player = result.scalar_one_or_none()
            
            if player:
                lang = player.language
            else:
                # Use Telegram language code if available
                lang = user.language_code or "ru"
                # Map Telegram language codes to our supported languages
                lang_map = {
                    "ru": "ru",
                    "en": "en",
                    "be": "be",
                    "de": "de",
                    "es": "es",
                }
                lang = lang_map.get(lang, "ru")
        
        data["lang"] = lang
        return await handler(event, data)

"""Throttling middleware to prevent spam."""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests."""
    
    def __init__(self, rate_limit: float = 0.5, ttl: int = 10):
        """Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum time between requests in seconds
            ttl: Cache TTL in seconds
        """
        self.rate_limit = rate_limit
        self.cache = TTLCache(maxsize=10000, ttl=ttl)
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Check if user is throttled."""
        if isinstance(event, Message):
            user_id = event.from_user.id
            current_time = time.time()
            
            if user_id in self.cache:
                last_time = self.cache[user_id]
                if current_time - last_time < self.rate_limit:
                    # User is throttled
                    return None
            
            self.cache[user_id] = current_time
        
        return await handler(event, data)

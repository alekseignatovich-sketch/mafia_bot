"""Middlewares for Mafia Bot."""

from app.middlewares.database import DatabaseMiddleware
from app.middlewares.i18n import I18nMiddleware
from app.middlewares.throttling import ThrottlingMiddleware

__all__ = [
    "DatabaseMiddleware",
    "I18nMiddleware",
    "ThrottlingMiddleware",
]

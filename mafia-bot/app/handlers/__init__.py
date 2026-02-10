"""Handlers for Mafia Bot."""

from aiogram import Router

from app.handlers import admin, city, game, menu, profile, registration


def get_routers() -> list[Router]:
    """Get all routers."""
    return [
        registration.router,
        menu.router,
        profile.router,
        city.router,
        game.router,
        admin.router,
    ]

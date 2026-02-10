# app/services/game_scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from app.models.database import AsyncSessionLocal
from app.models.game import Game
from app.models.role import PlayerRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class GameScheduler:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def end_all_nights(self):
        """Завершить все ночные фазы."""
        async with AsyncSessionLocal() as session:
            # Здесь логика завершения ночей
            logger.info("Проверка завершения ночных фаз...")

    async def end_all_voting(self):
        """Завершить все фазы голосования."""
        async with AsyncSessionLocal() as session:
            # Здесь логика завершения голосований
            logger.info("Проверка завершения голосований...")

    async def send_action_reminders(self):
        """Отправить напоминания о действиях."""
        logger.info("Отправка напоминаний...")

    def start(self):
        """Запустить задачи планировщика."""
        self.scheduler.add_job(
            self.end_all_nights,
            trigger=IntervalTrigger(seconds=30),
            id="end_all_nights"
        )
        self.scheduler.add_job(
            self.end_all_voting,
            trigger=IntervalTrigger(seconds=30),
            id="end_all_voting"
        )
        self.scheduler.add_job(
            self.send_action_reminders,
            trigger=IntervalTrigger(minutes=5),
            id="send_action_reminders"
        )
        self.scheduler.start()
        logger.info("Game scheduler started")

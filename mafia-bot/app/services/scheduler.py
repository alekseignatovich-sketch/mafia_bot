"""Task scheduler for game phases."""

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import AsyncSessionLocal
from app.models.game import Game, GameStatus
from app.services.game_engine import GameEngine


class GameScheduler:
    """Scheduler for game phase transitions."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self) -> None:
        """Start the scheduler."""
        # Schedule night end (day start)
        self.scheduler.add_job(
            self.end_all_nights,
            CronTrigger(hour=settings.DAY_START_HOUR, minute=0),
            id="end_nights",
            replace_existing=True,
        )
        
        # Schedule voting end
        self.scheduler.add_job(
            self.end_all_voting,
            CronTrigger(hour=23, minute=settings.VOTE_END_MINUTE),
            id="end_voting",
            replace_existing=True,
        )
        
        # Schedule action reminders
        self.scheduler.add_job(
            self.send_action_reminders,
            CronTrigger(hour=settings.NIGHT_START_HOUR + 6, minute=0),
            id="action_reminders",
            replace_existing=True,
        )
        
        self.scheduler.start()
        print("Scheduler started")
    
    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
    
    async def end_all_nights(self) -> None:
        """End night phase for all active games."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Game).where(Game.status == GameStatus.NIGHT)
            )
            games = result.scalars().all()
            
            engine = GameEngine(session)
            
            for game in games:
                try:
                    await engine.end_night(game)
                    print(f"Ended night for game {game.id}")
                except Exception as e:
                    print(f"Error ending night for game {game.id}: {e}")
    
    async def end_all_voting(self) -> None:
        """End voting phase for all active games."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Game).where(Game.status == GameStatus.VOTING)
            )
            games = result.scalars().all()
            
            engine = GameEngine(session)
            
            for game in games:
                try:
                    executed = await engine.process_votes(game)
                    
                    # Notify players about execution
                    if executed:
                        # Start new night
                        await engine.start_night(game)
                    else:
                        # No execution, start new night
                        await engine.start_night(game)
                    
                    print(f"Ended voting for game {game.id}")
                except Exception as e:
                    print(f"Error ending voting for game {game.id}: {e}")
    
    async def send_action_reminders(self) -> None:
        """Send reminders to players who haven't acted."""
        # This would require bot instance to send messages
        # Implementation depends on how bot is structured
        pass


# Global scheduler instance
scheduler = GameScheduler()

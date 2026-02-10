"""Event manager service for special game events."""

import random
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventType
from app.models.game import Game
from app.models.role import PlayerRole
from app.utils.i18n import i18n


class EventManager:
    """Manager for special game events."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def trigger_event(self, game: Game, event_type: EventType) -> Event:
        """Trigger a special event in the game."""
        event = Event(
            game_id=game.id,
            event_type=event_type,
            day_number=game.day_number,
        )
        
        self.session.add(event)
        await self.session.flush()
        
        # Apply event effects
        await self._apply_event_effects(game, event)
        
        await self.session.commit()
        return event
    
    async def _apply_event_effects(self, game: Game, event: Event) -> None:
        """Apply event-specific effects."""
        if event.event_type == EventType.INQUISITOR:
            # Sheriff can see all roles
            pass  # Handled in investigation logic
        
        elif event.event_type == EventType.MAYOR_ELECTION:
            # Start mayor election
            pass  # Handled in voting logic
        
        elif event.event_type == EventType.PLAGUE:
            # Random player loses ability
            alive_players = game.alive_players
            if alive_players:
                affected = random.choice(alive_players)
                event.affected_player_id = affected.player_id
                affected.ability_cooldown = 1
        
        elif event.event_type == EventType.FULL_MOON:
            # Maniac can kill 2 people
            pass  # Handled in action logic
        
        elif event.event_type == EventType.CURFEW:
            # No talking during day
            pass  # Handled in message handling
        
        elif event.event_type == EventType.DOUBLE_TROUBLE:
            # Mafia can kill 2 players
            pass  # Handled in action logic
        
        elif event.event_type == EventType.REVELATION:
            # Random role is revealed
            alive_players = game.alive_players
            if alive_players:
                revealed = random.choice(alive_players)
                event.affected_player_id = revealed.player_id
                revealed.is_revealed = True
    
    async def get_event_text(self, event: Event, lang: str) -> str:
        """Get localized event text."""
        event_key = event.event_type.value
        
        kwargs = {}
        if event.affected_player_id:
            result = await self.session.execute(
                select(PlayerRole).where(PlayerRole.player_id == event.affected_player_id)
            )
            player_role = result.scalar_one_or_none()
            if player_role:
                kwargs["player"] = player_role.player.display_name
                kwargs["role"] = i18n.get_role_name(player_role.role.name_key, lang)
        
        return i18n.get_event_text(event_key, lang, **kwargs)
    
    async def process_random_event(self, game: Game) -> Optional[Event]:
        """Process random event with 20% chance."""
        if random.random() > 0.8:  # 20% chance
            event_types = [
                EventType.INQUISITOR,
                EventType.MAYOR_ELECTION,
                EventType.PLAGUE,
                EventType.FULL_MOON,
                EventType.CURFEW,
                EventType.DOUBLE_TROUBLE,
                EventType.REVELATION,
            ]
            
            event_type = random.choice(event_types)
            return await self.trigger_event(game, event_type)
        
        return None
    
    async def end_event(self, event: Event) -> None:
        """End an active event."""
        event.complete()
        
        # Revert event effects if needed
        if event.event_type == EventType.PLAGUE and event.affected_player_id:
            result = await self.session.execute(
                select(PlayerRole).where(PlayerRole.player_id == event.affected_player_id)
            )
            player_role = result.scalar_one_or_none()
            if player_role:
                player_role.ability_cooldown = 0
        
        await self.session.commit()
